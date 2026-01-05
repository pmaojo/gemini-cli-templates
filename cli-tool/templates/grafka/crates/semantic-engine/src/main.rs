use tonic::transport::Server;
use semantic_engine::server::{MySemanticEngine, semantic_engine::semantic_engine_server::SemanticEngineServer};
use std::env;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let addr = "127.0.0.1:50051".parse()?;

    // Get storage path from env or default
    let storage_path = env::var("GRAPH_STORAGE_PATH").unwrap_or_else(|_| "data/graphs".to_string());

    let engine = MySemanticEngine::new(&storage_path);

    println!("Semantic Engine listening on {}", addr);
    println!("Storage Path: {}", storage_path);

    Server::builder()
        .add_service(SemanticEngineServer::new(engine))
        .serve(addr)
        .await?;

    Ok(())
}
