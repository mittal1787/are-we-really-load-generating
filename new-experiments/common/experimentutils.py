import time
import itertools
import paramiko
import threading
import os
import tcpdumpanalysis
import json

conn_counts = [10, 20, 25, 50, 100, 200, 500, 1000, 10000]
thread_counts = [1, 2, 4, 8, 10, 12, 16, 24]
rps_counts = [500, 1000, 5000, 10000, 50000, 100000]


DATA_DIR_WRK2_DSB = "data-wrk2-dsb-multimachine"
DATA_DIR = "data-wrk2"

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
    print("Server CPU utilization done reading")

def run_wrk2_on_client_machine(ssh_user:str, client_machine_name:str, server_machine_name:str, thread_count: int, conn_count: int, machine_rps:int, experiment_name:str, lua_script_path, dir_name, barrier):
    wrk = "are-we-really-load-generating/new-experiments/wrk2/wrk"
    cmd = f"{wrk} -t{thread_count} -c{conn_count} -d60s -R{machine_rps} --latency http://" + server_machine_name + ":8000"
    if lua_script_path != None:
        cmd += " --script " + lua_script_path
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

def read_client_tcpdump(ssh_user:str, client_hostname:str, server_machine_name: str, dir_name:str, barrier):
    cmd = "cd are-we-really-load-generating/new-experiments/common && python3 tcpdumpreader.py " + server_machine_name
    file_to_write = open(f"{dir_name}/client_tcpdump.csv","w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_hostname, username=ssh_user)
    barrier.wait()
    stdin, stdout, stderr = ssh_con.exec_command(cmd)
    client_data = stdout.read().decode("utf-8")
    file_to_write.write(client_data)
    file_to_write.close()
    with open(f"{dir_name}/client_tcpdump_results.json","w") as f:
        f.write(json.dumps(tcpdumpanalysis(f"{dir_name}/client_tcpdump.csv", client_hostname)))
    print("Finished reading tcpdump")

def run_server(ssh_user:str, client_hostname:str, server_machine_name: str, thread_count: int, conn_count: int, rps:int, experiment_name:str, barrier):
    file_to_write = open(f"new-experiments/{experiment_name}/{DATA_DIR}/client={client_hostname}-server={server_machine_name}/t{thread_count}-c{conn_count}-rps{rps}/server_arrival_times.csv","w")
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
    print("Finished running server")

def install_wrk2(client_hostname:str, ssh_user:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_hostname, username=ssh_user)
    stdin, stdout, stderr =  ssh_con.exec_command("git clone https://github.com/mittal1787/are-we-really-load-generating.git")
    print("install_wrk2 err: ", str(stderr.read()))
    stdin, stdout, stderr =  ssh_con.exec_command("cd are-we-really-load-generating && git pull origin main && sh new-experiments/install_wrk2.sh")
    print("install_wrk2 err: ", str(stderr.read()))
    try:
        stdin.write("Y\n")
        stdin.flush()
    except OSError:
        pass

def run_wrk2(client_hostname:str, server_machine_name: str, experiment_name: str, lua_script_path: str = None, ssh_user: str = None):
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
                py_threads.append(threading.Thread(target=run_server, args=(ssh_user, client_hostname, server_machine_name, thread, conn, rps, experiment_name, barrier)))
                py_threads.append(threading.Thread(target=read_wrk_cpu_utilization, args=(ssh_user, client_hostname, dir_name, barrier)))
                py_threads.append(threading.Thread(target=read_server_cpu_utilization, args=(ssh_user, dir_name, server_machine_name, "main", barrier)))
                py_threads.append(threading.Thread(target=run_wrk2_on_client_machine, args=(ssh_user, client_hostname, server_machine_name, thread, conn, rps, experiment_name, lua_script_path, dir_name, barrier)))
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

def install_wrk2_dsb(client_hostname:str, ssh_user:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_hostname, username=ssh_user)
    ssh_con.exec_command("git clone https://github.com/mittal1787/are-we-really-load-generating.git && cd are-we-really-load-generating && git pull origin main")
    ssh_con.exec_command("cd are-we-really-load-generating/new-experiments")
    stdin, stdout, stderr = ssh_con.exec_command("sh install_wrk2.sh")
    try:
        stdin.write("Y\n")
        stdin.flush()
    except OSError:
        pass

def run_wrk2_dsb_on_client_machine(ssh_user:str, client_machine_name:str, server_machine_name:str, thread_count: int, conn_count: int, machine_rps:int, distribution_type:str, lua_script_path, dir_name, barrier):
    wrk = "are-we-really-load-generating/new-experiments/DeathStarBench/wrk2/wrk"
    cmd = f"{wrk} -t{thread_count} -c{conn_count} -d60s -R{machine_rps} -D {distribution_type} --latency http://" + server_machine_name + ":8000"
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
    print("Finished reading wrk2 on client machine")

def run_wrk2_dsb(client_hostname:str, server_machine_name: str, experiment_name: str, lua_script_path: str = None, ssh_user: str = None):
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
                    py_threads.append(threading.Thread(target=run_server, args=(ssh_user, client_hostname, server_machine_name, thread, conn, rps, experiment_name, barrier)))
                    py_threads.append(threading.Thread(target=read_wrk_cpu_utilization, args=(ssh_user, client_hostname, dir_name, barrier)))
                    py_threads.append(threading.Thread(target=read_server_cpu_utilization, args=(ssh_user, dir_name, server_machine_name, "main", barrier)))
                    py_threads.append(threading.Thread(target=run_wrk2_dsb_on_client_machine, args=(ssh_user, client_hostname, server_machine_name, thread, conn, rps, distr, experiment_name, lua_script_path, dir_name, barrier)))
                    py_threads.append(threading.Thread(target=read_client_tcpdump, args=(ssh_user, client_hostname, server_machine_name, dir_name, barrier)))

                    for py_thread in py_threads:
                        py_thread.start()
                    # Signal the threads to begin
                    barrier.wait()
                    for py_thread in py_threads:
                        py_thread.join()
                    time.sleep(5) 