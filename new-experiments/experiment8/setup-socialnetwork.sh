sudo apt update
sudo apt install python3-pip
pip3 install paramiko numpy matplotlib
cd ../.. && python3 -m new-experiments.experiment8.selftune_experiment -c $1 -s $2 -u $3
