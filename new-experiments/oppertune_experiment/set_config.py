# save this as app.py
from oppertune.algorithms.hybrid_solver import HybridSolver
from oppertune.core.values import Categorical, Integer, Real
from flask import Flask
import json
import subprocess
from flask import request

app = Flask(__name__)


class Config:
    def __init__(self):
        parameters = [
            Categorical(name="mongodb-tls",  val="disabled", categories=("disabled","enabled")),
            Categorical(name="redis-tls-auth-clients", val="no", categories=("no", "yes")),
            
            Real(name="media-memcached-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="media-memcached-limits-memory", val=128, min=0, max=4096),
            Real(name="media-memcached-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="media-memcached-requests-memory", val=128, min=0, max=4096),

            Real(name="post-storage-memcached-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="post-storage-memcached-limits-memory", val=128, min=0, max=4096),
            Real(name="post-storage-memcached-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="post-storage-memcached-requests-memory", val=128, min=0, max=4096),

            Real(name="url-shorten-memcached-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="url-shorten-memcached-limits-memory", val=128, min=0, max=4096),
            Real(name="url-shorten-memcached-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="url-shorten-memcached-requests-memory", val=128, min=0, max=4096),

            Real(name="user-memcached-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-memcached-limits-memory", val=128, min=0, max=4096),
            Real(name="user-memcached-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-memcached-requests-memory", val=128, min=0, max=4096),
            
            Real(name="post-storage-mongodb-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="post-storage-mongodb-limits-memory", val=128, min=0, max=4096),
            Real(name="post-storage-mongodb-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="post-storage-mongodb-requests-memory", val=128, min=0, max=4096),
            
            Real(name="media-mongodb-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="media-mongodb-limits-memory", val=128, min=0, max=4096),
            Real(name="media-mongodb-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="media-mongodb-requests-memory", val=128, min=0, max=4096),
            
            Real(name="social-graph-mongodb-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="social-graph-mongodb-limits-memory", val=128, min=0, max=4096),
            Real(name="social-graph-mongodb-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="social-graph-mongodb-requests-memory", val=128, min=0, max=4096),
            
            Real(name="url-shorten-mongodb-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="url-shorten-mongodb-limits-memory", val=128, min=0, max=4096),
            Real(name="url-shorten-mongodb-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="url-shorten-mongodb-requests-memory", val=128, min=0, max=4096),
            
            Real(name="user-mongodb-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-mongodb-limits-memory", val=128, min=0, max=4096),
            Real(name="user-mongodb-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-mongodb-requests-memory", val=128, min=0, max=4096),
            
            Real(name="user-timeline-mongodb-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-timeline-mongodb-limits-memory", val=128, min=0, max=4096),
            Real(name="user-timeline-mongodb-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-timeline-mongodb-requests-memory", val=128, min=0, max=4096),
            
            Real(name="media-frontend-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="media-frontend-limits-memory", val=128, min=0, max=4096),
            Real(name="media-frontend-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="media-frontend-requests-memory", val=128, min=0, max=4096),
            
            Real(name="nginx-thrift-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="nginx-thrift-limits-memory", val=128, min=0, max=4096),
            Real(name="nginx-thrift-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="nginx-thrift-requests-memory", val=128, min=0, max=4096),
            
            Real(name="rabbitmq-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="rabbitmq-limits-memory", val=128, min=0, max=4096),
            Real(name="rabbitmq-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="rabbitmq-requests-memory", val=128, min=0, max=4096),
            
            Real(name="compose-post-redis-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="compose-post-redis-limits-memory", val=128, min=0, max=4096),
            Real(name="compose-post-redis-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="compose-post-redis-requests-memory", val=128, min=0, max=4096),
            
            Real(name="home-timeline-redis-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="home-timeline-redis-limits-memory", val=128, min=0, max=4096),
            Real(name="home-timeline-redis-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="home-timeline-redis-requests-memory", val=128, min=0, max=4096),

            Real(name="social-graph-redis-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="social-graph-redis-limits-memory", val=128, min=0, max=4096),
            Real(name="social-graph-redis-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="social-graph-redis-requests-memory", val=128, min=0, max=4096),

            Real(name="user-timeline-redis-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-timeline-redis-limits-memory", val=128, min=0, max=4096),
            Real(name="user-timeline-redis-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-timeline-redis-requests-memory", val=128, min=0, max=4096),

            Real(name="compose-post-service-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="compose-post-service-limits-memory", val=128, min=0, max=4096),
            Real(name="compose-post-service-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="compose-post-service-requests-memory", val=128, min=0, max=4096),

            Real(name="home-timeline-service-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="home-timeline-service-limits-memory", val=128, min=0, max=4096),
            Real(name="home-timeline-service-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="home-timeline-service-requests-memory", val=128, min=0, max=4096),

            Real(name="media-service-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="media-service-limits-memory", val=128, min=0, max=4096),
            Real(name="media-service-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="media-service-requests-memory", val=128, min=0, max=4096),

            Real(name="post-storage-service-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="post-storage-service-limits-memory", val=128, min=0, max=4096),
            Real(name="post-storage-service-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="post-storage-service-requests-memory", val=128, min=0, max=4096),

            Real(name="social-graph-service-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="social-graph-service-limits-memory", val=128, min=0, max=4096),
            Real(name="social-graph-service-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="social-graph-service-requests-memory", val=128, min=0, max=4096),

            Real(name="text-service-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="text-service-limits-memory", val=128, min=0, max=4096),
            Real(name="text-service-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="text-service-requests-memory", val=128, min=0, max=4096),

            Real(name="unique-id-service-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="unique-id-service-limits-memory", val=128, min=0, max=4096),
            Real(name="unique-id-service-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="unique-id-service-requests-memory", val=128, min=0, max=4096),

            Real(name="url-shorten-service-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="url-shorten-service-limits-memory", val=128, min=0, max=4096),
            Real(name="url-shorten-service-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="url-shorten-service-requests-memory", val=128, min=0, max=4096),

            Real(name="user-mention-service-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-mention-service-limits-memory", val=128, min=0, max=4096),
            Real(name="user-mention-service-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-mention-service-requests-memory", val=128, min=0, max=4096),

            Real(name="user-service-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-service-limits-memory", val=128, min=0, max=4096),
            Real(name="user-service-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-service-requests-memory", val=128, min=0, max=4096),

            Real(name="user-timeline-service-limits-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-timeline-service-limits-memory", val=128, min=0, max=4096),
            Real(name="user-timeline-service-requests-cpu", val=0.1, min=0.0, max=400.0),
            Integer(name="user-timeline-service-requests-memory", val=128, min=0, max=4096),
        ]

        proc = subprocess.run("export KUBECONFIG=/etc/kubernetes/admin.conf && sudo helm uninstall socialnet", shell=True)
        if proc.stderr:
            for line in proc.stderr.split('\n'):
                print(line)
        if proc.stdout:
            for line in proc.stdout.split('\n'):
                print(line)

        self.rightsizing_params_count = len(parameters)
        all_services = []

        with open("old_config.json", "r") as file:
            service_data = json.load(file)
            # all_services.extend(service_data.keys())
            for service in service_data:
                if isinstance(service_data[service],dict):
                    if "keepalive_ms" in service_data[service]:
                        parameters.append(
                            Integer(name=f"{service}_keepalive_ms", val=service_data[service]["keepalive_ms"], min=0, max=10000)    
                        )
                        all_services.append(f"{service}_keepalive_ms")
                    if "timeout_ms" in service_data[service]:
                        parameters.append(
                            Integer(name=f"{service}_timeout_ms", val=service_data[service]["timeout_ms"], min=0, max=10000)
                        )
                        all_services.append(f"{service}_timeout_ms")
                    # if "connections" in service_data[service]:
                    #     parameters.append(
                    #         Integer(name=f"{service}_connections", val=service_data[service]["connections"], min=0, max=512)
                    #     )
                    #     all_services.append(f"{service}_connections")
                    # if "binary_protocol" in service_data[service]:
                    #     parameters.append(
                    #         {
                    #             "type": "discrete",
                    #             "name": f"{service}_binary_protocol",
                    #             "initial_value": service_data[service]["binary_protocol"],
                    #             "lb": 0,
                    #             "ub": 1,
                    #         }
                    #     )
                    # if "use_cluster" in service_data[service]:
                    #     parameters.append(
                    #         Integer(name=f"{service}_use_cluster", val=service_data[service]["use_cluster"], min=0, max=1)
                    #     )
                    #     all_services.append(f"{service}_use_cluster")
    
        self.tuning_instance = HybridSolver(
            parameters,
            categorical_algorithm="exponential_weights_slates",  # For the categorical parameters
            categorical_algorithm_args=dict(
                random_seed=123,  # For reproducibility
            ),
            numerical_algorithm="bluefin",  # For the numerical (integer and real) parameters
            numerical_algorithm_args=dict(
                feedback=2,
                eta=0.01,
                delta=0.1,
                random_seed=123,  # For reproducibility
            ),
        )

        self.config_num = 1
        prediction, self.request_id = self.tuning_instance.predict()
        self.set_config(prediction)

    def create_socialnetwork_config(self, pred,config_num) -> dict:
        with open("old_config.json", "r") as file:
            old_config = json.load(file)
            i = 0
            for item in pred:
                if i >= self.rightsizing_params_count:
                    service = item[:item.index("_")]
                    param = item[item.index("_") + 1:]
                    old_config[service][param] = pred[item]
                i += 1
            with open(f"config_{config_num}.json","w") as file2:
                json.dump(old_config, file2, indent=4)
            return old_config
        return {}

    def set_config(self, prediction):
        self.helm_command = "sudo helm install socialnet DeathStarBench/socialNetwork/helm-chart/socialnetwork"
        i = 2
        item_list = list(prediction.keys())
        # i = self.rightsizing_params_count - 8
        self.command_list = []
        # while i < self.rightsizing_params_count:
        while i < 0:
            item = item_list[i]
            cpu_limits = prediction[item_list[i]]
            memory_limits = prediction[item_list[i+1]]
            cpu_requests = prediction[item_list[i+2]]
            memory_requests = prediction[item_list[i+3]]
            service = item[:item.index("-limits")]
            self.command_list.append(f"sudo kubectl set resources deployment {service} --limits=cpu={cpu_limits},memory={memory_limits}Mi --requests=cpu={cpu_requests},memory={memory_requests}Mi")
            # self.helm_command += f"""--set-string {service}.container.resources="requests:
            #     memory: "{memory_requests}Mi"
            #     cpu: "{cpu_requests}"
            # limits:
            #     memory: "{memory_limits}Mi"
            #     cpu: "{cpu_requests}"" \\
            # """
            i += 4
        print("Helm command: ", self.helm_command)
        mongo_tls = prediction["mongodb-tls"]
        redis_tls = prediction["redis-tls-auth-clients"]
        mongo_setting = "{{- define \"socialnetwork.templates.mongo.mongod.conf\"  }} \n" + \
        f"""net:
    tls:
        mode: {mongo_tls}""" + "\n{{- end }}"

        redis_setting = """{{- define "socialnetwork.templates.redis.redis.conf"  }}""" + \
        f"""
io-threads 8
io-threads-do-reads yes
port 6379
tls-port 0

tls-cert-file /keys/server.crt
tls-key-file /keys/server.key

tls-auth-clients {redis_tls}
        """ + \
        """
{{- end }}"""
        old_config = self.create_socialnetwork_config(prediction,self.config_num)
        self.config_num += 1
        self.service_config_tpl = """{{- define "mongodb-sharded.connection" }}
{{ .Values.global.mongodb.sharding.svc.user }}:{{ .Values.global.mongodb.sharding.svc.password }}@{{ .Values.global.mongodb.sharding.svc.name }}
{{- end }}

{{- define "memcached-cluster.connection" }}
  {{ .Release.Name }}-mcrouter
{{- end }}

{{- define "redis-cluster.connection" }}
  {{ .Release.Name }}-redis-cluster
{{- end}}

{{- define "socialnetwork.templates.other.service-config.json"  }}\n""" + json.dumps(old_config) + """
{{- end}}"""
        with open("DeathStarBench/socialNetwork/helm-chart/socialnetwork/templates/configs/other/service-config.tpl", "w") as f:
            print(self.service_config_tpl, file=f, end="")
        with open("DeathStarBench/socialNetwork/helm-chart/socialnetwork/templates/configs/mongo/mongod.tpl", "w") as f:
            print(mongo_setting, file=f, end="")
        with open("DeathStarBench/socialNetwork/helm-chart/socialnetwork/templates/configs/redis/redis.tpl", "w") as f:
            print(redis_setting, file=f, end="")
        with open("DeathStarBench/socialNetwork/config/service-config.json", "w") as f:
            json.dump(old_config, f, indent=4)
        
        proc = subprocess.run(f"export KUBECONFIG=/etc/kubernetes/admin.conf && {self.helm_command}", shell=True)
        # proc = subprocess.run(f"{self.helm_command}")
        if proc.stdout:
            for line in proc.stdout.split('\n'):
                print(line)

        if proc.stderr:
            for line in proc.stderr.split('\n'):
                print(line)

        for kubectl_command in self.command_list:
            print(kubectl_command)
            proc = subprocess.run(f"export KUBECONFIG=/etc/kubernetes/admin.conf && {kubectl_command}", shell=True)
            # proc = subprocess.run(f"{self.helm_command}")
            if proc.stdout:
                for line in proc.stdout.split('\n'):
                    print(line)

            if proc.stderr:
                for line in proc.stderr.split('\n'):
                    print(line)

    def predict_next(self, latency):
        self.tuning_instance.store_reward(self.request_id, latency)
        self.tuning_instance.set_reward(latency)
        proc = subprocess.run("export KUBECONFIG=/etc/kubernetes/admin.conf && sudo helm uninstall socialnet")
        for line in proc.stderr.split('\n'):
            print(line)
        for line in proc.stdout.split('\n'):
            print(line)
        prediction, self.request_id = self.tuning_instance.predict()
        self.set_config(prediction)


config_setter = Config()

@app.route("/")
def hello():
    global config_setter
    p95_latency = request.data["latency"]
    config_setter.predict_next(p95_latency)
    return "Hello, World!"


app.run()