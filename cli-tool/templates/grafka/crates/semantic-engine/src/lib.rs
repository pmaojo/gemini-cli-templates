pub mod topology {
    use serde::{Deserialize, Serialize};

    /// A Dynamic Graph Topology represented as an Adjacency List.
    /// Efficient for both read and write operations during the active phase.
    /// Can be compacted into CSR for archival or read-only optimization.
    #[derive(Debug, Clone, Serialize, Deserialize)]
    pub struct GraphTopology {
        /// Adjacency list: NodeID -> Vec<(NeighborID, EdgeTypeID)>
        pub adj: Vec<Vec<(u32, u16)>>,
    }

    impl GraphTopology {
        pub fn new() -> Self {
            Self {
                adj: Vec::new(),
            }
        }

        pub fn num_nodes(&self) -> usize {
            self.adj.len()
        }

        pub fn num_edges(&self) -> usize {
            self.adj.iter().map(|neighbors| neighbors.len()).sum()
        }

        pub fn neighbors(&self, node_id: u32) -> impl Iterator<Item = (u32, u16)> + '_ {
            self.adj.get(node_id as usize)
                .into_iter()
                .flatten()
                .cloned()
        }

        pub fn add_node(&mut self) -> u32 {
            let id = self.adj.len() as u32;
            self.adj.push(Vec::new());
            id
        }

        pub fn add_edge(&mut self, src: u32, dst: u32, edge_type: u16) {
            if src as usize >= self.adj.len() || dst as usize >= self.adj.len() {
                return; // Safety check
            }
            self.adj[src as usize].push((dst, edge_type));
        }

        pub fn ensure_capacity(&mut self, size: usize) {
            if size > self.adj.len() {
                self.adj.resize(size, Vec::new());
            }
        }
    }
}

pub mod properties {
    use std::collections::HashMap;
    use serde::{Deserialize, Serialize};

    #[derive(Debug, Clone, Serialize, Deserialize)]
    pub enum Value {
        String(String),
        Int(i64),
        Float(f64),
        Bool(bool),
        DateTime(String), // ISO8601
    }

    /// Columnar storage for properties.
    #[derive(Debug, Clone, Serialize, Deserialize)]
    pub struct PropertyStore {
        /// Dense properties: PropertyID -> Vector of Values (indexed by NodeID)
        pub dense_columns: HashMap<u16, Vec<Option<Value>>>,

        /// Sparse properties: NodeID -> PropertyID -> Value
        pub sparse_props: HashMap<u32, HashMap<u16, Value>>,
    }

    impl PropertyStore {
        pub fn new() -> Self {
            Self {
                dense_columns: HashMap::new(),
                sparse_props: HashMap::new(),
            }
        }

        pub fn get_property(&self, node_id: u32, prop_id: u16) -> Option<&Value> {
            // Check dense first
            if let Some(col) = self.dense_columns.get(&prop_id) {
                if let Some(Some(val)) = col.get(node_id as usize) {
                    return Some(val);
                }
            }

            // Check sparse
            self.sparse_props.get(&node_id).and_then(|props| props.get(&prop_id))
        }
    }
}

pub mod server;
pub mod mcp;
pub mod persistence;
