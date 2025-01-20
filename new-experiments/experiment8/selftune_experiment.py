from scp import SCPClient
import getopt
import itertools
import os
import re
import sys
import threading
import paramiko
import time

def put_vegeta_compose_body_to_client(ssh_user:str, hostname:str, file_path:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
    ssh_con.connect(hostname, username=ssh_user)
    scp = SCPClient(ssh_con.get_transport())
    # scp.put("new-experiments/experiment8/vegeta_compose_body", recursive=True)
    # scp.put("new-experiments/experiment8/vegeta_socialnetwork.txt", "vegeta_socialnetwork.txt")
    scp.put(file_path, "vegeta_socialnetwork.txt")

def run_vegeta_on_client(ssh_user:str, master_hostname:str, other_clients:list, filename:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
    ssh_con.connect(master_hostname, username=ssh_user)
    stdin, stdout, stderr = ssh_con.exec_command("vegeta/vegeta attack -duration=15m -rate=10000 -targets=vegeta_socialnetwork_old.txt | vegeta/vegeta report -type=json")
    file_to_write = open(f"{filename}_vegeta_results.json","w")
    file_to_write.write(stdout.read().decode("utf-8"))
    file_to_write.close()
    # stdin, stdout, stderr = ssh_con.exec_command("vegeta/vegeta attack -duration=15m -rate=1000 -targets=vegeta_socialnetwork.txt | tee results.bin | vegeta/vegeta report -type=json")
    # file_to_write = open(f"{filename}_{master_hostname}_vegeta_results.json","w")
    # other_ssh = []
    # other_stdout = []
    # other_stderr = []
    # for client in other_clients:
    #     ssh_con_o = paramiko.SSHClient()
    #     ssh_con_o.load_system_host_keys()
    #     # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
    #     ssh_con_o.connect(client, username=ssh_user)
    #     stdin, stdout_m, stderr_m = ssh_con_o.exec_command("vegeta/vegeta attack -duration=15m -rate=900 -targets=vegeta_socialnetwork.txt | tee results.bin | vegeta/vegeta report -type=json")
    #     other_ssh.append(ssh_con_o)
    #     other_stdout.append(stdout_m)
    #     other_stderr.append(stderr_m)

    # # print(stderr.read().decode("utf-8"))
    # file_to_write.write(stdout.read().decode("utf-8"))
    # file_to_write.close()

    # for i in range(len(other_clients)):
    #     file_to_write = open(f"{filename}_{other_clients[i]}_vegeta_results.json","w")
    #     file_to_write.write(other_stdout[i].read().decode("utf-8"))
    #     file_to_write.close()
    #     print(other_stderr[i].read().decode("utf-8"))
    
    # for i in range(len(other_clients)):
    #     other_ssh[i].close()
    # ssh_con.close()
    # stdin, stdout, stderr = ssh_con.exec_command("tee results.bin | vegeta/vegeta report -type=hist")
    # file_to_write = open(f"{filename}_vegeta_results_hist.txt","w")
    # print(stderr.read())
    # file_to_write.write(stdout.read().decode("utf-8"))
    # file_to_write.close()
    # stdin, stdout, stderr = ssh_con.exec_command("tee results.bin | vegeta/vegeta report -type=hdrplot")
    # file_to_write = open(f"{filename}_vegeta_results_hdrplot.txt","w")
    # print(stderr.read())
    # file_to_write.write(stdout.read().decode("utf-8"))
    # file_to_write.close()
    # stdin, stdout, stderr = ssh_con.exec_command("tee results.bin | vegeta/vegeta plot")
    # file_to_write = open(f"{filename}_vegeta_results_plot.html","w")
    # # print(stderr.read())
    # file_to_write.write(stdout.read().decode("utf-8"))
    # file_to_write.close()
    # scp = SCPClient(ssh_con.get_transport())
    # scp.get("results.bin", f"{filename}_results.bin")
    




def put_h2load_on_clients(ssh_user:str, master_hostname:str, clients:list):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
    ssh_con.connect(master_hostname, username=ssh_user)
    scp = SCPClient(ssh_con.get_transport())
    scp.put("new-experiments/nghttp2", recursive=True)
    for client in clients:
        ssh_con = paramiko.SSHClient()
        ssh_con.load_system_host_keys()
        # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
        ssh_con.connect(client, username=ssh_user)
        scp = SCPClient(ssh_con.get_transport())
        scp.put("new-experiments/nghttp2", recursive=True)

def run_h2load_on_clients(ssh_user:str, master_hostname:str, clients:list, server_machine_name:str, port:str, filename:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
    ssh_con.connect(master_hostname, username=ssh_user)
    scp = SCPClient(ssh_con.get_transport())
    scp.put("new-experiments/experiment8/nghttp2_socialnetwork.txt", "nghttp2_socialnetwork.txt")
    cmd = f"nghttp2/src/h2load -t 10 -c 90 --rps=100 --duration={60*15} --warm-up-time=30 --h1 --log-file=logs.log -i nghttp2_socialnetwork.txt"
    # cmd = f"nghttp2/src/h2load -t 1 -c 1 --rps=1 --duration={60*15} --warm-up-time=30 --h1 --log-file=logs.log \"http://c220g2-030832.wisc.cloudlab.us:31565/wrk2-api/home-timeline/read?user_id=913&start=61&stop=71\""
    stdin, stdout, stderr =  ssh_con.exec_command("tail nghttp2_socialnetwork.txt")
    print(stdout.read())
    stdin, stdout, stderr =  ssh_con.exec_command("curl http://c220g2-030832.wisc.cloudlab.us:31565/wrk2-api/home-timeline/read?user_id=913&start=61&stop=71")
    # print(stderr.read())
    # print(stdout.read())
    print(cmd)
    # time.sleep(120)
    stdin, stdout, stderr =  ssh_con.exec_command(cmd)
    # print(stderr.read())
    ssh_con_other_clients = []
    std_outs = []
    scp_clients = []
    data_num = 0
    for client in clients:
        for i in range(10):
            ssh_con_c = paramiko.SSHClient()
            ssh_con_c.load_system_host_keys()
            # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
            ssh_con_c.connect(client, username=ssh_user)
            new_scp = SCPClient(ssh_con_c.get_transport())
            print(f"nghttp2/src/h2load -t 1 -c 10 --rps=1 --h1 --duration={60*15} --log-file=logs_{i}.log -d data_{data_num}.txt -H 'Content-Type: application/x-www-form-urlencoded' \"http://{server_machine_name}:{port}/wrk2-api/post/compose\"")
            new_scp.put(f"new-experiments/experiment8/h2load_compose_body/data_{data_num}.txt", f"data_{data_num}.txt")
            _, stdout_c, stderr = ssh_con_c.exec_command(f"nghttp2/src/h2load -t 1 -c 10 --rps=1 --h1 --duration={60*15} --log-file=logs_{i}.log -d data_{data_num}.txt -H 'Content-Type: application/x-www-form-urlencoded' \"http://{server_machine_name}:{port}/wrk2-api/post/compose\"")
            # print(f"nghttp2/src/h2load -t 1 -c 10 --rps=1 --h1 --duration={60*15} --log-file=logs_{i}.log -d data_{data_num}.json -H 'Content-Type: application/x-www-form-urlencoded' \"http://{server_machine_name}:{port}/wrk2-api/post/compose\"")
            # new_scp.put(f"new-experiments/experiment8/h2load_compose_body/data_{data_num}.json", f"data_{data_num}.json")
            # _, stdout_c, stderr = ssh_con_c.exec_command(f"nghttp2/src/h2load -t 1 -c 10 --rps=1 --h1 --duration={60*15} --log-file=logs_{i}.log -d data_{data_num}.json -H 'Content-Type: application/x-www-form-urlencoded' \"http://{server_machine_name}:{port}/wrk2-api/post/compose\"")
            # print(stderr.read())
            data_num += 1
            ssh_con_other_clients.append(ssh_con_c)
            std_outs.append(stdout_c)
            # scp_clients.append(new_scp)
        # scp = SCPClient(ssh_con.get_transport())
    file_to_write = open(f"{filename}_h2load_GET_results.txt","w")
    # print(stderr.read())
    file_to_write.write(stdout.read().decode("utf-8"))
    file_to_write.close() 
    # scp.get(f"logs.log", f"{filename}_GET_logs.log")
    for j in range(len(clients)):
        for i in range(10):
            file_to_write = open(f"{filename}_{clients[j]}_h2load_compose_post_{i}_results.txt","w")
            # print(stderr.read())
            file_to_write.write(std_outs[10*j + i].read().decode("utf-8"))
            file_to_write.close()
            # scp_clients[10*j + i].get(f"logs_{i}.log", f"{filename}_{clients[j]}_compose_post_logs_{i}.log")
        for i in range(10):    
            ssh_con_other_clients[10*j + i].close()


def put_locustfile_on_clients(ssh_user:str, master_hostname:str, clients:list):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
    ssh_con.connect(master_hostname, username=ssh_user)
    scp = SCPClient(ssh_con.get_transport())
    scp.put("new-experiments/experiment8/socialnetworklocustfile.py","socialnetworklocustfile.py")
    scp.put("new-experiments/experiment8/base64_images", recursive=True)
    for client in clients:
        ssh_con = paramiko.SSHClient()
        ssh_con.load_system_host_keys()
        # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
        ssh_con.connect(client, username=ssh_user)
        scp = SCPClient(ssh_con.get_transport())
        scp.put("new-experiments/experiment8/socialnetworklocustfile.py","socialnetworklocustfile.py")
        scp.put("new-experiments/experiment8/base64_images", recursive=True)

def kill_locust(ssh_user:str, master_hostname:str, clients:list):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
    ssh_con.connect(master_hostname, username=ssh_user)
    ssh_con.exec_command("killall locust")
    for client in clients:
        ssh_con = paramiko.SSHClient()
        ssh_con.load_system_host_keys()
        # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
        ssh_con.connect(client, username=ssh_user)
        ssh_con.exec_command("killall locust")

def run_locust_on_client_machines(ssh_user:str, master_hostname:str, clients:list, server_machine_name:str, port:str, filename:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
    ssh_con.connect(master_hostname, username=ssh_user)
    ssh_con.exec_command("killall locust")
    # 10000 users, 1 RPS per user
    # cmd = f"locust -f socialnetworklocustfile.py -H http://{server_machine_name}:{port} --headless --master --expect-workers 100 --users 10000 -r 10000 -t 15m --csv rundata"
    # 5000 users, 2 RPS per user
    # cmd = f"locust -f socialnetworklocustfile.py -H http://{server_machine_name}:{port} --headless --master --expect-workers 100 --users 5000 -r 5000 -t 15m --csv rundata"
    # 20000 users, 0.5 RPS per user
    cmd = f"locust -f socialnetworklocustfile.py -H http://{server_machine_name}:{port} --headless --master --expect-workers 100 --users 20000 -r 10000 -t 15m --csv rundata"
    print(cmd)
    stdin, stdout, stderr = ssh_con.exec_command(cmd)
    ssh_con_2 = paramiko.SSHClient()
    ssh_con_2.load_system_host_keys()
    # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
    ssh_con_2.connect(master_hostname, username=ssh_user)
    ssh_con_2.exec_command(f"locust -f socialnetworklocustfile.py --worker --processes 10")
    for client in clients:
        ssh_con_3 = paramiko.SSHClient()
        ssh_con_3.load_system_host_keys()
        # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
        ssh_con_3.connect(client, username=ssh_user)
        ssh_con_3.exec_command("killall locust")
        stdin3, stdout3, stderr3 = ssh_con_3.exec_command(f"locust -f socialnetworklocustfile.py --worker --processes 10 --master-host {master_hostname}")
        # print(f"Read err of {client}")
        # print(stderr3.read())
    file_to_write = open(f"{filename}_locust_results.txt","w")
    # print(stderr.read())
    file_to_write.write(stdout.read().decode("utf-8"))
    file_to_write.close()
    scp = SCPClient(ssh_con.get_transport())
    scp.get(f"rundata_stats.csv", f"{filename}_stats.csv")
    scp.get(f"rundata_stats_history.csv", f"{filename}_stats_history.csv")
    scp.get(f"rundata_failures.csv", f"{filename}_failures.csv")
    ssh_con.close()


def run_k6_on_client_machine(ssh_user:str, client_hostname:str, port:str, filename:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
    ssh_con.connect(client_hostname, username=ssh_user)
    stdin, stdout, stderr = ssh_con.exec_command("k6 run social_network_selftune_k6.js")
    file_to_write = open(f"{filename}_k6_results.txt","w")
    print(stderr.read())
    file_to_write.write(stdout.read().decode("utf-8"))
    file_to_write.close()
    # scp.get("test_results.json", f"{filename}_k6_results.json")
    # scp.close()
    ssh_con.close()

def run_wrk2_dsb_on_client_machine(ssh_user:str, client_machine_name:str, server_machine_name:str, port:str, lua_script_path, filename):
    wrk = "./are-we-really-load-generating/new-experiments/DeathStarBench/wrk2/wrk"
    cmd = f"{wrk} -t4 -c5000 -d15m -R10000 --requests --latency http://{server_machine_name}:{port}"
    if lua_script_path != None:
        cmd += " --script " + lua_script_path
    print("run_wrk2_on_client_machine: command = ", cmd)
    file_to_write = open(f"{filename}_wrk2_results.csv","w")
    ssh_con = paramiko.SSHClient()
    # ssh_con.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_machine_name, username=ssh_user)
    stdin, stdout, stderr = ssh_con.exec_command(cmd)
    # print("run_wrk2_on_client_machine err: ", stderr.read().decode("utf-8"))
    file_to_write.write(stdout.read().decode("utf-8"))
    print("Execution is done")
    file_to_write.close()
    print("Finished reading wrk2 on client machine")
    ssh_con.close()

def run_wrk2_on_client_machine(ssh_user:str, client_machine_name:str, server_machine_name:str, port:str, lua_script_path, filename):
    wrk = "./wrk2/wrk"
    cmd = f"{wrk} -t2 -c100 -d15m -R10000 --latency http://{server_machine_name}:{port}"
    if lua_script_path != None:
        cmd += " --script " + lua_script_path
    print("run_wrk2_on_client_machine: command = ", cmd)
    file_to_write = open(f"{filename}_wrk2_results.csv","w")
    ssh_con = paramiko.SSHClient()
    # ssh_con.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_con.load_system_host_keys()
    ssh_con.connect(client_machine_name, username=ssh_user)
    stdin, stdout, stderr = ssh_con.exec_command(cmd)
    # print("run_wrk2_on_client_machine err: ", stderr.read().decode("utf-8"))
    file_to_write.write(stdout.read().decode("utf-8"))
    print("Execution is done")
    file_to_write.close()
    print("Finished reading wrk2 on client machine")
    ssh_con.close()

def deploy_everything(ssh_user:str, server_machine_name:str, exp_num:int=0):
    ssh_con = paramiko.SSHClient()
    # ssh_con.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_machine_name, username=ssh_user)
    stdin, stdout, stderr = ssh_con.exec_command("export KUBECONFIG=/etc/kubernetes/admin.conf")
    print(stdout.read())
    print(stderr.read())
    stdin, stdout, stderr = ssh_con.exec_command("sudo kubectl get nodes")
    print("kubectl get nodes: ", stdout.read())
    print("kubectl get nodes err: ", stdout.read())
    stdin, stdout, stderr = ssh_con.exec_command("sudo kubectl get pods")
    print("kubectl get pods: ", stdout.read())
    print("kubectl get pods err: ", stdout.read())
    if exp_num > 0:
        stdin, stdout, stderr = ssh_con.exec_command(f"cp SelfTune/python/examples/bluefin/recommender_deployment_{exp_num}.yaml autoscaler/vertical-pod-autoscaler/deploy/recommender-deployment.yaml")
        ssh_con.exec_command(f"cp SelfTune/python/examples/bluefin/config_{exp_num}.json DeathStarBench/socialNetwork/config/service-config.json")
    # stdin, stdout, stderr = ssh_con.exec_command("sudo ./autoscaler/vertical-pod-autoscaler/hack/vpa-up.sh")
    # print("vpa-up: ", stderr.read())
    # print("vpa-up err:",stdout.read())
    stdin, stdout, stderr = ssh_con.exec_command("sh install_socialnet_and_vpa.sh")
    print("install err: ", stderr.read().decode("utf-8"))
    print("install:",stdout.read().decode("utf-8"))
    time.sleep(60)
    stdin, stdout, stderr = ssh_con.exec_command("cd DeathStarBench/socialNetwork && python3 scripts/init_social_graph.py --port=30096")
    print("python err: ", stderr.read().decode("utf-8"))
    print("python:",stdout.read().decode("utf-8"))

def reset_everything(ssh_user:str, server_machine_name:str):
    ssh_con = paramiko.SSHClient()
    ssh_con.load_system_host_keys()
    ssh_con.connect(server_machine_name, username=ssh_user)
    stdin, stdout, stderr = ssh_con.exec_command("sh reset_socialnet.sh")
    # stdin, stdout, stderr = ssh_con.exec_command("ls")
    print(stdout.read())
    print(stderr.read())
    # stdin, stdout, stderr = ssh_con.exec_command("export KUBECONFIG=/etc/kubernetes/admin.conf")
    # print(stdout.read())
    # print(stderr.read())
    # stdin, stdout, stderr = ssh_con.exec_command("sudo ./autoscaler/vertical-pod-autoscaler/hack/vpa-down.sh")
    # print("vpa-down:",stdout.read())
    # print("vpa-down err:",stderr.read())
    # stdin, stdout, stderr = ssh_con.exec_command("cd DeathStarBench/socialNetwork && sudo helm uninstall socialnet")
    # print("helm uninstall socialnet:",stdout.read())
    # print("helm uninstall socialnet err:",stderr.read())

if __name__ == "__main__":
    # client_hostname = "c220g2-010605.wisc.cloudlab.us"
    client_hostname = "c220g2-011126.wisc.cloudlab.us"
    other_clients = ["c220g2-011126.wisc.cloudlab.us", 
                    "c220g2-010617.wisc.cloudlab.us", 
                    "c220g2-011328.wisc.cloudlab.us",
                    "c220g2-011332.wisc.cloudlab.us",
                    "c220g2-011012.wisc.cloudlab.us",
                    "c220g2-010619.wisc.cloudlab.us",
                    "c220g2-011001.wisc.cloudlab.us",
                    "c220g2-011131.wisc.cloudlab.us",
                    "c220g2-011128.wisc.cloudlab.us",
                    "c220g2-011002.wisc.cloudlab.us"]
    # server_hostname = "c220g2-030832.wisc.cloudlab.us"
    server_hostname = "c220g2-010604.wisc.cloudlab.us"
    loadgen = None
    user = "yugm2"

    # t1 = threading.Thread(target=put_vegeta_compose_body_to_client, args=(user, client_hostname, "new-experiments/experiment8/vegeta_socialnetwork_mbig.txt"))
    # other_threads = [ 
    #     threading.Thread(target=put_vegeta_compose_body_to_client, args=(user, other_clients[i], f"new-experiments/experiment8/vegeta_socialnetwork_m{i+1}.txt")) 
    #     for i in range(len(other_clients)) 
    # ]
    # t1.start()
    # for other_thread in other_threads:
    #     other_thread.start() 

    # t1.join()
    # for other_thread in other_threads:
    #     other_thread.join()

    # with open("vegeta_socialnetwork.txt","r") as f:


    # try:
    #     opts, args = getopt.getopt(sys.argv[1:],"u:c:s",["username=","client=","server="])
    # except getopt.GetoptError:
    #     print('selftune_experiment.py -c <client-hostname> -s <server-hostname> -u <username>')
    #     sys.exit(2)
    # for opt, arg in opts:
    #     if opt == '-c':
    #         print("client_hostname=",arg)
    #         client_hostname = arg
    #     elif opt == '-s':
    #         print("server_hostname=",arg)
    #         server_hostname = arg
    #     elif opt == '-u':
    #         print("user=",arg)
    #         user = arg
    #     else:
    #         # print("Invalid arguments")
    #         print('selftune_experiment.py -c <client-hostname> -s <server-hostname> -u <username>')
    #         sys.exit(2)
    # if (user == None or client_hostname == None or server_hostname == None):
    #     print("One of which is None:", user, client_hostname, server_hostname)
    #     print('selftune_experiment.py -c <client-hostname> -s <server-hostname> -u <username>')
    #     sys.exit(2)
    os.makedirs("new-experiments/experiment8/wrk2_results", exist_ok=True)
    # os.makedirs("new-experiments/experiment8/wrk2_dsb_results", exist_ok=True)
    # os.makedirs("new-experiments/experiment8/k6_results", exist_ok=True)
    # os.makedirs("new-experiments/experiment8/locust_results", exist_ok=True)
    # os.makedirs("new-experiments/experiment8/h2load_results", exist_ok=True)
    # os.makedirs("new-experiments/experiment8/vegeta_results", exist_ok=True)
    
    # port = "31565"
    port = "30096"
    # put_locustfile_on_clients(user, client_hostname, other_clients)
    # ssh_con = paramiko.SSHClient()
    # ssh_con.load_system_host_keys()
    # print("run_k6_on_client_machine: client_hostname=",client_hostname,", ssh_user=",ssh_user)
    # ssh_con.connect(client_hostname, username=user)
    # scp = SCPClient(ssh_con.get_transport())
    # # scp.put("new-experiments/experiment8/social_network_selftune_k6.js","social_network_selftune_k6.js")
    # put_h2load_on_clients(user, client_hostname, other_clients)
    # put_vegeta_compose_body_to_clients(user,client_hostname)
    # reset_everything(user, server_hostname)
    # deploy_everything(user, server_hostname)
    # # run_wrk2_dsb_on_client_machine(user, client_hostname, server_hostname, port, lua_script_path="are-we-really-load-generating/new-experiments/DeathStarBench/socialNetwork/wrk2/scripts/social-network/mixed-workload.lua", filename="new-experiments/experiment8/wrk2_dsb_results/default")
    # # run_k6_on_client_machine(user, client_hostname, port, filename="new-experiments/experiment8/k6_results/default")
    # run_locust_on_client_machines(user, client_hostname, other_clients, server_hostname, port, filename="new-experiments/experiment8/locust_results/default")
    # run_h2load_on_clients(user, client_hostname, other_clients, server_hostname, port, filename="new-experiments/experiment8/h2load_results/default")
    # run_vegeta_on_client(user, client_hostname, other_clients, filename="new-experiments/experiment8/vegeta_results/default")
    for i in range(50):
        reset_everything(user, server_hostname)
        deploy_everything(user, server_hostname, i+1)
        # run_k6_on_client_machine(user, client_hostname, port, filename=f"new-experiments/experiment8/k6_results/iter{i+1}")
        # run_wrk2_dsb_on_client_machine(user, client_hostname, server_hostname, port, lua_script_path="are-we-really-load-generating/new-experiments/DeathStarBench/socialNetwork/wrk2/scripts/social-network/mixed-workload.lua", filename=f"new-experiments/experiment8/wrk2_dsb_results/iter{i+1}")
        run_wrk2_on_client_machine(user, client_hostname, server_hostname, port, lua_script_path="are-we-really-load-generating/new-experiments/DeathStarBench/socialNetwork/wrk2/scripts/social-network/mixed-workload.lua", filename=f"new-experiments/experiment8/wrk2_results/iter{i+1}")
        # run_locust_on_client_machines(user, client_hostname, other_clients, server_hostname, port, filename=f"new-experiments/experiment8/locust_results/iter{i+1}")
        # kill_locust(user, client_hostname, other_clients)
        # run_h2load_on_clients(user, client_hostname, other_clients, server_hostname, port, filename=f"new-experiments/experiment8/h2load_results/iter{i+1}")
        # run_vegeta_on_client(user, client_hostname, other_clients, filename=f"new-experiments/experiment8/vegeta_results/iter{i+1}")
    # kill_locust(user, client_hostname, other_clients)