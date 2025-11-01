#!/bin/bash

# Network configuration script
# Configure ens3 interface with static IP and default route

# Set variables
INTERFACE="ens3"
MY_MAC_ADDRESS="$(cat /sys/class/net/${INTERFACE}/address)"
LAST_OCTET=$(echo $MY_MAC_ADDRESS | awk -F ":" '{print $6}')
LAST_DECIMAL=$(printf "%d" "0x$LAST_OCTET")
#echo $LAST_DECIMAL
IP_ADDRESS="192.168.102.1${LAST_DECIMAL}/24"
#GATEWAY="192.168.102.1"

# Add IP address to interface
echo "Setting IP address $IP_ADDRESS on $INTERFACE..."
ip addr add $IP_ADDRESS dev $INTERFACE
if [ $? -ne 0 ]; then
    echo "Failed to set IP address!"
    exit 1
fi

# Bring interface up
echo "Bringing up interface $INTERFACE..."
ip link set $INTERFACE up
if [ $? -ne 0 ]; then
    echo "Failed to bring up interface!"
    exit 1
fi

# Add default route
#echo "Setting default route via $GATEWAY..."
#ip route add default via $GATEWAY
#if [ $? -ne 0 ]; then
#    echo "Failed to set default route!"
#    exit 1
#fi

echo "Network configuration completed successfully!"
