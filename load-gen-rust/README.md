# Simple Load Generator

A basic open-loop load generator that sends HTTP requests to the specified endpoint at a specified rate.

## Usage
```
Simple Load Generator

Usage: load-gen [OPTIONS] --endpoint <ENDPOINT>

Options:
  -e, --endpoint <ENDPOINT>            URL of the endpoint
  -r, --rps <RPS>                      number of request per second [default: 1]
  -t, --test-duration <TEST_DURATION>  Duration of testing in seconds [default: 60]
  -h, --help                           Print help
  -V, --version                        Print version
```

## Example
Run the following command to generate load on the server and save the log to a file.
```
./target/debug/load-gen --endpoint http://localhost:8080 --rps 10 --test-duration 60 > log.txt
```

Analyse the log file and graph the result.
```
python analysis.py log.txt
```