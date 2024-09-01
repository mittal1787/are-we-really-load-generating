import time
import itertools
import paramiko
import threading
import os

conn_counts = [10, 20, 25, 50, 100, 200, 500, 1000, 10000]
thread_counts = [1, 2, 4, 8, 10, 12, 16, 24]
rps_counts = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]


# DATA_DIR = "data-wrk2-dsb-multimachine"
# WRK = "DeathStarBench/wrk2/wrk"
DATA_DIR = "data-wrk2"

def read_wrk_cpu_utilization(machine_name:str, server_machine_name:str, thread_count: int, conn_count: int, rps: int, experiment_name:str, barrier):
    file_to_write = open(f"{DATA_DIR}/{experiment_name}/client={machine_name}-server={server_machine_name}/t{thread_count}-c{conn_count}-rps{rps}/wrk2-cpu-util.csv","w")
    file_to_write.write("PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND\n")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(machine_name, username="yugm2")
    barrier.wait()
    for i in range(60):
        stdin, stdout, stderr = ssh_con.exec_command(f"top -b -n1 | grep wrk")
        file_to_write.write(stdout.read().decode("utf-8")[2:])
        # print(stderr.read())
        time.sleep(1)
    file_to_write.close()
    print("wrk2 CPU utilization done")

def read_server_cpu_utilization(client_hostname, server_machine_name:str, machine_thread_count:int, machine_conn_count:int, rps:int, experiment_name:str, barrier):
    file_to_write = open(f"{DATA_DIR}/{experiment_name}/client={client_hostname}-server={server_machine_name}/t{machine_thread_count}-c{machine_conn_count}-rps{rps}/server-cpu-util.csv","w")
    file_to_write.write("PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND\n")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_machine_name, username="yugm2")
    barrier.wait()
    for i in range(60):
        stdin, stdout, stderr = ssh_con.exec_command(f"top -b -n1 | grep main")
        file_to_write.write(stdout.read().decode("utf-8"))
        time.sleep(1)
    file_to_write.close()
    print("Server CPU utilization done reading")

def run_wrk2_on_client_machine(client_machine_name:str, server_machine_name:str, thread_count: int, conn_count: int, machine_rps:int, experiment_name:str, barrier):
    wrk = "are-we-really-load-generating/new-experiments/wrk2/wrk"
    cmd = f"{wrk} -t{thread_count} -c{conn_count} -d60s -R{machine_rps} --latency http://" + server_machine_name + ":8000/hello"
    file_to_write = open(f"{DATA_DIR}/{experiment_name}/client={client_machine_name}-server={server_machine_name}/t{thread_count}-c{conn_count}-rps{machine_rps}/wrk2_results.csv","w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_machine_name, username="yugm2")
    barrier.wait()
    stdin, stdout, stderr = ssh_con.exec_command(cmd)
    file_to_write.write(stdout.read().decode("utf-8"))
    file_to_write.close()
    print("Finished reading wrk2 on client machine")

def read_client_tcpdump(client_hostname:str, server_machine_name: str, thread_count: int, conn_count: int, rps:int, experiment_name:str, barrier):
    cmd = "cd are-we-really-load-generating/new-experiments/common && python3 tcpdumpreader.py " + server_machine_name
    file_to_write = open(f"{DATA_DIR}/{experiment_name}/client={client_hostname}-server={server_machine_name}/t{thread_count}-c{conn_count}-rps{rps}/client_tcpdump.csv","w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_hostname, username="yugm2")
    barrier.wait()
    stdin, stdout, stderr = ssh_con.exec_command(cmd)
    client_data = stdout.read().decode("utf-8")
    file_to_write.write(client_data)
    file_to_write.close()
    print("Finished reading tcpdump")

def run_server(client_hostname:str, server_machine_name: str, thread_count: int, conn_count: int, rps:int, experiment_name:str, barrier):
    file_to_write = open(f"{DATA_DIR}/{experiment_name}/client={client_hostname}-server={server_machine_name}/t{thread_count}-c{conn_count}-rps{rps}/server_arrival_times.csv","w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_machine_name, username="yugm2")
    ssh_con.exec_command(f"go run are-we-really-load-generating/new-experiments/{experiment_name}/main.go > timestamp.txt")
    barrier.wait()
    time.sleep(60)
    print("run_server: Now read lines")
    ssh_con.close()
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_machine_name, username="yugm2")
    stdin, stdout, stderr = ssh_con.exec_command("cat timestamp.txt")
    file_to_write.write(stdout.read().decode().replace('\x00',''))
    file_to_write.close()
    print("Finished running server")

def install_wrk2(client_hostname:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_hostname, username="yugm2")
    ssh_con.exec_command("git clone https://github.com/mittal1787/are-we-really-load-generating.git")
    ssh_con.exec_command("cd are-we-really-load-generating/new-experiments")
    stdin, stdout, stderr = ssh_con.exec_command("sh install_wrk2.sh")
    try:
        stdin.write("Y\n")
        stdin.flush()
    except OSError:
        pass

def run_wrk2(client_hostname:str, server_machine_name: str, experiment_name: str):
    os.makedirs(DATA_DIR, exist_ok=True)
    os.makedirs(f"{DATA_DIR}/experiment_name")
    os.makedirs(f"{DATA_DIR}/experiment_name/client={client_hostname}-server={server_machine_name}", exist_ok=True)
    configs = itertools.product(conn_counts, thread_counts)
    for rps in rps_counts:
        for i, (conn, thread) in enumerate(configs):
            if conn >= thread:
                print(f"RPS = {rps}, Connections = {conn}, Thread = {thread}")
                os.makedirs(f"{DATA_DIR}/client={client_hostname}-server={server_machine_name}/t{thread}-c{conn}-rps{rps}", exist_ok=True)
                barrier = threading.Barrier(6)
                py_threads = []
                py_threads.append(threading.Thread(target=run_server, args=(client_hostname, server_machine_name, thread, conn, rps, experiment_name, barrier)))
                py_threads.append(threading.Thread(target=read_wrk_cpu_utilization, args=(client_hostname, server_machine_name, thread, conn, rps, experiment_name, barrier)))
                py_threads.append(threading.Thread(target=read_server_cpu_utilization, args=(client_hostname, server_machine_name, thread, conn, rps, experiment_name, barrier)))
                py_threads.append(threading.Thread(target=run_wrk2_on_client_machine, args=(client_hostname, server_machine_name, thread, conn, rps, experiment_name, barrier)))
                py_threads.append(threading.Thread(target=read_client_tcpdump, args=(client_hostname, server_machine_name, thread, conn, rps, experiment_name, barrier)))

                for py_thread in py_threads:
                    py_thread.start()
                # Signal the threads to begin
                barrier.wait()
                for py_thread in py_threads:
                    py_thread.join()
                time.sleep(5) 