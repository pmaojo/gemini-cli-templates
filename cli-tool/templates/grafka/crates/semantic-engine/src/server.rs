use tonic::{Request, Response, Status};
use crate::topology::GraphTopology;
use crate::properties::PropertyStore;
use crate::persistence::GraphSnapshot;
use tokio::sync::RwLock as AsyncRwLock; // Alias for async RwLock
use std::sync::RwLock; // Standard library RwLock
use std::collections::HashMap;
use std::sync::Arc;
use std::sync::atomic::{AtomicU32, AtomicU16, Ordering};
use std::path::Path;

// Import the generated proto code
pub mod semantic_engine {
    tonic::include_proto!("semantic_engine");
}

use semantic_engine::semantic_engine_server::SemanticEngine;
use semantic_engine::{IngestRequest, IngestResponse, NodeRequest, NeighborResponse, Neighbor, SearchRequest, SearchResponse, ResolveRequest, ResolveResponse, EmptyRequest, TriplesResponse, Triple, DeleteResponse};

pub struct TenantGraph {
    pub tenant_id: String,
    pub topology: AsyncRwLock<GraphTopology>,
    pub properties: AsyncRwLock<PropertyStore>,

    // Node Dictionary (String <-> u32)
    pub dictionary: RwLock<HashMap<String, u32>>,
    pub reverse_dictionary: RwLock<HashMap<u32, String>>,

    // Predicate Dictionary (String <-> u16)
    pub predicate_dictionary: RwLock<HashMap<String, u16>>,
    pub reverse_predicate_dictionary: RwLock<HashMap<u16, String>>,

    // Atomic counters for lock-free ID generation
    pub next_node_id: AtomicU32,
    pub next_predicate_id: AtomicU16,
}

impl TenantGraph {
    pub fn new(tenant_id: &str) -> Self {
        Self {
            tenant_id: tenant_id.to_string(),
            topology: AsyncRwLock::new(GraphTopology::new()),
            properties: AsyncRwLock::new(PropertyStore::new()),
            dictionary: RwLock::new(HashMap::new()),
            reverse_dictionary: RwLock::new(HashMap::new()),
            predicate_dictionary: RwLock::new(HashMap::new()),
            reverse_predicate_dictionary: RwLock::new(HashMap::new()),
            next_node_id: AtomicU32::new(0),
            next_predicate_id: AtomicU16::new(0),
        }
    }

    // Helper to get or create a node ID
    fn get_or_create_node_id(&self, name: &str) -> (u32, bool) {
        // Optimistic read
        {
            let dict = self.dictionary.read().unwrap();
            if let Some(id) = dict.get(name) {
                return (*id, false);
            }
        } // Drop read lock

        // Acquire write lock
        let mut dict = self.dictionary.write().unwrap();
        // Check again
        if let Some(id) = dict.get(name) {
            return (*id, false);
        }

        let id = self.next_node_id.fetch_add(1, Ordering::Relaxed);

        // Insert into reverse dictionary
        {
            let mut rev_dict = self.reverse_dictionary.write().unwrap();
            rev_dict.insert(id, name.to_string());
        }

        dict.insert(name.to_string(), id);
        (id, true)
    }

    // Helper for predicates
    fn get_or_create_predicate_id(&self, name: &str) -> u16 {
        // Optimistic read
        {
            let dict = self.predicate_dictionary.read().unwrap();
            if let Some(id) = dict.get(name) {
                return *id;
            }
        } // Drop read lock

        // Acquire write lock
        let mut dict = self.predicate_dictionary.write().unwrap();
        // Check again
        if let Some(id) = dict.get(name) {
            return *id;
        }

        let id = self.next_predicate_id.fetch_add(1, Ordering::Relaxed);

        // Insert into reverse dictionary
        {
            let mut rev_dict = self.reverse_predicate_dictionary.write().unwrap();
            rev_dict.insert(id, name.to_string());
        }

        dict.insert(name.to_string(), id);
        id
    }

    pub async fn to_snapshot(&self) -> GraphSnapshot {
        let topology = self.topology.read().await;

        let nodes: Vec<(u32, String)> = {
            let rev_dict = self.reverse_dictionary.read().unwrap();
            rev_dict
                .iter()
                .map(|(k, v)| (*k, v.clone()))
                .collect()
        };

        let mut edges = Vec::new();
        for node_id in 0..topology.num_nodes() as u32 {
            for (neighbor_id, predicate_id) in topology.neighbors(node_id) {
                edges.push((node_id, neighbor_id, predicate_id));
            }
        }

        let predicates: Vec<(u16, String)> = {
            let rev_dict = self.reverse_predicate_dictionary.read().unwrap();
            rev_dict
                .iter()
                .map(|(k, v)| (*k, v.clone()))
                .collect()
        };

        GraphSnapshot {
            nodes,
            edges,
            predicates,
        }
    }

    pub async fn from_snapshot(tenant_id: &str, snapshot: GraphSnapshot) -> Self {
        let graph = TenantGraph::new(tenant_id);

        // Restore dictionaries
        {
            let mut dict = graph.dictionary.write().unwrap();
            let mut rev_dict = graph.reverse_dictionary.write().unwrap();
            let mut max_node_id = 0;
            for (id, name) in snapshot.nodes {
                dict.insert(name.clone(), id);
                rev_dict.insert(id, name);
                if id > max_node_id {
                    max_node_id = id;
                }
            }
            graph.next_node_id.store(max_node_id + 1, Ordering::Relaxed);
        }

        {
            let mut dict = graph.predicate_dictionary.write().unwrap();
            let mut rev_dict = graph.reverse_predicate_dictionary.write().unwrap();
            let mut max_pred_id = 0;
            for (id, name) in snapshot.predicates {
                dict.insert(name.clone(), id);
                rev_dict.insert(id, name);
                if id > max_pred_id {
                    max_pred_id = id;
                }
            }
            graph.next_predicate_id.store(max_pred_id + 1, Ordering::Relaxed);
        }

        // Restore topology
        let mut topo = graph.topology.write().await;

        // Ensure capacity - approximating based on next_node_id
        let next_node = graph.next_node_id.load(Ordering::Relaxed);
        if next_node > 0 {
            topo.ensure_capacity(next_node as usize);
        }

        for (s, o, p) in snapshot.edges {
            let max_curr = std::cmp::max(s, o);
            if max_curr as usize >= topo.num_nodes() {
                 topo.ensure_capacity((max_curr + 1) as usize);
            }
            topo.add_edge(s, o, p);
        }

        drop(topo);
        graph
    }
}

pub struct MySemanticEngine {
    // Map of Tenant ID -> Tenant Graph
    pub tenants: RwLock<HashMap<String, Arc<TenantGraph>>>,
    pub storage_path: String,
}

impl MySemanticEngine {
    pub fn new(storage_path: &str) -> Self {
        // Ensure storage directory exists
        if !Path::new(storage_path).exists() {
            std::fs::create_dir_all(storage_path).unwrap_or_else(|e| {
                println!("Warning: Could not create storage dir: {}", e);
            });
        }

        Self {
            tenants: RwLock::new(HashMap::new()),
            storage_path: storage_path.to_string(),
        }
    }

    // Helper to get a tenant graph (creating if not exists)
    async fn get_tenant_graph(&self, tenant_id: &str) -> Arc<TenantGraph> {
        // Default to "default" tenant if empty
        let tid = if tenant_id.is_empty() { "default" } else { tenant_id };

        // Optimistic read
        {
            let tenants = self.tenants.read().unwrap();
            if let Some(graph) = tenants.get(tid) {
                return graph.clone();
            }
        } // Drop read lock

        // Try load from disk - do NOT hold lock during IO
        let file_path = format!("{}/{}.bin", self.storage_path, tid);
        let graph = if Path::new(&file_path).exists() {
            println!("📥 Loading graph for tenant '{}' from {}", tid, file_path);
            match GraphSnapshot::load_from_file(&file_path) {
                Ok(snapshot) => Arc::new(TenantGraph::from_snapshot(tid, snapshot).await),
                Err(e) => {
                    println!("❌ Failed to load snapshot for {}: {}", tid, e);
                    Arc::new(TenantGraph::new(tid))
                }
            }
        } else {
            Arc::new(TenantGraph::new(tid))
        };

        // Write lock
        {
            let mut tenants = self.tenants.write().unwrap();
            // Check again (Double-checked locking)
            if let Some(existing_graph) = tenants.get(tid) {
                return existing_graph.clone();
            }
            tenants.insert(tid.to_string(), graph.clone());
        }

        graph
    }

    async fn save_tenant_graph(&self, tenant_id: &str) {
        let tid = if tenant_id.is_empty() { "default" } else { tenant_id };

        let graph_opt = {
            let tenants = self.tenants.read().unwrap();
            tenants.get(tid).cloned()
        };

        if let Some(graph) = graph_opt {
            let snapshot = graph.to_snapshot().await;
            let file_path = format!("{}/{}.bin", self.storage_path, tid);
            if let Err(e) = snapshot.save_to_file(&file_path) {
                println!("❌ Failed to save graph for {}: {}", tid, e);
            }
        }
    }
}

#[tonic::async_trait]
impl SemanticEngine for MySemanticEngine {
    async fn ingest_triples(
        &self,
        request: Request<IngestRequest>,
    ) -> Result<Response<IngestResponse>, Status> {
        let req = request.into_inner();
        let tenant_graph = self.get_tenant_graph(&req.tenant_id).await;

        let mut nodes_added = 0;
        let mut edges_added = 0;

        // We need a write lock for the duration of the batch to ensure consistency of the topology vector
        let mut topo = tenant_graph.topology.write().await;

        for triple in req.triples {
            // 1. Resolve Subject
            let s_id = tenant_graph.get_or_create_node_id(&triple.subject).0;
            let o_id = tenant_graph.get_or_create_node_id(&triple.object).0;
            let p_id = tenant_graph.get_or_create_predicate_id(&triple.predicate);

            // Ensure topology has space
            let max_id = std::cmp::max(s_id, o_id);
            if max_id as usize >= topo.num_nodes() {
                topo.ensure_capacity((max_id + 1) as usize);
                nodes_added += 1;
            }

            // 3. Add Edge
            topo.add_edge(s_id, o_id, p_id);
            edges_added += 1;
        }

        // Release lock before saving
        drop(topo);

        // Auto-save after ingest
        // TODO: Move to background task for performance
        let snapshot = tenant_graph.to_snapshot().await;
        let file_path = format!("{}/{}.bin", self.storage_path, tenant_graph.tenant_id);
        let _ = snapshot.save_to_file(&file_path);

        Ok(Response::new(IngestResponse {
            nodes_added,
            edges_added,
        }))
    }

    async fn get_neighbors(
        &self,
        request: Request<NodeRequest>,
    ) -> Result<Response<NeighborResponse>, Status> {
        let req = request.into_inner();
        let tenant_graph = self.get_tenant_graph(&req.tenant_id).await;

        let topo = tenant_graph.topology.read().await;

        let neighbors = topo.neighbors(req.node_id)
            .map(|(n, t)| {
                // Resolve Node ID to String Name
                let rev_dict = tenant_graph.reverse_dictionary.read().unwrap();
                let node_name = rev_dict.get(&n)
                    .cloned()
                    .unwrap_or_else(|| format!("Node_{}", n));

                // Resolve Predicate ID to String Name
                let rev_pred_dict = tenant_graph.reverse_predicate_dictionary.read().unwrap();
                let edge_name = rev_pred_dict.get(&t)
                    .cloned()
                    .unwrap_or_else(|| format!("Predicate_{}", t));

                Neighbor {
                    node_id: n,
                    edge_type: edge_name,
                }
            })
            .collect();

        Ok(Response::new(NeighborResponse { neighbors }))
    }

    async fn search(
        &self,
        _request: Request<SearchRequest>,
    ) -> Result<Response<SearchResponse>, Status> {
        // Placeholder for vector search
        Ok(Response::new(SearchResponse { results: vec![] }))
    }

    async fn resolve_id(
        &self,
        request: Request<ResolveRequest>,
    ) -> Result<Response<ResolveResponse>, Status> {
        let req = request.into_inner();
        let tenant_graph = self.get_tenant_graph(&req.tenant_id).await;

        // Optimistic read
        let id_opt = {
            let dict = tenant_graph.dictionary.read().unwrap();
            dict.get(&req.content).cloned()
        };

        if let Some(id) = id_opt {
            Ok(Response::new(ResolveResponse {
                node_id: id,
                found: true,
            }))
        } else {
            Ok(Response::new(ResolveResponse {
                node_id: 0,
                found: false,
            }))
        }
    }

    async fn get_all_triples(
        &self,
        request: Request<EmptyRequest>,
    ) -> Result<Response<TriplesResponse>, Status> {
        let req = request.into_inner();
        let tenant_graph = self.get_tenant_graph(&req.tenant_id).await;

        let topo = tenant_graph.topology.read().await;
        let mut triples = Vec::new();

        // Iterate through all nodes and their edges
        for node_id in 0..topo.num_nodes() as u32 {
            for (neighbor_id, predicate_id) in topo.neighbors(node_id) {
                // Resolve IDs to strings
                let subject = {
                    let rev_dict = tenant_graph.reverse_dictionary.read().unwrap();
                    rev_dict.get(&node_id)
                        .cloned()
                        .unwrap_or_else(|| format!("Node_{}", node_id))
                };

                let object = {
                    let rev_dict = tenant_graph.reverse_dictionary.read().unwrap();
                    rev_dict.get(&neighbor_id)
                        .cloned()
                        .unwrap_or_else(|| format!("Node_{}", neighbor_id))
                };

                let predicate = {
                    let rev_pred_dict = tenant_graph.reverse_predicate_dictionary.read().unwrap();
                    rev_pred_dict.get(&predicate_id)
                        .cloned()
                        .unwrap_or_else(|| format!("Predicate_{}", predicate_id))
                };

                triples.push(Triple {
                    subject,
                    predicate,
                    object,
                });
            }
        }

        Ok(Response::new(TriplesResponse { triples }))
    }

    async fn delete_tenant_data(
        &self,
        request: Request<EmptyRequest>,
    ) -> Result<Response<DeleteResponse>, Status> {
        let req = request.into_inner();
        let tenant_id = req.tenant_id;

        if tenant_id.is_empty() {
             return Ok(Response::new(DeleteResponse {
                success: false,
                message: "Tenant ID required".to_string(),
            }));
        }

        // 1. Remove from memory
        {
            let mut tenants = self.tenants.write().unwrap();
            tenants.remove(&tenant_id);
        }

        // 2. Remove from disk
        let file_path = format!("{}/{}.bin", self.storage_path, tenant_id);
        if Path::new(&file_path).exists() {
            match std::fs::remove_file(&file_path) {
                Ok(_) => Ok(Response::new(DeleteResponse {
                    success: true,
                    message: format!("Deleted data for tenant {}", tenant_id),
                })),
                Err(e) => Ok(Response::new(DeleteResponse {
                    success: false,
                    message: format!("Failed to delete file: {}", e),
                })),
            }
        } else {
             Ok(Response::new(DeleteResponse {
                success: true,
                message: "Tenant data not found (already clean)".to_string(),
            }))
        }
    }
}
