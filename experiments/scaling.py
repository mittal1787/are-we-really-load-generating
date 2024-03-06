import os
import subprocess
import time
import itertools

conn_counts = [1, 2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 100, 150, 200, 300, 400, 500]
thread_counts = [1, 2, 3, 4, 5, 10]


DATA_DIR = "data-wrk2-dsb"
WRK = "../DeathStarBench/wrk2/wrk"
# DATA_DIR = "data-wrk2"
# WRK = "../wrk2/wrk"


def run_trial(thread_count: int, conn_count: int):
    cmd = f"{WRK} -t{thread_count} -c{conn_count} -d30s -R1000000 --latency http://c220g5-110905.wisc.cloudlab.us"
    print(cmd)
    res = subprocess.run(cmd.split(" "), capture_output=True)
    with open(f"{DATA_DIR}/t{thread_count}-c{conn_count}.txt", "w+") as f:
        f.write(res.stdout.decode('utf-8'))
    

os.makedirs(DATA_DIR, exist_ok=True)

configs = itertools.product(conn_counts, thread_counts)
for i, (conn, thread) in enumerate(configs):
    res = run_trial(thread, conn)
    time.sleep(5)

# with open("out.csv", "w+") as f:
#     f.write(f"conn,thread,RPS\n")
# 
# configs = itertools.product(conn_counts, thread_counts)
# for i, (conn, thread) in enumerate(configs):
#     res = run_trial(thread, conn)
#     with open("out.csv", "a+") as f:
#         f.write(f"{conn},{thread},res\n")
