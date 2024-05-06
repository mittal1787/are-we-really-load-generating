import os
import subprocess
import time
import itertools
# import paramiko
import threading
from datetime import datetime
import requests

# conn_counts = [1, 2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 100, 150, 200, 300, 400, 500, 1000, 2000, 5000, 10000]
# thread_counts = [1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 40, 50, 100, 200]
# rps_counts = [10, 50, 100, 200, 500, 1000,1500,2000,2500,3000,4500,5000,7500,10000,20000,25000,30000,45000,50000,75000,100000]
conn_counts = [100]
thread_counts = [10]
rps_counts = [10000]
# machines = ["sp24-cs525-0301.cs.illinois.edu"]

containers = """hotel_reserv_profile
hotel_reserv_reservation
hotel_reserv_geo
hotel_reserv_recommendation
hotel_reserv_rate
hotel_reserv_frontend
hotel_reserv_user
hotel_reserv_search
hotel_reserv_reservation_mongo
hotelreservation-consul-1
hotel_reserv_user_mongo
hotel_reserv_profile_mongo
hotel_reserv_rate_mongo
hotel_reserv_recommendation_mongo
hotel_reserv_geo_mongo
hotel_reserv_rate_mmc
hotel_reserv_profile_mmc
hotel_reserv_reservation_mmc
""".split("\n")

# DATA_DIR = "data-wrk2-config-data"
# WRK = "../../wrk2/wrk"
DATA_DIR = "data-wrk2-dsb-config-data"
WRK = "../../DeathStarBench/wrk2/wrk"

def read_wrk_cpu_utilization(machine_name:str, machine_thread_count:int, machine_conn_count:int, rps:int):
    file_to_write = open(f"{DATA_DIR}/cpu_utils/t{machine_thread_count}-c{machine_conn_count}-rps{rps}-cpu-util.csv","w")
    file_to_write.write("PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND\n")
    for i in range(30):
        # stdin, stdout, stderr = ssh_con.exec_command(f"top -b -n1 | grep wrk")
        top_process = subprocess.Popen(["top", "-b", "-n1"], stdout=subprocess.PIPE, text=True)
        grep_process = subprocess.Popen(["grep", "wrk"], stdin=top_process.stdout, stdout=subprocess.PIPE, text=True)
        output, error = grep_process.communicate()

        file_to_write.write(output)
        # print(stderr.read())
        time.sleep(1)
    file_to_write.close()
    
def run_wrk2_on_machine(machine_name:str, machine_thread_count:int, machine_conn_count:int, machine_rps:int):
    cmd = f"{WRK} -t{machine_thread_count} -c{machine_conn_count} -d30s -R{machine_rps} --script ../../DeathStarBench/hotelReservation/wrk2/scripts/hotel-reservation/only-search.lua --latency http://c220g5-110414.wisc.cloudlab.us:5000/"
    file_to_write = open(f"{DATA_DIR}/wrk2_results/t{machine_thread_count}-c{machine_conn_count}-{machine_rps}-fixed.csv","w")
    res = subprocess.run(cmd.split(" "), capture_output=True)
    file_to_write.write(res.stdout.decode('utf-8'))
    file_to_write.close()

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(f"{DATA_DIR}/cpu_utils", exist_ok=True)
os.makedirs(f"{DATA_DIR}/server_cpu_utils", exist_ok=True)
os.makedirs(f"{DATA_DIR}/tracing_request_times", exist_ok=True)
os.makedirs(f"{DATA_DIR}/wrk2_results", exist_ok=True)

configs = itertools.product(conn_counts, thread_counts)


for i, (conn, thread) in enumerate(configs): 
    if conn >= thread:
        for rps in rps_counts:
            print("RPS =", rps, ", Conn =", conn, ", Thread =", thread)
            start_time = datetime.now().strftime('%Y-%m-%dT%H:%M:%S')
            print("start_time =", start_time)
            py_threads = []
            py_threads.append(threading.Thread(target=read_wrk_cpu_utilization, args=("apt001.apt.emulab.net", thread, conn, rps)))
            py_threads.append(threading.Thread(target=run_wrk2_on_machine, args=("apt001.apt.emulab.net", thread, conn, rps)))


            for py_thread in py_threads:
                py_thread.start()
            for py_thread in py_threads:
                py_thread.join()

            for container_name in containers:
                with open(f"{DATA_DIR}/server_cpu_utils/t{thread}-c{conn}-{rps}-{container_name}-cpu-data.json", "w+") as f:
                    f.write(requests.get(f"http://c220g5-110414.wisc.cloudlab.us:8080/api/v1.3/docker/{container_name}?start_time={start_time}").text)

            
            file_to_write = open(f"{DATA_DIR}/tracing_request_times/t{thread}-c{conn}-rps{rps}-server-cpu-util.json","w")
            file_to_write.write(requests.get(f"http://c220g5-110414.wisc.cloudlab.us:16686/api/traces?limit={min(3000,rps*30)}&lookback=1m&service=search").text)
            file_to_write.close()
            time.sleep(5) 