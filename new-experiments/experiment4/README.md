# Experiment 4 (DeathStarBench SocialNetwork)

For this experiment, we run SocialNetwork from DeathStarBench and run the load generator tests against DeathStarBench.

## Prerequisites
Make sure docker is installed before running the SocialNetwork application. Running `sh install.sh` will install docker and run the DeathStarBench SocialNetwork

### Run DeathStarBench SocialNetwork

Clone [DeathStarBench repository](https://github.com/delimitrou/DeathStarBench.git). Change to the DeathStarBench socialNetwork directory and run `docker compose` to install the docker containers. 

### Shell scripts
Unlike simple servers, we have to run a custom wrk2 lua script for providing the query parameters to the server. HotelReservation repo provided a lua script for wrk2 load generators to run. For the other load generators, the scripts have to be manually created.

## Throughput test
Jaeger tracing can be used to verify the throughput across the server. 


### Distribution Type test (Not applicable to Gil Tene's wrk2)
Ground truth: The throughput per second should match that of the expected arrivals (i.e exponential graph for exponential distribution, exponential distribution ). The overall load though should match RPS x duration.

### Hypothesis
For higher RPS, wrk2 family of workload generators will fail to generate the correct throughput across the server due to complexities of the socialNetwork application.

## Tail Latency test
Ground truth: use `tcpdump` to measure the tail latency on the client side. 

```
sudo tcpdump | grep <server-hostname>
```

With the server results, to measure the tail latencies, measure the difference between the timestamps of when the packet was sent and when the packet was recieved. `tcpdump` gets the packets at the network layer as opposed to the application layer, so the latency 

### Jaeger Tracing
To measure the tail latency on the server side, Jaeger tracing can be utilized. For each request, one must sum up the latencies of all the traces as long as they do not overlap.

### Distribution Type test (Not applicable to Gil Tene's wrk2)
Ground truth: Exponential distribution/Ramping should have smaller tail latencies than that of fixed. Zipf should have higher tail latencies than that of fixed. 

### Hypothesis
Many workload generators, particularly wrk2 family workload generators, will fail to record the accurate tail latency due to client side queueing delay. 

## Tests to run
For wrk2 family workload generators, run the tests for 100 RPS, 200 RPS, 250 RPS, 500 RPS, 1000 RPS, 2000 RPS, 2500 RPS, 5000 RPS, 10000 RPS, 20000 RPS, 25000 RPS, 50000 RPS, 100000 RPS, 200000 RPS, 500000 RPS, 1000000 RPS. Run the thread combinations of 1 thread, 2 threads, 4 threads, 8 threads, 10 threads, 12 threads, 16 threads, and 24 threads. Try 10, 20, 25, 50, 100, 200, 500, 1000, 10000, and 100000 connections.

Repeat similar experiments for other workload generators as well.

Two versions of this experiment:
* Client and server in same cluster
* Client and server in two different clusters

Also change the distribution type of the workload generators (i.e exp, zipf, fixed) to conduct the distribution type tests.