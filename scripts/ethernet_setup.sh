#!/bin/bash

#setup ethernet for pluging Pi4 directly to laptop via RJ45

# Check if script is run as root
if [[ $EUID -ne 0 ]]; then
   echo "This script must be run as root" 
   exit 1
fi

# Check if dhcpd service is installed
if ! pacman -Qs dhcp &> /dev/null; then
   echo "dhcp package not found. Install it with 'pacman -S dhcp'"
   exit 1
fi


# Get interface names and static IP address for laptop
read -p "Enter ethernet interface name: " interface
read -p "Enter WiFi interface name: " wlan
read -p "Enter static IP address for laptop: " ip_address

# Set up ICS and forward traffic from ethernet to WiFi
echo 1 > /proc/sys/net/ipv4/ip_forward
iptables -t nat -A POSTROUTING -o $wlan -j MASQUERADE
iptables -A FORWARD -i $wlan -o $interface -m state --state RELATED,ESTABLISHED -j ACCEPT
iptables -A FORWARD -i $interface -o $wlan -j ACCEPT

# Set static IP address on laptop
ip link set $interface down
ip address add $ip_address/24 dev $interface
ip link set $interface up

# Create dhcpd.conf file
echo "subnet 192.168.137.0 netmask 255.255.255.0 {
  range 192.168.137.2 192.168.137.10;
  option routers $ip_address;
  option domain-name-servers 8.8.8.8, 8.8.4.4;
}" > /etc/dhcpd.conf

# Start DHCP server on ethernet interface
dhcpd $interface

