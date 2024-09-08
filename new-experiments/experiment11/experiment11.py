import getopt
import itertools
import os
import sys
import threading
import paramiko
import time
from ..common import experimentutils

conn_counts = [10, 20, 25, 50, 100, 200, 500]
thread_counts = [1, 2, 4, 8, 10, 12, 16, 24]
rps_counts = [500, 1000, 2000, 5000, 10000]

DATA_DIR = "data-wrk2"
DATA_DIR_DSB = "data-wrk2-dsb"

def install_servers(user:str, server_name:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_name, username=user)
    stdin, stdout, stderr = ssh_con.exec_command("git clone https://github.com/mittal1787/are-we-really-load-generating.git ; cd are-we-really-load-generating ; git pull origin main")
    while True:
        try:
            stdin.write("Y\n")
            stdin.flush()
        except OSError:
            break
    print(str(stderr.read()))
    print(str(stdout.read()))
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()

def run_server(user:str, server_one: str, duration:str, dir_name:str, barrier):
    filename = f"{dir_name}/server_arrival_times.csv"
    file_to_write = open(filename,"w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_one, username=user)
    stdin, stdout, stderr = ssh_con.exec_command(f"go run are-we-really-load-generating/new-experiments/experiment11/main.go {duration} > timestamp.txt")
    barrier.wait()
    time.sleep(60)
    ssh_con.close()
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_one, username=user)
    stdin, stdout, stderr = ssh_con.exec_command("cat timestamp.txt")
    file_to_write.write(stdout.read().decode().replace('\x00',''))
    file_to_write.close()
    experimentutils.create_latency_histogram(filename,  f"{dir_name}/server_arrival_times.png")
    print("Finished running server")

def run_wrk2(client_hostname:str, server_one_hostname: str, experiment_name: str, user: str):
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR}", exist_ok=True)
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR}/client={client_hostname}-server_one={server_one_hostname}-server_two={server_two_hostname}", exist_ok=True)
    configs = itertools.product(conn_counts, thread_counts)
    for rps in rps_counts:
        for i, (conn, thread) in enumerate(configs):
            for duration in ['1s','5s','10s','30s','45s','1m','1m30s','2m']:
                if conn >= thread:
                    print(f"RPS = {rps}, Connections = {conn}, Thread = {thread}, duration = {duration}")
                    dir_name = f"new-experiments/{experiment_name}/{DATA_DIR}/client={client_hostname}-server={server_one_hostname}/t{thread}-c{conn}-rps{rps}-{duration}"
                    os.makedirs(dir_name, exist_ok=True)
                    barrier = threading.Barrier(6)
                    py_threads = []
                    py_threads.append(threading.Thread(target=run_server, args=(user, server_one_hostname, duration, dir_name, barrier)))
                    py_threads.append(threading.Thread(target=experimentutils.read_wrk_cpu_utilization, args=(user, client_hostname, dir_name, barrier)))
                    py_threads.append(threading.Thread(target=experimentutils.run_wrk2_on_client_machine, args=(user, client_hostname, server_one_hostname, thread, conn, rps, experiment_name, "8001", None, dir_name, barrier)))
                    py_threads.append(threading.Thread(target=experimentutils.read_client_tcpdump, args=(user, client_hostname, server_one_hostname, dir_name, barrier)))
                    py_threads.append(threading.Thread(target=experimentutils.read_server_cpu_utilization, args=(user, dir_name, server_one_hostname, "main", barrier)))

                    for py_thread in py_threads:
                        py_thread.start()
                    time.sleep(1)
                    # Signal the threads to begin
                    barrier.wait()
                    for py_thread in py_threads:
                        py_thread.join()
                    time.sleep(5) 

def run_wrk2_dsb(client_hostname:str, server_one_hostname: str, experiment_name: str, user: str):
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR_DSB}", exist_ok=True)
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR_DSB}/client={client_hostname}-server_one={server_one_hostname}-server_two={server_two_hostname}", exist_ok=True)
    configs = itertools.product(conn_counts, thread_counts)
    for rps in rps_counts:
        for i, (conn, thread) in enumerate(configs):
            for duration in ['1s','5s','10s','30s','45s','1m','1m30s','2m']:
                if conn >= thread:
                    for distr in ["fixed","exp","zipf","norm"]:
                        print(f"RPS = {rps}, Connections = {conn}, Thread = {thread}, Distribution = {disr}, Duration = {duration}")
                        dir_name = f"new-experiments/{experiment_name}/{DATA_DIR_DSB}/client={client_hostname}-server_one={server_one_hostname}-server_two={server_two_hostname}/t{thread}-c{conn}-rps{rps}-{duration}-"
                        client_to_s1_packets = f"{dir_name}/{client_hostname}-to-{server_one_hostname}-packets"
                        s1_to_s2_packets = f"{dir_name}/{server_one_hostname}-to-{server_two_hostname}-packets"
                        os.makedirs(dir_name, exist_ok=True)
                        os.makedirs(client_to_s1_packets, exist_ok=True)
                        os.makedirs(s1_to_s2_packets, exist_ok=True)
                        barrier = threading.Barrier(8)
                        py_threads = []
                        py_threads.append(threading.Thread(target=run_server, args=(user, server_one_hostname, duration, dir_name, barrier)))
                        py_threads.append(threading.Thread(target=experimentutils.read_wrk_cpu_utilization, args=(user, client_hostname, dir_name, barrier)))
                        py_threads.append(threading.Thread(target=experimentutils.run_wrk2_on_client_machine, args=(user, client_hostname, server_one_hostname, thread, conn, rps, distr, experiment_name, "8001", None, dir_name, barrier)))
                        py_threads.append(threading.Thread(target=experimentutils.read_client_tcpdump, args=(user, client_hostname, server_one_hostname, dir_name, barrier)))
                        py_threads.append(threading.Thread(target=experimentutils.read_server_cpu_utilization, args=(user, dir_name, server_one_hostname, "main", barrier)))

                        for py_thread in py_threads:
                            py_thread.start()
                        # Signal the threads to begin
                        barrier.wait()
                        for py_thread in py_threads:
                            py_thread.join()
                        time.sleep(5) 

if __name__ == "__main__":
    client_hostname = None
    server_one_hostname = None
    server_two_hostname = None
    loadgen = None
    user = None

    try:
        opts, args = getopt.getopt(sys.argv[1:],"c:s:u:g",["client=","server=","user=","loadgen="])
    except getopt.GetoptError:
        print('experiment5.py -c <client-hostname> -s <server-hostname>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-c':
            client_hostname = arg
        elif opt == '-s':
            server_one_hostname = arg
        elif opt == '-g':
            loadgen = arg
        elif opt == '-u':
            user = arg
        else:
            print('experiment11.py -c <client-hostname> -s <server-hostname> -g <load-generator> -u <username>')
            sys.exit(2)

    install_servers(user, server_one_hostname)
    if loadgen == "wrk2":
        experimentutils.install_wrk2(client_hostname, user)
        run_wrk2(client_hostname, server_one_hostname, server_two_hostname, experiment_name="experiment11", user=user)
    elif loadgen == "wrk2-dsb":
        experimentutils.install_wrk2_dsb(client_hostname, user)
        run_wrk2_dsb(client_hostname, server_one_hostname, server_two_hostname, experiment_name="experiment11", user=user)
    else:
        # Run all here
        experimentutils.install_wrk2(client_hostname, user)
        run_wrk2(client_hostname, server_one_hostname, experiment_name="experiment11", user=user)
        experimentutils.install_wrk2_dsb(client_hostname, user)
        run_wrk2_dsb(client_hostname, server_one_hostname, experiment_name="experiment11", user=user)
    # TODO: Create installation for other load generators