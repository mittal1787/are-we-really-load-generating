git clone https://github.com/mittal1787/DeathStarBench.git
sudo apt-get update
sudo apt install lua5.4 liblua5.4-dev
sudo apt install libssl-dev
sudo apt install zlib1g
cd DeathStarBench/wrk2
git submodule update --init --recursive
git submodule update --recursive --remote
git pull origin master
make