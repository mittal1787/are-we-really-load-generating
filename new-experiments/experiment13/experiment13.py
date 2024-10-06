from scp import SCPClient
import getopt
import itertools
import os
import re
import sys
import threading
import paramiko
import time
from ..common import experimentutils

conn_counts = [1, 10, 20, 25, 50, 100, 200, 500, 1000, 2000]
thread_counts = [1, 2, 4, 8, 10, 12, 16, 24]
rps_counts = [1, 10, 50, 100, 200, 500, 1000, 2000, 5000, 10000]
preallocated_vu_counts = [1, 10, 20, 50, 100, 1000, 2000, 5000, 10000, 20000, 25000, 50000]
max_vu_counts = [1,10,20,50,100,1000,2000,5000,10000,20000,25000,50000,100000,200000]

DATA_DIR = "data-wrk2"
DATA_DIR_DSB = "data-wrk2-dsb"
DATA_DIR_K6 = "data-k6"

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
    ssh_con.exec_command("openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes -subj \"/CN=localhost\"")
    ssh_con.load_system_host_keys()

def run_server(user:str, server_one: str, duration:str, dir_name:str, barrier):
    filename = f"{dir_name}/server_arrival_times.csv"
    file_to_write = open(filename,"w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_one, username=user)
    stdin, stdout, stderr = ssh_con.exec_command("sudo lsof -i -P -n | grep *:8001")
    str_data = re.sub(' +', ' ',stdout.read().decode())
    print("run_server:", str_data)
    if len(str_data) > 0:
        stdin, stdout, stderr = ssh_con.exec_command(f"kill {int(str_data.split()[1])}")
    stdin, stdout, stderr = ssh_con.exec_command(f"go run are-we-really-load-generating/new-experiments/experiment11/main.go {duration} > timestamp.txt")
    time.sleep(1)
    print("run_server: begin barrier wait")
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

def run_wrk2_on_client_machine(ssh_user:str, client_machine_name:str, server_machine_name:str, thread_count: int, conn_count: int, machine_rps:int, port:str, lua_script_path, dir_name, barrier):
    wrk = "./are-we-really-load-generating/new-experiments/wrk2/wrk"
    cmd = f"{wrk} -t{thread_count} -c{conn_count} -d60s -R{machine_rps} --latency https://" + server_machine_name + ":" + port
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

def run_wrk2(client_hostname:str, server_one_hostname: str, experiment_name: str, user: str):
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR}", exist_ok=True)
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR}/client={client_hostname}-server_one={server_one_hostname}-server_two={server_two_hostname}", exist_ok=True)
    configs = itertools.product(conn_counts, thread_counts)
    for rps in rps_counts:
        for i, (conn, thread) in enumerate(configs):
            for duration in ['1s','5s','10s','30s','45s','1m']:
                if conn >= thread:
                    print(f"RPS = {rps}, Connections = {conn}, Thread = {thread}, duration = {duration}")
                    dir_name = f"new-experiments/{experiment_name}/{DATA_DIR}/client={client_hostname}-server={server_one_hostname}/t{thread}-c{conn}-rps{rps}-{duration}"
                    os.makedirs(dir_name, exist_ok=True)
                    barrier = threading.Barrier(6)
                    py_threads = []
                    py_threads.append(threading.Thread(target=run_server, args=(user, server_one_hostname, duration, dir_name, barrier)))
                    py_threads.append(threading.Thread(target=experimentutils.read_wrk_cpu_utilization, args=(user, client_hostname, dir_name, barrier)))
                    py_threads.append(threading.Thread(target=run_wrk2_on_client_machine, args=(user, client_hostname, server_one_hostname, thread, conn, rps, "8000", None, dir_name, barrier)))
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

def run_wrk2_dsb_on_client_machine(ssh_user:str, client_machine_name:str, server_machine_name:str, thread_count: int, conn_count: int, machine_rps:int, distribution_type:str, port:str, lua_script_path, dir_name, barrier):
    wrk = "are-we-really-load-generating/new-experiments/DeathStarBench/wrk2/wrk"
    cmd = f"{wrk} -t{thread_count} -c{conn_count} -d60s -R{machine_rps} -D {distribution_type} --requests --latency https://" + server_machine_name + ":" + port
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

def run_wrk2_dsb(client_hostname:str, server_one_hostname: str, experiment_name: str, user: str):
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR_DSB}", exist_ok=True)
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR_DSB}/client={client_hostname}-server_one={server_one_hostname}", exist_ok=True)
    configs = itertools.product(conn_counts, thread_counts)
    for rps in rps_counts:
        for i, (conn, thread) in enumerate(configs):
            for duration in ['1s','5s','10s','30s','45s','1m']:
                if conn >= thread:
                    for distr in ["fixed","exp","zipf","norm"]:
                        print(f"RPS = {rps}, Connections = {conn}, Thread = {thread}, Distribution = {distr}, Duration = {duration}")
                        dir_name = f"new-experiments/{experiment_name}/{DATA_DIR_DSB}/client={client_hostname}-server_one={server_one_hostname}/t{thread}-c{conn}-rps{rps}-dist{distr}-{duration}"
                        os.makedirs(dir_name, exist_ok=True)
                        barrier = threading.Barrier(6)
                        py_threads = []
                        py_threads.append(threading.Thread(target=run_server, args=(user, server_one_hostname, duration, dir_name, barrier)))
                        py_threads.append(threading.Thread(target=experimentutils.read_wrk_cpu_utilization, args=(user, client_hostname, dir_name, barrier)))
                        py_threads.append(threading.Thread(target=run_wrk2_dsb_on_client_machine, args=(user, client_hostname, server_one_hostname, thread, conn, rps, distr, "8001", None, dir_name, barrier)))
                        py_threads.append(threading.Thread(target=experimentutils.read_client_tcpdump, args=(user, client_hostname, server_one_hostname, dir_name, barrier)))
                        py_threads.append(threading.Thread(target=experimentutils.read_server_cpu_utilization, args=(user, dir_name, server_one_hostname, "main", barrier)))

                        for py_thread in py_threads:
                            py_thread.start()
                        # Signal the threads to begin
                        barrier.wait()
                        
                        for py_thread in py_threads:
                            py_thread.join()

                        time.sleep(5) 

def create_k6_constant_arrival_script_file(rate:int, preallocated_vus:int, max_vus:int, server_hostname:str, port:str):
    return """
    import http from 'k6/http';
    
    export const options = {
        scenarios: {
            open_model: {
            executor: 'constant-arrival-rate',
            rate:""" + str(rate) + """,
            timeUnit: '1s',
            duration: '1m',
            preAllocatedVUs:""" + str(preallocated_vus) + """ ,
            maxVUs:""" + str(max_vus) + """
            },
        },
    };

    export default function() {
        http.get('http://""" + server_hostname + ":" + port +  """');
    }
    """

def run_k6_on_client_machine(ssh_user:str, client_hostname:str, server_hostname:str, port:str, rate:int, preallocated_vus:int, max_vus:int, dir_name:str, barrier):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
    ssh_con.connect(client_hostname, username=ssh_user)
    scp = SCPClient(ssh_con.get_transport())
    script_file = open(f"{dir_name}/script.js", "w")
    script_file.write(create_k6_constant_arrival_script_file(rate, preallocated_vus, max_vus, server_hostname, port))
    script_file.close()
    scp.put(f"{dir_name}/script.js","script.js")
    barrier.wait()
    stdin, stdout, stderr = ssh_con.exec_command("k6 run --insecure-skip-tls-verify --out json=test_results.json script.js", timeout=120)
    file_to_write = open(f"{dir_name}/k6_results.txt","w")
    file_to_write.write(stdout.read().decode("utf-8"))
    file_to_write.close()
    scp.get("test_results.json", f"{dir_name}/k6_results.json")
    scp.close()
    ssh_con.close()

def run_k6(client_hostname:str, server_one_hostname: str, experiment_name: str, user:str):
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR_K6}", exist_ok=True)
    os.makedirs(f"new-experiments/{experiment_name}/{DATA_DIR_K6}/client={client_hostname}-server={server_one_hostname}", exist_ok=True)
    for rps in rps_counts:
        for duration in ['1s','5s','10s','30s','45s','1m']:
            print(f"RPS = {rps}, Duration = {duration}")
            dir_name = f"new-experiments/{experiment_name}/{DATA_DIR_K6}/client={client_hostname}-server={server_one_hostname}/rps{rps}-{duration}"
            os.makedirs(dir_name, exist_ok=True)
            barrier = threading.Barrier(6)
            py_threads = []
            py_threads.append(threading.Thread(target=run_server, args=(user, server_one_hostname, duration, dir_name, barrier)))
            py_threads.append(threading.Thread(target=experimentutils.read_k6_cpu_utilization, args=(user, client_hostname, dir_name, barrier)))
            py_threads.append(threading.Thread(target=run_k6_on_client_machine, args=(user, client_hostname, server_one_hostname, "8001", rps, dir_name, barrier)))
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
        opts, args = getopt.getopt(sys.argv[1:],"c:s:u:g:",["client=","server=","user=","loadgen="])
    except getopt.GetoptError:
        print('experiment11.py -c <client-hostname> -s <server-hostname>')
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
    print("loadgen = ", loadgen)
    install_servers(user, server_one_hostname)
    if loadgen == "wrk2":
        experimentutils.install_wrk2(client_hostname, user)
        run_wrk2(client_hostname, server_one_hostname, experiment_name="experiment13", user=user)
    elif loadgen == "wrk2-dsb":
        experimentutils.install_wrk2_dsb(client_hostname, user)
        run_wrk2_dsb(client_hostname, server_one_hostname, experiment_name="experiment13", user=user)
    elif loadgen == "k6":
        experimentutils.install_k6(client_hostname, user)
        run_k6(client_hostname, server_one_hostname, experiment_name="experiment13", user=user)
    else:
        # Run all here
        experimentutils.install_wrk2(client_hostname, user)
        run_wrk2(client_hostname, server_one_hostname, experiment_name="experiment13", user=user)
        experimentutils.install_wrk2_dsb(client_hostname, user)
        run_wrk2_dsb(client_hostname, server_one_hostname, experiment_name="experiment13", user=user)
    # TODO: Create installation for other load generators