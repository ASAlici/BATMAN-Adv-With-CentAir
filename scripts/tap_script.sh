#! /bin/sh

#USER="$(whoami)"
#BRIDGE=odev-br
#NUM_SESSIONS=3
#sudo ip link add "${BRIDGE}" type bridge
#for i in $(seq 1 "${NUM_SESSIONS}"); do
	#sudo ip tuntap add dev tap$i mode tap user "$USER"
	#sudo ip link set tap$i up 
	#sudo ip link set tap$i master "${BRIDGE}"
#done

#sudo ip link set "${BRIDGE}" up
#sudo ip addr replace 192.168.251.1/24 dev "${BRIDGE}" 

#sudo ./virtual-network-filter-traffic.nft


sudo ip tuntap add dev tapdev mode tap user ahmet
sudo ip link set tapdev up
sudo ip addr add 192.168.100.3/24 dev tapdev

