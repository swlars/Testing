# Testing
Testing

##################################################
Set the directories:
##################################################

IPERF3_CONTROL = "/home/swlarsen/git/esnet/iperf/src/iperf3"
IPERF3_TEST = "/home/swlarsen/git/seg/iperf/src/iperf3"
IPERF2="/home/swlarsen/git/iperf2-code/src/iperf"

##################################################
     Clone Them
##################################################
git clone git://git.code.sf.net/p/iperf2/code iperf2-code

git clone https://github.com/esnet/iperf.git
cd iperf
git fetch
git checkout mt


##################################################
     Build them
##################################################
./bootstrap.sh
./configure
make


##################################################
     Python
##################################################
python3 -m pip install seaborn
python3 -m pip install Tk
python3 tp.py

