import sys

import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv) != 2:
    print("Usage: python analysis.py <log_file>")
    sys.exit(1)

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    log = f.read()

REQ_SEND = "S"
REQ_RECV = "R"
ERROR = "E"

latencies = []
request_timestamps = []
error_timestamps = []
curr_in_flight = set()
in_flight = []

for line in log.split("\n"):
    if line.startswith(REQ_SEND):
        vals = line.split(",")
        req_id = int(vals[1])
        timestamp = int(vals[2])

        request_timestamps.append(timestamp)
        curr_in_flight.add(req_id)
        in_flight.append((timestamp, len(curr_in_flight)))
    elif line.startswith(REQ_RECV):
        vals = line.split(",")
        req_id = int(vals[1])
        timestamp = int(vals[2])
        latency = int(vals[3])

        latencies.append(latency)
        curr_in_flight.remove(req_id)
        in_flight.append((timestamp, len(curr_in_flight)))
    elif line.startswith(ERROR):
        vals = line.split(",")
        req_id = int(vals[1])
        error_msg = vals[2]

        error_timestamps.append(timestamp)
        curr_in_flight.remove(req_id)
        in_flight.append((timestamp, len(curr_in_flight)))
    else:
        continue

for line in log.split("\n"):
    if line.startswith(REQ_SEND):
        vals = line.split(",")
        req_id = int(vals[1])
        timestamp = int(vals[2])

        request_timestamps.append(timestamp)
    elif line.startswith(REQ_RECV):
        vals = line.split(",")
        req_id = int(vals[1])
        timestamp = int(vals[2])
        latency = int(vals[3])

        latencies.append(latency)
    elif line.startswith(ERROR):
        vals = line.split(",")
        req_id = int(vals[1])
        error_msg = vals[2]
    else:
        continue


# graph distribution of latencies
latencies = np.array(sorted(latencies))
plt.hist(latencies / 1000, bins=100)
plt.ylabel("Count")
plt.xlabel("Latency (ms)")
perct95 = np.percentile(latencies, 95)
perct99 = np.percentile(latencies, 99)
plt.vlines(perct95 / 1000, 0, 1000, color="b", label="95th percentile")
plt.vlines(perct99 / 1000, 0, 1000, color="r", label="99th percentile")
plt.legend()
plt.show()


# graph distribution of request sent times
def standardize_timestamps(timestamps):
    timestamps = np.array(timestamps).astype(np.float64)
    timestamps -= timestamps[0]
    timestamps /= 1000.0
    return timestamps


req_times = standardize_timestamps(request_timestamps)
err_times = standardize_timestamps(error_timestamps)
timestamps, in_flight = zip(*in_flight)
timestamps = standardize_timestamps(timestamps)
fig, ax1 = plt.subplots()
ax2 = ax1.twinx()
ax1.hist(req_times, bins=100, label="Request Sent")
ax1.hist(err_times, bins=100, label="Request Error")
ax2.plot(timestamps, in_flight, label="In-flight requests", c="r")
plt.xlabel("Time (ms)")
ax1.set_ylabel("Request Count")
ax2.set_ylabel("In-Flight Requests Count")
ax1.legend()
ax2.legend()
plt.show()
