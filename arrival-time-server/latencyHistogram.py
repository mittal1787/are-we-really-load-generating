import sys
import numpy as np
import matplotlib.pyplot as plt

if len(sys.argv) != 2:
    print("Usage: python latencyHistogram.py <log_file>")
    sys.exit(1)

path = sys.argv[1]
with open(path, "r", encoding="utf-8") as f:
    log = f.read()

arrival_times = []

for line in log.split("\n"):
    if len(line) > 0:
        arrival_times.append(float(line))

plt.hist(arrival_times,bins=60)
plt.ylabel("Count")
plt.xlabel("Arrival time")
plt.savefig("latencyHistogram.png")
plt.show()
