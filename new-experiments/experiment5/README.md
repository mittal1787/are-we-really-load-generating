# Experiment 5 (Two Servers)

**This test requires the usage of two server machines**

For this experiment, we run a distributed system of two servers and run the load generator tests against this distributed system.

## Prerequisites
Make sure `go` is installed in the server machines.

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

The file serverone.go is Server1. The file servertwo.go is Server2.


First server run
```
go run serverone.go <second-server-hostname> > timestamp.txt
```

Second server run
```
go run servertwo.go > timestamp.txt
```

## Throughput test

Run the load generator against the server by supplying the URL to the client machine. After running the two servers on their respective machines, run the workload generator against Server1 on the client machine. The timestamps will be printed out in the `timestamp.txt` file of each server machine. 

After running the workload generator on the client machine against Server1, run the command below on the machines running the servers to generate the histogram. Each bin should represent a second of time and the height of those bins should be (approximately) equal to the RPS provided by the workload generator.

```
python3 latencyHistogram.py timestamp.txt
```

### Hypothesis
For a distributed set of servers, the load generator will fail to generate the correct load across the server due to the first server holding back when waiting for the second server. In other words, wrk2 will violate the conditions for open-loop as the first server depending on the second server is going to slow down the requests for the client.

## Tail Latency test
Ground truth: use `tcpdump` to measure the tail latency on the client side as well as the first server. 

```
sudo tcpdump | grep <server-hostname>
```

With the server results, to measure the tail latencies, measure the difference between the timestamps of when the packet was sent and when the packet was recieved. `tcpdump` gets the packets at the network layer as opposed to the application layer, so the latency by `tcpdump` discards the client queueing delay. 

Moreover, to see some latency change across the second server, `tcpdump` across the first server can see the packets sent from the first server to the second server and compute the latency between the two server.

### Hypothesis

Many workload generators, particularly wrk2 family workload generators, will fail to record the accurate tail latency due to client side queueing delay. Moreover, due to variations among distributed systems, there will be more errors in recording the tail latency accurately.

### Important update
You can make modifications to main.go and add some line of code that will make some sort of impact on the tail latency. However, the tail latency from the workload generators should match nearly that of what tcpdump returns.

## Tests to run
For wrk2 family workload generators, run the tests for 100 RPS, 200 RPS, 250 RPS, 500 RPS, 1000 RPS, 2000 RPS, 2500 RPS, 5000 RPS, 10000 RPS, 20000 RPS, 25000 RPS, 50000 RPS, 100000 RPS. Run the thread combinations of 1 thread, 2 threads, 4 threads, 8 threads, 10 threads, 12 threads, 16 threads, and 24 threads. Try 10, 20, 25, 50, 100, 200, 500, 1000, and 10000 connections. 

Repeat similar experiments for other workload generators as well.

Two types of configurations for the server machines:
* Same cluster
* Different cluster

Two versions of this experiment:
* Client and server in same cluster
* Client and server in two different clusters

Also change the distribution type of the workload generators (i.e exp, zipf, fixed) to conduct the distribution type tests.