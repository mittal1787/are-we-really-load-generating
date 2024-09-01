import getopt
import sys
import paramiko
from ..common import experimentutils

sys.path.insert(0, '../common')

def install_server(server_machine_name:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_machine_name, username="yugm2")
    stdin, stdout, stderr = ssh_con.exec_command("git clone https://github.com/mittal1787/are-we-really-load-generating.git && cd are-we-really-load-generating && git pull origin main")
    stdin, stdout, stderr = ssh_con.exec_command("cd new-experiments/experiment1 && sh install.sh")
    for i in range(4):
        try:
            stdin.write("Y\n")
            stdin.flush()
        except OSError:
            pass
    print(str(stderr.read()))
    print(str(stdout.read()))


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

    install_server(server_hostname)
    if loadgen == "wrk2":
        experimentutils.install_wrk2(client_hostname)
        experimentutils.run_wrk2(client_hostname, server_hostname, "experiment1")
    else:
        # Run all here
        experimentutils.install_wrk2(client_hostname)
        experimentutils.run_wrk2(client_hostname, server_hostname, "experiment1")
    # TODO: Create installation for other load generators