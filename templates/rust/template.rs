// Minimal Rust 2021 competitive-programming template.

use std::io::{self, Read};

fn solve(input: &str) -> String {
    let _ = input;
    String::new()
}

fn main() {
    let mut input = String::new();
    io::stdin().read_to_string(&mut input).unwrap();
    print!("{}", solve(&input));
}
