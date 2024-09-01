import getopt
import sys
import time
import itertools
import paramiko
import threading

conn_counts = [10, 20, 25, 50, 100, 200, 500, 1000, 10000]
thread_counts = [1, 2, 4, 8, 10, 12, 16, 24]
rps_counts = [100, 200, 500, 1000, 2000, 5000, 10000, 20000, 50000, 100000]


# DATA_DIR = "data-wrk2-dsb-multimachine"
# WRK = "DeathStarBench/wrk2/wrk"
DATA_DIR = "data-wrk2"
WRK = "../wrk2/wrk"

def read_wrk_cpu_utilization(machine_name:str, thread_count: int, conn_count: int):
    file_to_write = open(f"{DATA_DIR}/t{thread_count}-c{conn_count}/cpu_utils/cpu-util.csv","w")
    file_to_write.write("PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND\n")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(machine_name, username="yugm2")
    for i in range(60):
        stdin, stdout, stderr = ssh_con.exec_command(f"top -b -n1 | grep wrk")
        file_to_write.write(stdout.read().decode("utf-8")[2:])
        # print(stderr.read())
        time.sleep(1)
    file_to_write.close()

def read_server_cpu_utilization(server_machine_name:str, machine_thread_count:int, machine_conn_count:int, rps:int):
    file_to_write = open(f"{DATA_DIR}/server_cpu_utils/cpu-util.csv","w")
    file_to_write.write("CONTAINER ID   NAME      CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS\n")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_machine_name, username="yugm2")
    for i in range(60):
        stdin, stdout, stderr = ssh_con.exec_command(f"top -b -n1 | grep serverone")
        file_to_write.write(stdout.read().decode("utf-8"))
        time.sleep(1)
    file_to_write.close()

def run_wrk2_on_client_machine(client_machine_name:str, server_machine_name:str, thread_count: int, conn_count: int, machine_rps:int):
    cmd = f"{WRK} -t{thread_count} -c{conn_count} -d60s -R{machine_rps} --latency " + server_machine_name
    file_to_write = open(f"{DATA_DIR}/t{thread_count}-c{conn_count}/results/wrk2_results.csv","w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_machine_name, username="yugm2")
    stdin, stdout, stderr = ssh_con.exec_command(cmd)
    print(client_machine_name, ":",str(stderr.read()))
    file_to_write.write(stdout.read().decode("utf-8"))
    file_to_write.close()

def read_client_tcpdump(client_hostname:str, server_machine_name: str, thread_count: int, conn_count: int,):
    cmd = "python3 tcpdumpreader.py " + server_machine_name
    file_to_write = open(f"{DATA_DIR}/t{thread_count}-c{conn_count}/client_tcpdump/{client_hostname}-t{thread_count}-c{conn_count}.csv","w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_hostname, username="yugm2")
    stdin, stdout, stderr = ssh_con.exec_command(cmd)
    print(client_hostname, ":",str(stderr.read()))
    file_to_write.write(stdout.read().decode("utf-8"))
    file_to_write.close()

def run_wrk2(client_hostname:str, server_machine_name: str):
    configs = itertools.product(conn_counts, thread_counts)
    for rps in rps_counts:
        for i, (conn, thread) in enumerate(configs): 
            py_threads = []
            py_threads.append(threading.Thread(target=read_wrk_cpu_utilization, args=(client_hostname, thread, conn, rps)))
            py_threads.append(threading.Thread(target=read_server_cpu_utilization, args=(server_machine_name, thread, conn, rps)))
            py_threads.append(threading.Thread(target=run_wrk2_on_client_machine, args=(client_hostname, server_machine_name, thread, conn, rps)))
            py_threads.append(threading.Thread(target=read_client_tcpdump, args=(client_hostname, server_machine_name, thread, conn, rps)))

            for py_thread in py_threads:
                py_thread.start()
            for py_thread in py_threads:
                py_thread.join()
            time.sleep(5) 

def run_server(server_machine_name:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_machine_name, username="yugm2")
    ssh_con.exec_command("git clone https://github.com/mittal1787/are-we-really-load-generating.git")
    ssh_con.exec_command("cd are-we-really-load-generating/new-experiments/experiment1")
    ssh_con.exec_command("sh install.sh")
    for i in range(4):
        ssh_con.write("Y\n")
        ssh_con.flush()
    ssh_con.exec_command("go run main.go")

def install_wrk2(client_hostname:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_hostname, username="yugm2")
    ssh_con.exec_command("git clone https://github.com/mittal1787/are-we-really-load-generating.git")
    ssh_con.exec_command("cd are-we-really-load-generating/new-experiments")
    ssh_con.exec_command("sh install_wrk2.sh")
    ssh_con.write("Y\n")
    ssh_con.flush()


if __name__ == "__main__":
    client_hostname = None
    server_hostname = None
    loadgen = None

    try:
        opts, args = getopt.getopt(sys.argv[1:],"c:s:g",["client=","server=","loadgen="])
    except getopt.GetoptError:
        print('experiment1.py -c <client-hostname> -s <server-hostname> -g <load-generator>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-c':
            client_hostname = arg
        elif opt == '-s':
            server_hostname = arg
        elif opt == '-g':
            loadgen = arg

    run_server(server_hostname)
    if loadgen == "wrk2":
        install_wrk2(client_hostname)
        run_wrk2(client_hostname, server_hostname)
    else:
        # Run all here
        install_wrk2(client_hostname)
        run_wrk2(client_hostname, server_hostname)
    # TODO: Create installation for other load generators