#!/bin/bash

# Batman node setup script
# Configure ens4 interface for batman node 

# Set variables
INTERFACE="ens4"

echo "Awakening batman_adv from its slumber."
modprobe batman_adv
if [ $? -ne 0 ]; then
	echo "It did not awaken..."
	exit 1
fi

echo "Submitting $INTERFACE to batman's control."
batctl if add $INTERFACE
if [ $? -ne 0 ]; then
    echo "It did not submit..."
    exit 1
fi

echo "Batman-adv is ready my Lord!"


BAT_IF="bat0"
MY_MAC_ADDRESS="$(cat /sys/class/net/${INTERFACE}/address)"
LAST_OCTET=$(echo $MY_MAC_ADDRESS | awk -F ":" '{print $6}')
LAST_DECIMAL=$(printf "%d" "0x$LAST_OCTET")
MY_IP_ADDRESS="192.168.101.1${LAST_DECIMAL}"
echo "My generated IP address of $BAT_IF: $MY_IP_ADDRESS based on MAC: $MY_MAC_ADDRESS"
ip addr add $MY_IP_ADDRESS/24 dev $BAT_IF
ip link set $INTERFACE up
ip link set $BAT_IF up

ip link set up mtu 1450 dev $BAT_IF

systemctl stop ufw 

./socket_script.sh
