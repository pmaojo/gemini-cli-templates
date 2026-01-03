use clap::Parser;
use tokio::fs::File;
use tokio::io::AsyncReadExt;

/// A simple async file reader CLI tool.
#[derive(Parser, Debug)]
#[clap(author, version, about, long_about = None)]
struct Args {
    /// The path to the file to read.
    #[clap(value_parser)]
    path: String,
}

#[tokio::main] async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args = Args::parse();

    let mut file = match File::open(&args.path).await {
        Ok(file) => file,
        Err(e) => {
            eprintln!("Error opening file '{}': {}", args.path, e);
            return Err(e.into());
        }
    };

    let mut contents = String::new();
    if let Err(e) = file.read_to_string(&mut contents).await {
        eprintln!("Error reading file '{}': {}", args.path, e);
        return Err(e.into());
    }

    println!("File content:\n{}", contents);

    Ok(())
}