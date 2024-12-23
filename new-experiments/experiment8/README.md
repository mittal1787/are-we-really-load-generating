# Experiment 8 (SelfTune SocialNetwork Experiment)

For this experiment, the workload generated by the load generators will replicate the workload stressing the DeathStarBench Social Network when running SelfTune. According to SelfTune paper, they used SocialNetwork microservice application, and they ran 500 RPS for 15 minutes with the ratio of 9 GET requests to 1 POST request.

## Purpose of this experiment
SelfTune paper was accepted in NSDI'23, and they used wrk2 to verify their system. However, depending on the previous experiment results, wrk2 and other load generators can give wrong results, and this puts the reliability of SelfTune into question.

## Experiment design
The DeathStarBench SocialNetwork application was run on four servers, each with 24 cores, 40GB of memory, and 250GB of disk space. From there, the workload generator ran a mixed workload of read timelines and creating new posts in a ratio of 9 to 1 at 500 requests per second from another machine. The experimenters ran the Kubernetes Vertical Pod Autoscaler with 85 configuration parameters (2-5 parameters per microservices) for the 28 microservices, all of which impact the application latency.

The experimenters ran the SelfTune's Bluefin and compared it with [Gaussian Process method](https://papers.nips.cc/paper_files/paper/2011/file/86e8f7ab32cfd12577bc2619bc635690-Paper.pdf), [Contextual Bandits method](https://arxiv.org/abs/1802.04064), and [Deep Deterministic Policy Gradient](https://arxiv.org/abs/1509.02971).

After running the workload generator each time, update the parameters accordingly until the parameters converge to a certain value.

After each tuning, raise the RPS to 10000 RPS and verify the convergence.

In our case, we can use 4 c6525-100g Cloudlab Utah machine (each with 24 cores, 128 GB of Memory), or two Wisconsin 8545 Cloudlab machines (each with 48 cores and 512 GB memory).

## Setting up machines
For multiple machines, kubeadm will be used to create the multiple machine kubernetes cluster. 