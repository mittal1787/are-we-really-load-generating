# Install
1. Install rustup toolchain from [https://rustup.rs/](https://rustup.rs/)

2. Build the binary
    ```bash
    cargo build --release
    ```
    The binary will be in `target/release/mock-server`

# Usage
```
Fast HTTP mock server

Usage: mock-server [OPTIONS] --port <PORT>

Options:
  -p, --port <PORT>    port to listen on
  -d, --delay <DELAY>  request processing delay in milliseconds [default: 0]
  -h, --help           Print help
  -V, --version        Print version
```

# Example
Running the server on port 8080 with a 500ms delay
```bash
mock-server --port 8080 --delay 500
```
The log will be written to `./log.txt` file