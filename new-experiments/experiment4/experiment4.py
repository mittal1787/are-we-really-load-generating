import getopt
import sys
import paramiko
from ..common import experimentutils

def install_server(server_machine_name:str, username):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_machine_name, username=username)
    stdin, stdout, stderr = ssh_con.exec_command("git clone https://github.com/mittal1787/are-we-really-load-generating.git && cd are-we-really-load-generating && git pull origin main")
    stdin, stdout, stderr = ssh_con.exec_command("cd are-we-really-load-generating/new-experiments/experiment4 && sh install.sh")
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
    user = None

    try:
        opts, args = getopt.getopt(sys.argv[1:],"u:c:s:g",["username=","client=","server=","loadgen="])
    except getopt.GetoptError:
        print('experiment4.py -c <client-hostname> -s <server-hostname> -g <load-generator> -u <username>')
        print("OR")
        print('experiment4.py -c <client-hostname> -s <server-hostname> -u <username>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-c':
            client_hostname = arg
        elif opt == '-s':
            server_hostname = arg
        elif opt == '-g':
            loadgen = arg
        elif opt == '-u':
            user = arg
        else:
            print('experiment4.py -c <client-hostname> -s <server-hostname> -g <load-generator> -u <username>')
            sys.exit(2)

    install_server(server_hostname, user)
    if loadgen == "wrk2":
        experimentutils.install_wrk2(client_hostname, user)
        experimentutils.run_wrk2(client_hostname, server_hostname, "experiment4", "are_we_really_load_generating/new_experiments/experiment4/requests.lua", user)
    elif loadgen == "wrk2-dsb":
        experimentutils.install_wrk2_dsb(client_hostname, user)
        experimentutils.run_wrk2_dsb(client_hostname, server_hostname, "experiment4", "are_we_really_load_generating/new_experiments/experiment4/requests.lua", ssh_user=user)
    else:
        # Run all here
        experimentutils.install_wrk2(client_hostname, user)
        experimentutils.run_wrk2(client_hostname, server_hostname, "experiment4", "are_we_really_load_generating/new_experiments/experiment4/requests.lua", user)
        experimentutils.install_wrk2_dsb(client_hostname, user)
        experimentutils.run_wrk2_dsb(client_hostname, server_hostname, "experiment4", "are_we_really_load_generating/new_experiments/experiment4/requests.lua", ssh_user=user)
    # TODO: Create installation for other load generators