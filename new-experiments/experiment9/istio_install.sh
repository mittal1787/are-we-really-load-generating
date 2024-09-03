sh install_kubernetes.sh
curl -L https://istio.io/downloadIstio | sh -
cd istio-1.23.0
export PATH=$PWD/bin:$PATH
kind create cluster --name istio-testing
istioctl install