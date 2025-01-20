import numpy as np
import json
import yaml

from selftune_core import SelfTune

throughput_attained = [499.61, ]
cpu_histogram_delay_half_lives = [24,22]

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
            old_config = list(yaml.load_all(stream))
            i = 0
            for item in pred:
                if i < 4:
                    if i == 0:
                        old_config[1]["spec"]["template"]["spec"]["containers"][0]["args"] = [f"--{item}={pred[item]}"]
                    else:
                        old_config[1]["spec"]["template"]["spec"]["containers"][0]["args"].append(f"--{item}={pred[item]}")
                i += 1
            with open(f"recommender_deployment_{config_num}.yaml", "w") as file2:
                yaml.dump(old_config, file2)
        except yaml.YAMLError as exc:
            print(exc)

def main():
    parameters = [
        {
            "type": "discrete",
            "name": "cpu-histogram-decay-half-life",
            "initial_value": 24,
            "lb": 0,
            "ub": 24,
        },
        {
            "type": "continuous",
            "name": "recommendation-margin-fraction",
            "initial_value": 0.15,
            "lb": 0.0,
            "ub": 1.0,
        },
        {
            "type": "discrete",
            "name": "pod-recommendation-min-cpu",
            "initial_value": 25,
            "lb": 0,
            "ub": 24000,
        },
        {
            "type": "discrete",
            "name": "history-length",
            "initial_value": 24,
            "lb": 0,
            "ub": 24,
        },
    ]

    all_services = ["cpu-histogram-decay-half-life", "recommendation-margin-fraction", "pod-recommendation-min-cpu", "history-length"]
    with open("old_config.json", "r") as file:
        service_data = json.load(file)
        # all_services.extend(service_data.keys())
        for service in service_data:
            if isinstance(service_data[service],dict):
                if "keepalive_ms" in service_data[service]:
                    parameters.append(
                        {
                            "type": "discrete",
                            "name": f"{service}_keepalive_ms",
                            "initial_value": service_data[service]["keepalive_ms"],
                            "lb": 0,
                            "ub": 10000,
                        }
                    )
                    all_services.append(f"{service}_keepalive_ms")
                if "timeout_ms" in service_data[service]:
                    parameters.append(
                        {
                            "type": "discrete",
                            "name": f"{service}_timeout_ms",
                            "initial_value": service_data[service]["timeout_ms"],
                            "lb": 0,
                            "ub": 10000,
                        }
                    )
                    all_services.append(f"{service}_timeout_ms")
                if "connections" in service_data[service]:
                    parameters.append(
                        {
                            "type": "discrete",
                            "name": f"{service}_connections",
                            "initial_value": service_data[service]["connections"],
                            "lb": 0,
                            "ub": 512,
                        }
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
                        {
                            "type": "discrete",
                            "name": f"{service}_use_cluster",
                            "initial_value": service_data[service]["use_cluster"],
                            "lb": 0,
                            "ub": 1,
                        }
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

    # Initialize an instance of SelfTune
    st = SelfTune(
        algorithm="bluefin",
        parameters=parameters,
        algorithm_args=dict(
            feedback="twopoint",
            eta=0.01,
            delta=0.1,
            random_seed=4,
            logging_level="debug"
        ),
    )

    print(len(parameters))

    num_iterations = 50
    old_cpu_decay = parameters[1]["initial_value"]

    for i in range(num_iterations):
        # Predict the next set of perturbed parameters
        pred = st.predict()

        # Receive feedback
        # reward = get_reward(np.asarray([pred["p1"], pred["p2"]]))

        # print("Pred =",pred)
        with open(f'results_{i}.json', 'w') as fp:
            json.dump(pred, fp, indent=4)

        create_socialnetwork_config(pred, i+1)
        create_recommender_deployment(pred,i+1)

        # Send the feedback to SelfTune for the gradient update
        reward = pred["cpu-histogram-decay-half-life"] - old_cpu_decay
        
        st.set_reward(reward)

        old_cpu_decay = pred["cpu-histogram-decay-half-life"]

        if i % 5 == 0:
            print(
                f'Round={i}, Reward={reward},'
                f" Best=({st.center[0]:.4f}, {st.center[1]:.4f})"
            )


if __name__ == "__main__":
    main()
