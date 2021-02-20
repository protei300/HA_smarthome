#/bin/bash

IP=$1
PWD=$2

curl --user root:$PWD 192.168.1.$IP/cgi-bin/get_miner_status.cgi  --anyauth
