git clone https://github.com/delimitrou/DeathStarBench.git
sudo apt-get update
sudo apt install libssl-dev
cd DeathStarBench/wrk2
git submodule update --init --recursive
git submodule update --recursive --remote
git pull origin master
make