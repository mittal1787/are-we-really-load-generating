# Experiment 1 (Simple Server)

For this experiment, we run a simple server and run the load generator tests against this simple server.

## Prerequisites
Make sure `go` is installed in the server machine.

```
sudo apt-get install golang-go
```

Make sure `python` along with `numpy` and `matplotlib` are also installed for creating the histograms. 

```
sudo apt-get install python3-pip
pip install numpy
pip install matplotlib
```

Alternatively, you can run the shell script `install.sh` to install these prerequisites

```
sh install.sh
```

## Run the server

The file main.go is the server. 

```
go run main.go > timestamp.txt
```

## Even simpler approach
In your local machine, you can run 

```
python -m new-experiments.experiment1.experiment1.py -c <client-hostname> -s <server-hostname> -u <machine-username>
```

from the `are-we-really-load-generating` directory.

Note you need to have paramiko installed on your local machine. You can install via `pip install paramiko`.

## Throughput test

Run the load generator against the server by supplying the URL to the client machine. After running the server, run the workload generator against the server on the client machine. The timestamps will be printed out in the `timestamp.txt` file of the server machine. 

After running the workload generator on the client machine against the server machine, run the command below to generate a histogram. Each bin should represent a second of time and the height of those bins should be (approximately) equal to the RPS provided by the workload generator.

```
python3 latencyHistogram.py timestamp.txt
```

### Distribution Type test (Not applicable to Gil Tene's wrk2)
Ground truth: The throughput per second should match that of the expected arrivals (i.e exponential graph for exponential distribution, exponential distribution ). The overall load though should match RPS x duration.

### Hypothesis
For a simple server, the server will be able to achieve the desired throughput when the client (run on same cluster as server) runs an RPS smaller than 1000000 RPS, but after the simple server saturates, that is when the throughput experienced by the server will not reach the target. 

However, if client and server are run on different clusters (i.e Utah to Wisconsin), the server will not hit the target RPS for RPS at least 1000 due to propagation delay between the two clusters, and wrk2 will not fire the desired requests.

I also do hypothesize that if the number of threads and/or connections are too high, the RPS experienced by the server will be smaller as more open connections reduces throughput.

## Tail Latency test
Ground truth: use `tcpdump` to measure the tail latency on the client side. 

```
sudo tcpdump | grep <server-hostname>
```

With the server results, to measure the tail latencies, measure the difference between the timestamps of when the packet was sent and when the packet was recieved. `tcpdump` gets the packets at the network layer as opposed to the application layer, so the latency by `tcpdump` discards the client queueing delay. 


### Distribution Type test (Not applicable to Gil Tene's wrk2)
Ground truth: Exponential distribution/Ramping should have smaller tail latencies than that of fixed. Zipf should have higher tail latencies than that of fixed. 

### Hypothesis

Many workload generators, particularly wrk2 family workload generators, will fail to record the accurate tail latency due to client side queueing delay. 

### Important update
You can make modifications to main.go and add some line of code that will make some sort of impact on the tail latency. However, the tail latency from the workload generators should match nearly that of what tcpdump returns

## Tests to run
For wrk2 family workload generators, run the tests for 100 RPS, 200 RPS, 500 RPS, 1000 RPS, 2000 RPS, 5000 RPS, 10000 RPS, 20000 RPS, 50000 RPS, 100000 RPS. Run the thread combinations of 1 thread, 2 threads, 4 threads, 8 threads, 10 threads, 12 threads, 16 threads, and 24 threads. Try 10, 20, 25, 50, 100, 200, 500, 1000, and 10000 connections. 

Repeat similar experiments for other workload generators as well.

Two versions of this experiment:
* Client and server in same cluster
* Client and server in two different clusters

Also change the distribution type of the workload generators (i.e exp, zipf, fixed) to conduct the distribution type tests.