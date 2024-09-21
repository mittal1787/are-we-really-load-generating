import getopt
import itertools
import os
import re
import sys
import threading
import paramiko
import time
from ..common import experimentutils

conn_counts = [10, 20, 25, 50, 100, 200, 500, 1000, 2000]
thread_counts = [1, 2, 4, 8, 10, 12, 16, 24]
rps_counts = [500, 1000, 2000, 5000, 10000]

DATA_DIR = "data-wrk2"
DATA_DIR_DSB = "data-wrk2-dsb"
DATA_DIR_K6 = "data-k6"

def install_server(user:str, server_name:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_name, username=user)
    stdin, stdout, stderr = ssh_con.exec_command("git clone https://github.com/mittal1787/are-we-really-load-generating.git ; cd are-we-really-load-generating ; git pull origin main ; sh new-experiments/experiment11/install.sh")
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
    install_server(user, server_one_hostname)
    if loadgen == "wrk2":
        experimentutils.install_wrk2(client_hostname, user)
        experimentutils.run_wrk2(client_hostname, server_one_hostname, experiment_name="experiment12", user=user)
    elif loadgen == "wrk2-dsb":
        experimentutils.install_wrk2_dsb(client_hostname, user)
        experimentutils.run_wrk2_dsb(client_hostname, server_one_hostname, experiment_name="experiment12", user=user)
    elif loadgen == "k6":
        experimentutils.install_k6(client_hostname, user)
        experimentutils.run_k6(client_hostname, server_one_hostname, experiment_name="experiment12", user=user)
    else:
        # Run all here
        experimentutils.install_wrk2(client_hostname, user)
        experimentutils.run_wrk2(client_hostname, server_one_hostname, experiment_name="experiment12", user=user)
        experimentutils.install_wrk2_dsb(client_hostname, user)
        experimentutils.run_wrk2_dsb(client_hostname, server_one_hostname, experiment_name="experiment12", user=user)
        experimentutils.install_k6(client_hostname, user)
        experimentutils.run_k6(client_hostname, server_one_hostname, experiment_name="experiment12", user=user)
    # TODO: Create installation for other load generators