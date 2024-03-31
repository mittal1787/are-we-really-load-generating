# decode jaegar jsons into a useful format
import json
import pandas as pd
import numpy as np

def jaegar_decode(fname):
    # we will add all the data to a pandas dataframe later
    f = open(fname)
    data = json.load(f)
    # data is a singleton dict
    data = data['data']
    
    # trace object
    # print(data[0].keys())
    # span object
    # print(data[0]['spans'][0].keys())
    # number of traces analyzed
    
    print(f'{fname}: {len(data)} traces analyzed.')
    
    # data is a list of dicts. Each dict represents a trace
    df = pd.DataFrame({
        'traceID':[span['traceID'] for trace in data for span in trace['spans']],
        'operationName':[span['operationName'] for trace in data for span in trace['spans']],
        'startTime':[span['startTime'] for trace in data for span in trace['spans']],
        'duration':[span['duration'] for trace in data for span in trace['spans']],
    })
    df['endTime'] = df['startTime'] + df['duration']
    traces = [trace['traceID'] for trace in data]
    
    return df, traces

def getTraceDurationDistribution(fname):
    df, traces = jaegar_decode(fname)
    # print(traces)
    # print(df[:10])
    durations = []
    # For each trace, calculate the start time and stop time
    for trace in traces:
        trace_spans = df[df['traceID'] == trace]
        trace_start = min(trace_spans['startTime'])
        trace_end = max(trace_spans['endTime'])
        # converting to millis from micros
        duration = (trace_end - trace_start) / 1000
        durations += [duration]
        
    mu = np.mean(durations)
    std = np.std(durations)
    percentiles = np.percentile(durations, [50, 75, 90, 99, 99.9, 99.99, 99.999, 100])
    
    return mu, std, percentiles

# 1 thread with 1 connection with 1000 RPS in the first workload
_, _, p = getTraceDurationDistribution('./traces-1711494724532.json')
print(p)

# This is when I ran the same experiment for 1 minute
_, _, p = getTraceDurationDistribution('./traces-1711494724532-1min.json')
print(p)

# This is when I ran DeathStarBench wrk2 with one of Indy's machines with 4 threads, 1000 connections, and 3000 RPS.
_, _, p = getTraceDurationDistribution('./traces-1711497385465.json')
print(p)

# This is when I ran the 3 machine setup (mentioned in the other chat). If you saw the other chat, then you know that 
# the results across those machines were inconsistent, and the single machine's results had lower latency as opposed
# to multiple machine setup's
_, _, p = getTraceDurationDistribution('./traces-1711498894034.json')
print(p)

# Here is the JSON data from Jaeger from when I ran the tracing for wrk2/wrk -D fixed -t 4 -c 500 -d 1m -L -s 
# hotelReservation/wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua http://clnode056.clemson.cloudlab.us:5000/ -R 1000
# Attached are also the cAdvisor results of the hotel_reserv_search container, which contain the CPU usage
# and memory results (under stats property of cadvisor_results JSON) over the time when I ran the load generator
# _, _, p = getTraceDurationDistribution('./jsonData-1.json')
# print(p)

# This is the data from when I ran `wrk2/wrk -D fixed -t 1 -c 500 -d 1m
# -L -s hotelReservation/wrk2/scripts/hotel-reservation/mixed-workload_type_1.lua http://clnode056.clemson.cloudlab.us:5000/ -R 1000`
# _, _, p = getTraceDurationDistribution('./jsonData-2.json')
# print(p)

# These are the results from when I ran 6 threads with 500 connections and 3000 RPS:
# _, _, p = getTraceDurationDistribution('./jsonData-3.json')
# print(p)

# This is when I ran with 6 threads with 1500 connections for 1 minute for 3000 RPS:
# _, _, p = getTraceDurationDistribution('./jsonData-4.json')
# print(p)

# Even with the multi machine setup, it appears that the results wrk2 records appear
# to be off from the latencies Jaeger gets as jaeger is able to see smaller latencies
# than what each of the machines record. My guess has to be the other delays not accounted
# for, but it possibly means something more than that. I also notice two red dots, which mean
# failures, but wrk2 did not notice any failures here, so I am more skeptical about how it's
# collecting and analyzing the data as well.
_, _, p = getTraceDurationDistribution('./traces-1711494724532.json')
print(p)

# @Ayaan Shah Another set of traces to analyze. From what I have noticed when running Mark's experiment
# against HotelReservation, it seems for a higher RPS value, the latencies between the server results and
# the client results appear to have a huge gap because the traces here appear to be in the microseconds region
# (mostly less than 20 ms, usually less than 10 ms) but the wrk2 results appear to be in seconds
# (like 7 seconds, and that is also for the first request as well). It cannot be queueing delay as I feel the
# data sent to the server should be such that it is able to fit into one packet.
# I think this is what this issue is referring to: https://github.com/delimitrou/DeathStarBench/issues/10
_, _, p = getTraceDurationDistribution('./traces-1711856770511.json')
print(p)


# example span start time: 1711494698069054
# example current time   : 1711909199565||| hence times are in microseconds


# df, _ = jaegar_decode('./traces-1711494724532.json')
# print(df[:100])