from datetime import datetime 
from scp import SCPClient
import matplotlib.pyplot as plt
import time
import itertools
import paramiko
import threading
import os
import sys
import numpy as np
import json
import re

conn_counts = [10, 20, 25, 50, 100, 200, 500, 1000, 10000]
thread_counts = [1, 2, 4, 8, 10, 12, 16, 24]
rps_counts = [500, 1000, 5000, 10000, 50000, 100000]


DATA_DIR_WRK2_DSB = "data-wrk2-dsb-multimachine"
DATA_DIR = "data-wrk2"
DATA_DIR_K6 = "data-k6"

def create_latency_histogram(timestamp_file:str, file_to_save:str):
    with open(timestamp_file, "r", encoding="utf-8") as f:
        log = f.read()

    arrival_times = []

    for line in log.split("\n"):
        if len(line) > 0:
            arrival_times.append(float(line))

    plt.clf()
    plt.hist(arrival_times,bins=60)
    plt.ylabel("Count")
    plt.xlabel("Arrival time")
    plt.savefig(file_to_save)

def parse_tcpdumps_file(file_name:str, client_hostname:str):
    latencies = []
    with open(file_name) as file:
        lines = [line.rstrip() for line in file]
        i = 0
        while len(lines) > 0:
            line = lines[i]
            # print("line=", line)
            if line.strip():
                time = line[0:15]
                # print("time=", time)
                try:
                    sender_and_reciever = line[line.index("IP")+3:line.index(": ")].split(" > ")
                    if client_hostname in sender_and_reciever[0]:
                        # print("sender_and_reciever = ", sender_and_reciever)
                        j = i + 1
                        while j < len(lines):
                            line_two = lines[j]
                            if line_two.strip():
                                time_two = line_two[0:15]
                                sender_and_reciever_two = line_two[line_two.index("IP")+3:line_two.index(": ")].split(" > ")
                                if sender_and_reciever[0] == sender_and_reciever_two[1] and sender_and_reciever[1] == sender_and_reciever_two[0]:
                                    time_elapsed = datetime.strptime(time_two,"%H:%M:%S.%f") - datetime.strptime(time, "%H:%M:%S.%f")
                                    latencies.append(time_elapsed.total_seconds()*1000)
                                    lines.remove(line_two)
                                    break
                            j += 1
                except ValueError:
                    pass
                except IndexError:
                    pass
            lines.remove(line)
    return {"latencies": latencies, "percentiles": np.percentile(latencies, [50,75,90,99,99.9,99.99,99.999,100]).tolist()}

def read_wrk_cpu_utilization(ssh_user:str, machine_name:str, dir_name:str, barrier):
    file_to_write = open(f"{dir_name}/wrk2-cpu-util.csv","w")
    file_to_write.write("PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND\n")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(machine_name, username=ssh_user)
    barrier.wait()
    for i in range(60):
        stdin, stdout, stderr = ssh_con.exec_command(f"top -b -n1 | grep wrk")
        file_to_write.write(stdout.read().decode("utf-8")[2:])
        # print(stderr.read())
        time.sleep(1)
    file_to_write.close()
    ssh_con.close()
    print("wrk2 CPU utilization done")

def read_server_cpu_utilization(ssh_user, dir_name, server_machine_name:str, server_app:str, barrier):
    file_to_write = open(f"{dir_name}/server-cpu-util.csv","w")
    file_to_write.write("PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND\n")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_machine_name, username=ssh_user)
    barrier.wait()
    for i in range(60):
        stdin, stdout, stderr = ssh_con.exec_command(f"top -b -n1 | grep {server_app}")
        file_to_write.write(stdout.read().decode("utf-8"))
        time.sleep(1)
    file_to_write.close()
    ssh_con.close()
    print("Server CPU utilization done reading")

def run_wrk2_on_client_machine(ssh_user:str, client_machine_name:str, server_machine_name:str, thread_count: int, conn_count: int, machine_rps:int, experiment_name:str, port:str, lua_script_path, dir_name, barrier):
    wrk = "./are-we-really-load-generating/new-experiments/wrk2/wrk"
    cmd = f"{wrk} -t{thread_count} -c{conn_count} -d60s -R{machine_rps} --latency http://" + server_machine_name + ":" + port
    if lua_script_path != None:
        cmd += " --script " + lua_script_path
    print("run_wrk2_on_client_machine: command = ", cmd)
    file_to_write = open(f"{dir_name}/wrk2_results.csv","w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_machine_name, username=ssh_user)
    barrier.wait()
    stdin, stdout, stderr = ssh_con.exec_command(cmd)
    print("run_wrk2_on_client_machine: ", stderr.read().decode("utf-8"))
    file_to_write.write(stdout.read().decode("utf-8"))
    file_to_write.close()
    print("Finished reading wrk2 on client machine")
    ssh_con.close()

def read_client_tcpdump(ssh_user:str, client_hostname:str, server_machine_name: str, dir_name:str, barrier):
    print("read_client_tcpdump")
    cmd = "cd are-we-really-load-generating/new-experiments/common && python3 tcpdumpreader.py " + server_machine_name
    file_to_write = open(f"{dir_name}/client_tcpdump.csv","w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_hostname, username=ssh_user)
    barrier.wait()
    stdin, stdout, stderr = ssh_con.exec_command(cmd, timeout=120)
    while True:
        file_to_write.write(stdout.readline())
        if stdout.channel.exit_status_ready():
            break
    file_to_write.close()
    with open(f"{dir_name}/client_tcpdump_results.json","w") as f:
        f.write(json.dumps(parse_tcpdumps_file(f"{dir_name}/client_tcpdump.csv", client_hostname)))
    print("read_client_tcpdump: Finished reading tcpdump")
    ssh_con.close()

def run_server(ssh_user:str, server_machine_name: str, experiment_name:str, dir_name:str, barrier):
    filename = f"{dir_name}/server_arrival_times.csv"
    file_to_write = open(filename,"w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_machine_name, username=ssh_user)
    ssh_con.exec_command(f"go run are-we-really-load-generating/new-experiments/{experiment_name}/main.go > timestamp.txt")
    barrier.wait()
    time.sleep(60)
    ssh_con.close()
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_machine_name, username=ssh_user)
    stdin, stdout, stderr = ssh_con.exec_command("cat timestamp.txt")
    file_to_write.write(stdout.read().decode().replace('\x00',''))
    file_to_write.close()
    create_latency_histogram(filename,  f"{dir_name}/server_arrival_times.png")
    print("Finished running server")
    ssh_con.close()

def install_wrk2(client_hostname:str, ssh_user:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_hostname, username=ssh_user)
    stdin, stdout, stderr =  ssh_con.exec_command("git clone https://github.com/mittal1787/are-we-really-load-generating.git")
    print("install_wrk2 err: ", str(stderr.read()))
    stdin, stdout, stderr =  ssh_con.exec_command("cd are-we-really-load-generating && git pull origin main && cd new-experiments && sh install_wrk2.sh")
    print("install_wrk2 err: ", str(stderr.read()))
    try:
        stdin.write("Y\n")
        stdin.flush()
    except OSError:
        pass
    ssh_con.close()

def run_wrk2(client_hostname:str, server_machine_name: str, experiment_name: str, lua_script_path: str = None, ssh_user: str = None, port:str = "8000"):
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR}", exist_ok=True)
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR}/client={client_hostname}-server={server_machine_name}", exist_ok=True)
    configs = itertools.product(conn_counts, thread_counts)
    for rps in rps_counts:
        for i, (conn, thread) in enumerate(configs):
            if conn >= thread:
                print(f"RPS = {rps}, Connections = {conn}, Thread = {thread}")
                dir_name = f"new-experiments/{experiment_name}/{DATA_DIR}/client={client_hostname}-server={server_machine_name}/t{thread}-c{conn}-rps{rps}"
                os.makedirs(dir_name, exist_ok=True)
                barrier = threading.Barrier(6)
                py_threads = []
                py_threads.append(threading.Thread(target=run_server, args=(ssh_user, server_machine_name, experiment_name, dir_name, barrier)))
                py_threads.append(threading.Thread(target=read_wrk_cpu_utilization, args=(ssh_user, client_hostname, dir_name, barrier)))
                py_threads.append(threading.Thread(target=read_server_cpu_utilization, args=(ssh_user, dir_name, server_machine_name, "main", barrier)))
                py_threads.append(threading.Thread(target=run_wrk2_on_client_machine, args=(ssh_user, client_hostname, server_machine_name, thread, conn, rps, experiment_name, port, lua_script_path, dir_name, barrier)))
                py_threads.append(threading.Thread(target=read_client_tcpdump, args=(ssh_user, client_hostname, server_machine_name, dir_name, barrier)))

                for py_thread in py_threads:
                    py_thread.start()
                # Signal the threads to begin
                barrier.wait()
                for py_thread in py_threads:
                    py_thread.join()
                time.sleep(5) 

def install_wrk2_dsb(client_hostname:str, ssh_user:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_hostname, username=ssh_user)
    ssh_con.exec_command("git clone https://github.com/mittal1787/are-we-really-load-generating.git && cd are-we-really-load-generating && git pull origin main")
    stdin, stdout, stderr = ssh_con.exec_command("sh are-we-really-load-generating/new-experiments/install_wrk2_dsb.sh")
    try:
        stdin.write("Y\n")
        stdin.flush()
    except OSError:
        pass
    ssh_con.close()

def install_wrk2_dsb(client_hostname:str, ssh_user:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_hostname, username=ssh_user)
    ssh_con.exec_command("git clone https://github.com/mittal1787/are-we-really-load-generating.git && cd are-we-really-load-generating && git pull origin main")
    stdin, stdout, stderr = ssh_con.exec_command("cd are-we-really-load-generating/new-experiments && sh install_wrk2.sh")
    try:
        stdin.write("Y\n")
        stdin.flush()
    except OSError:
        pass
    ssh_con.close()

def run_wrk2_dsb_on_client_machine(ssh_user:str, client_machine_name:str, server_machine_name:str, thread_count: int, conn_count: int, machine_rps:int, distribution_type:str, port:str, lua_script_path, dir_name, barrier):
    wrk = "are-we-really-load-generating/new-experiments/DeathStarBench/wrk2/wrk"
    cmd = f"{wrk} -t{thread_count} -c{conn_count} -d60s -R{machine_rps} -D {distribution_type} --requests --latency http://" + server_machine_name + ":" + port
    if lua_script_path != None:
        cmd += " --script " + lua_script_path
    file_to_write = open(f"{dir_name}/wrk2_results.csv","w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_machine_name, username=ssh_user)
    barrier.wait()
    stdin, stdout, stderr = ssh_con.exec_command(cmd)
    file_to_write.write(stdout.read().decode("utf-8"))
    file_to_write.close()
    ssh_con.close()
    print("Finished reading wrk2 on client machine")

def run_wrk2_dsb(client_hostname:str, server_machine_name: str, experiment_name: str, lua_script_path: str = None, ssh_user: str = None, port:str = "8000"):
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR_WRK2_DSB}", exist_ok=True)
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR_WRK2_DSB}/client={client_hostname}-server={server_machine_name}", exist_ok=True)
    configs = itertools.product(conn_counts, thread_counts)
    for rps in rps_counts:
        for i, (conn, thread) in enumerate(configs):
            if conn >= thread:
                for distr in ["fixed","exp","zipf","norm"]:
                    print(f"RPS = {rps}, Connections = {conn}, Thread = {thread}")
                    dir_name = f"new-experiments/{experiment_name}/{DATA_DIR_WRK2_DSB}/client={client_hostname}-server={server_machine_name}/t{thread}-c{conn}-rps{rps}-{distr}distribution"
                    os.makedirs(dir_name, exist_ok=True)
                    barrier = threading.Barrier(6)
                    py_threads = []
                    py_threads.append(threading.Thread(target=run_server, args=(ssh_user, server_machine_name, experiment_name, dir_name, barrier)))
                    py_threads.append(threading.Thread(target=read_wrk_cpu_utilization, args=(ssh_user, client_hostname, dir_name, barrier)))
                    py_threads.append(threading.Thread(target=read_server_cpu_utilization, args=(ssh_user, dir_name, server_machine_name, "main", barrier)))
                    py_threads.append(threading.Thread(target=run_wrk2_dsb_on_client_machine, args=(ssh_user, client_hostname, server_machine_name, thread, conn, rps, distr, port, experiment_name, lua_script_path, dir_name, barrier)))
                    py_threads.append(threading.Thread(target=read_client_tcpdump, args=(ssh_user, client_hostname, server_machine_name, dir_name, barrier)))

                    for py_thread in py_threads:
                        py_thread.start()
                    # Signal the threads to begin
                    barrier.wait()
                    for py_thread in py_threads:
                        py_thread.join()
                            
                    time.sleep(5) 

def install_k6(client_hostname:str, ssh_user:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_hostname, username=ssh_user)
    ssh_con.exec_command("git clone https://github.com/mittal1787/are-we-really-load-generating.git && cd are-we-really-load-generating && git pull origin main")
    stdin, stdout, stderr = ssh_con.exec_command("cd are-we-really-load-generating/new-experiments && sh install_k6.sh")
    try:
        stdin.write("Y\n")
        stdin.flush()
    except OSError:
        pass
    ssh_con.close()

def create_k6_constant_arrival_script_file(vus:int, server_hostname:str, port:str):
    return """
    import http from 'k6/http';
    
    export const options = {
        scenarios: {
            open_model: {
            executor: 'constant-arrival-rate',
            rate:""" + str(vus) + """,
            timeUnit: '1s',
            duration: '1m',
            preAllocatedVUs:""" + str(vus+5) + """ ,
            },
        },
    };

    export default function() {
        http.get('http://""" + server_hostname + ":" + port +  """');
    }
    """

def create_k6_ramping_arrival_script_file(vus:int, server_hostname:str, port:str):
    return """
    import http from 'k6/http';
    
    export const options = {
        scenarios: {
            open_model: {
            executor: 'ramping-arrival-rate',
            rate:""" + str(vus) + """,
            timeUnit: '1s',
            duration: '1m',
            preAllocatedVUs:""" + str(vus) + """ ,
            },
        },
    };

    export default function() {
        http.get('http://""" + server_hostname + ":" + port +  """');
    }
    """

def run_k6_on_client_machine(ssh_user:str, client_hostname:str, server_hostname:str, port:str, vus:int, dir_name:str, barrier):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
    ssh_con.connect(client_hostname, username=ssh_user)
    scp = SCPClient(ssh_con.get_transport())
    script_file = open(f"{dir_name}/script.js", "w")
    script_file.write(create_k6_constant_arrival_script_file(vus,server_hostname, port))
    script_file.close()
    scp.put(f"{dir_name}/script.js","script.js")
    barrier.wait()
    stdin, stdout, stderr = ssh_con.exec_command("k6 run --out json=test_results.json script.js", timeout=120)
    file_to_write = open(f"{dir_name}/k6_results.txt","w")
    file_to_write.write(stdout.read().decode("utf-8"))
    file_to_write.close()
    scp.get("test_results.json", f"{dir_name}/k6_results.json")
    scp.close()
    ssh_con.close()

def read_k6_cpu_utilization(ssh_user:str, machine_name:str, dir_name:str, barrier):
    file_to_write = open(f"{dir_name}/k6-cpu-util.csv","w")
    file_to_write.write("PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND\n")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(machine_name, username=ssh_user)
    barrier.wait()
    for i in range(60):
        stdin, stdout, stderr = ssh_con.exec_command(f"top -b -n1 | grep k6")
        file_to_write.write(stdout.read().decode("utf-8")[2:])
        # print(stderr.read())
        time.sleep(1)
    file_to_write.close()
    ssh_con.close()
    print("k6 CPU utilization done")

def run_k6(client_hostname:str, server_machine_name: str, experiment_name: str, lua_script_path: str = None, ssh_user: str = None, port:str = "8000"):
    for rps in rps_counts:
        print(f"run_k6: RPS = {rps}")
        dir_name = f"new-experiments/{experiment_name}/{DATA_DIR_K6}/client={client_hostname}-server={server_machine_name}/rps{rps}"
        os.makedirs(dir_name, exist_ok=True)
        barrier = threading.Barrier(6)
        py_threads = []
        py_threads.append(threading.Thread(target=run_server, args=(ssh_user, server_machine_name, experiment_name, dir_name, barrier)))
        py_threads.append(threading.Thread(target=read_k6_cpu_utilization, args=(ssh_user, client_hostname, dir_name, barrier)))
        py_threads.append(threading.Thread(target=read_server_cpu_utilization, args=(ssh_user, dir_name, server_machine_name, "main", barrier)))
        py_threads.append(threading.Thread(target=run_k6_on_client_machine, args=(ssh_user, client_hostname, server_machine_name, port, dir_name, barrier)))
        py_threads.append(threading.Thread(target=read_client_tcpdump, args=(ssh_user, client_hostname, server_machine_name, dir_name, barrier)))

        for py_thread in py_threads:
            py_thread.start()
        # Signal the threads to begin
        barrier.wait()
        for py_thread in py_threads:
            py_thread.join()
        time.sleep(5)         
