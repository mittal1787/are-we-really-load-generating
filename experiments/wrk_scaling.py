import os
import subprocess
import time
import itertools
import paramiko
import threading

conn_counts = [1, 2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 100, 150, 200, 300, 400, 500, 1000, 2000, 5000, 10000]
thread_counts = [1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 40, 50, 100, 200]
rps_counts = [10, 50, 100, 200, 500, 1000,1500,2000,2500,3000,4000,4500,5000,7500,10000,20000,25000,30000,40000,45000,50000,75000,100000]
machines = ["sp24-cs525-0301.cs.illinois.edu"]

DATA_DIR = "data-wrk2-config-data"
WRK = "../wrk2/wrk"

def read_wrk_cpu_utilization(machine_name:str, machine_thread_count:int, machine_conn_count:int, rps:int):
    file_to_write = open(f"{DATA_DIR}/cpu_utils/t{machine_thread_count}-c{machine_conn_count}-rps{rps}-cpu-util.csv","w")
    file_to_write.write("PID USER      PR  NI    VIRT    RES    SHR S  %CPU  %MEM     TIME+ COMMAND\n")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(machine_name, username="yugm2")
    for i in range(30):
        stdin, stdout, stderr = ssh_con.exec_command(f"top -b -n1 | grep wrk")
        file_to_write.write(stdout.read().decode("utf-8")[2:])
        # print(stderr.read())
        time.sleep(1)
    file_to_write.close()

def read_server_cpu_utilization(machine_name:str, machine_thread_count:int, machine_conn_count:int, rps:int):
    file_to_write = open(f"{DATA_DIR}/server_cpu_utils/t{machine_thread_count}-c{machine_conn_count}-rps{rps}-server-cpu-util.csv","w")
    file_to_write.write("CONTAINER ID   NAME      CPU %     MEM USAGE / LIMIT     MEM %     NET I/O           BLOCK I/O         PIDS\n")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(machine_name, username="yugm2")
    for i in range(30):
        stdin, stdout, stderr = ssh_con.exec_command(f"docker stats --no-stream | grep web")
        file_to_write.write(stdout.read().decode("utf-8"))
        # print(stderr.read())
        time.sleep(1)
    file_to_write.close()
    
def run_wrk2_on_machine(machine_name:str, machine_thread_count:int, machine_conn_count:int, machine_rps:int):
    cmd = f"{WRK} -t{machine_thread_count} -c{machine_conn_count} -d30s -R{machine_rps} --latency http://sp24-cs525-0302.cs.illinois.edu"
    file_to_write = open(f"{DATA_DIR}/wrk2_results/t{machine_thread_count}-c{machine_conn_count}.csv","w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(machine_name, username="yugm2")
    stdin, stdout, stderr = ssh_con.exec_command(cmd)
    print(machine_name, ":",str(stderr.read()))
    file_to_write.write(stdout.read().decode("utf-8"))
    file_to_write.close()



def run_trial(thread_count: int, conn_count: int, rps_count: int):
    cmd = f"{WRK} -t{thread_count} -c{conn_count} -d30s -R{rps_count} --latency http://sp24-cs525-0302.cs.illinois.edu"
    print(cmd)
    res = subprocess.run(cmd.split(" "), capture_output=True)
    with open(f"{DATA_DIR}/t{thread_count}-c{conn_count}-{rps_count}.txt", "w+") as f:
        f.write(res.stdout.decode('utf-8'))
    

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(f"{DATA_DIR}/cpu_utils", exist_ok=True)
os.makedirs(f"{DATA_DIR}/server_cpu_utils", exist_ok=True)
os.makedirs(f"{DATA_DIR}/nginx_server_request_times", exist_ok=True)
os.makedirs(f"{DATA_DIR}/wrk2_results", exist_ok=True)

configs = itertools.product(conn_counts, thread_counts)

for rps in rps_counts:
    for i, (conn, thread) in enumerate(configs): 
        py_threads = []
        py_threads.append(threading.Thread(target=read_wrk_cpu_utilization, args=("sp24-cs525-0301.cs.illinois.edu", thread, conn, rps)))
        py_threads.append(threading.Thread(target=read_server_cpu_utilization, args=("sp24-cs525-0302.cs.illinois.edu", thread, conn, rps)))
        py_threads.append(threading.Thread(target=run_wrk2_on_machine, args=("sp24-cs525-0301.cs.illinois.edu", thread, conn, rps)))

        for py_thread in py_threads:
            py_thread.start()
        for py_thread in py_threads:
            py_thread.join()
        time.sleep(5) 