
import os
import subprocess
import time
import itertools
import paramiko
import threading

conn_counts = [1, 2, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 100, 150, 200, 300, 400, 500, 1000, 2000, 5000, 10000]
thread_counts = [1, 2, 3, 4, 5, 10, 15, 20, 25, 30, 40, 50, 100, 200]
machines = []
with open("machines", 'r') as f:
    i = 0
    for vm_name in f:
        machines.append(vm_name.strip())


# DATA_DIR = "data-wrk2-dsb-multimachine"
# WRK = "DeathStarBench/wrk2/wrk"
DATA_DIR = "data-wrk2-multimachine"
WRK = "../wrk2/wrk"

def read_wrk_cpu_utilization(machine_name:str, machine_count:int, thread_count: int, conn_count: int, machine_thread_count:int, machine_conn_count:int):
    file_to_write = open(f"{DATA_DIR}/m{machine_count}-t{thread_count}-c{conn_count}/cpu_utils/{machine_name}-t{machine_thread_count}-c{machine_conn_count}-cpu-util.csv","w")
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

def run_wrk2_on_machine(machine_name:str, machine_count:int, thread_count: int, conn_count: int, machine_thread_count:int, machine_conn_count:int, machine_rps:int):
    cmd = f"{WRK} -t{machine_thread_count} -c{machine_conn_count} -d30s -R{machine_rps} --latency http://clnode028.clemson.cloudlab.us"
    file_to_write = open(f"{DATA_DIR}/m{machine_count}-t{thread_count}-c{conn_count}/wrk2_results/{machine_name}-t{thread_count}-c{conn_count}.csv","w")
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(machine_name, username="yugm2")
    stdin, stdout, stderr = ssh_con.exec_command(cmd)
    print(machine_name, ":",str(stderr.read()))
    file_to_write.write(stdout.read().decode("utf-8"))
    file_to_write.close()


def even_distribution(rps: int, machine_count: int, thread_count: int, conn_count: int):
    rps_per_machine = [rps//machine_count for _ in range(machine_count)]
    for i in range(rps % machine_count):
        rps_per_machine[i] += 1
    thread_per_machine = [thread_count//machine_count for _ in range(machine_count)]
    for i in range(thread_count % machine_count):
        thread_per_machine[i] += 1
    conn_per_machine = [conn_count//machine_count for _ in range(machine_count)]
    for i in range(conn_count % machine_count):
        conn_per_machine[i] += 1
    return rps_per_machine, thread_per_machine, conn_per_machine



def run_trial(thread_count: int, conn_count: int):
    cmd = f"{WRK} -t{thread_count} -c{conn_count} -d30s -R1000000 --latency http://c220g5-110905.wisc.cloudlab.us"
    print(cmd)
    res = subprocess.run(cmd.split(" "), capture_output=True)
    with open(f"{DATA_DIR}/t{thread_count}-c{conn_count}.txt", "w+") as f:
        f.write(res.stdout.decode('utf-8'))
    

# os.makedirs(DATA_DIR, exist_ok=True)

configs = itertools.product(conn_counts, thread_counts)
rps = 1000000

for j in range(3,len(machines)):
    for i, (conn, thread) in enumerate(configs):
        machine_count = j+1 
        if machine_count > thread or thread > conn or machine_count > conn:
            print(f"Requirements not met for t{thread}, c{conn}, and m{machine_count}")
        else:
            print(f"Requirements met for t{thread}, c{conn}, and m{machine_count}")
            os.makedirs(f"{DATA_DIR}/m{machine_count}-t{thread}-c{conn}", exist_ok=True)
            os.makedirs(f"{DATA_DIR}/m{machine_count}-t{thread}-c{conn}/cpu_utils", exist_ok=True)
            os.makedirs(f"{DATA_DIR}/m{machine_count}-t{thread}-c{conn}/wrk2_results", exist_ok=True)
            machines_to_read = [machines[k] for k in range(machine_count)]
            rps_per_machine, thread_per_machine, conn_per_machine = even_distribution(rps=rps, machine_count=machine_count, thread_count=thread, conn_count=conn)
            py_threads = []
            for k in range(machine_count):
                py_threads.append(threading.Thread(target=read_wrk_cpu_utilization, args=(machines_to_read[k],machine_count, thread, conn, thread_per_machine[k], conn_per_machine[k],)))
                py_threads.append(threading.Thread(target=run_wrk2_on_machine, args=(machines_to_read[k],machine_count, thread, conn, thread_per_machine[k], conn_per_machine[k], rps_per_machine[k],)))
            for py_thread in py_threads:
                py_thread.start()
            for py_thread in py_threads:
                py_thread.join()
            time.sleep(5)

# with open("out.csv", "w+") as f:
#     f.write(f"conn,thread,RPS\n")
# 
# configs = itertools.product(conn_counts, thread_counts)
# for i, (conn, thread) in enumerate(configs):
#     res = run_trial(thread, conn)
#     with open("out.csv", "a+") as f:
#         f.write(f"{conn},{thread},res\n")
