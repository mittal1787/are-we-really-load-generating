from oppertune.oppertune_algorithms.src.oppertune.algorithms.ddpg import DDPG
from oppertune.core.values import Categorical, Integer, Real
import json
import yaml
import numpy as np


def get_reward(pred) -> float:
    """Negative RMSE Loss."""
    target = np.asarray([])
    return -np.sqrt(np.mean(np.square(pred - target)))

def create_socialnetwork_config(pred,config_num) -> dict:
    with open("old_config.json", "r") as file:
        old_config = json.load(file)
        i = 0
        for item in pred:
            if i >= 4:
                service = item[:item.index("_")]
                param = item[item.index("_") + 1:]
                old_config[service][param] = pred[item]
            i += 1
        with open(f"config_{config_num}.json","w") as file2:
            json.dump(old_config, file2, indent=4)

def create_recommender_deployment(pred,config_num):
    with open("old_recommender_deployment.yaml") as stream:
        try:
            old_config = list(yaml.safe_load_all(stream))
            print(old_config)
            i = 0
            for item in pred:
                if i < 4:
                    if i == 0:
                        old_config[0]["spec"]["template"]["spec"]["containers"][0]["args"] = [f"--{item}={pred[item]}"]
                    else:
                        old_config[0]["spec"]["template"]["spec"]["containers"][0]["args"].append(f"--{item}={pred[item]}")
                i += 1
            with open(f"recommender_deployment_{config_num}.yaml", "w") as file2:
                yaml.dump(old_config, file2)
        except yaml.YAMLError as exc:
            print(exc)

def main():
    parameters = [
        Integer(name="cpu-histogram-decay-half-life", val=24, min=0, max=24),
        Real(name="recommendation-margin-fraction", val=0.15, min=0.0, max=1.0),
        Integer(name="pod-recommendation-min-cpu", val=25, min=0, max=24000),
        Integer(name="history-length", val=24, min=0, max=24)
    ]

    all_services = ["cpu-histogram-decay-half-life", "recommendation-margin-fraction", "pod-recommendation-min-cpu", "history-length"]
    print(all_services)
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
                if "connections" in service_data[service]:
                    parameters.append(
                        Integer(name=f"{service}_connections", val=service_data[service]["connections"], min=0, max=512)
                    )
                    all_services.append(f"{service}_connections")
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
                if "use_cluster" in service_data[service]:
                    parameters.append(
                        Integer(name=f"{service}_use_cluster", val=service_data[service]["use_cluster"], min=0, max=1)
                    )
                    all_services.append(f"{service}_use_cluster")
                # if "workers" in service_data[service]:
                #     parameters.append(
                #         {
                #             "type": "discrete",
                #             "name": f"{service}_workers",
                #             "initial_value": service_data[service]["workers"],
                #             "lb": 0,
                #             "ub": 192,
                #         }
                #     )
                    # all_services.append(f"{service}_workers")

    state_config = [
        Integer("cpu", val=0, min=0, max=4000),
        Integer("memory", val=0, min=0, max=160*10*1024*1024*1024),
        Integer("workload_volume",val=10000, max=10000, min=0),
        Integer("clients", val=1000, min=1, max=500000),
        Integer("read_home_timeline", val=67500, min=0, max=67500),
        Integer("read_user_timeline", val=67500, min=0, max=67500),
        Integer("compose_post", val=15000, min=0, max=15000),
    ]

    # print(parameters)

    tuning_instance = DDPG(
        parameters,
        state_config
    )

    num_iterations = 50
    old_cpu_decay = parameters[1].val

    for i in range(num_iterations):
        # Predict the next set of perturbed parameters
        prediction, request_id = tuning_instance.predict()

        # Receive feedback
        # reward = get_reward(np.asarray([pred["p1"], pred["p2"]]))

        # print("Pred =",pred)
        with open(f'results_{i}.json', 'w') as fp:
            json.dump(prediction, fp, indent=4)

        create_socialnetwork_config(prediction, i+1)
        create_recommender_deployment(prediction,i+1)

        # Send the feedback to SelfTune for the gradient update
        reward = prediction["cpu-histogram-decay-half-life"] - old_cpu_decay
        
        tuning_instance.store_reward(request_id, reward)

        # tuning_instance.set_reward(reward)

        old_cpu_decay = prediction["cpu-histogram-decay-half-life"]

main()
