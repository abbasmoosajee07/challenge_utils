/* {header_text} */

use std::env;
use std::fs;
use std::io;

fn main() -> io::Result<()> {{

    // Get the first command-line argument, or default to "Lang06_input.txt"
    let args: Vec<String> = env::args().collect();
    let file_path = if args.len() > 1 {{
        &args[1]  // Use the provided file path
    }} else {{
        "{text_placeholder}"  // Default file
    }};

    let contents = fs::read_to_string(file_path)?;
    println!("Input Data:\\n{{}}", contents);
    println!("Hello World!\\n-From Rust");
    Ok(())
}}
