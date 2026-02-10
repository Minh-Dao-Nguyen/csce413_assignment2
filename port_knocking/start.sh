#!/bin/bash

# iptables -F

# # allow loopback
# iptables -A INPUT -i lo -j ACCEPT

# # allow established
# iptables -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# # block SSH by default
# iptables -A INPUT -p tcp --dport 2222 -j DROP

# knockd -d &
# exec /usr/sbin/sshd -D


# iptables -F
# iptables -t nat -F

# # allow established
# iptables -A FORWARD -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# # block SSH by default
# iptables -A FORWARD -p tcp --dport 2222 -j DROP

# knockd -d &
# exec /usr/sbin/sshd -D

IPT=/usr/sbin/iptables-legacy

$IPT -F

$IPT -A INPUT -i lo -j ACCEPT
$IPT -A INPUT -m conntrack --ctstate ESTABLISHED,RELATED -j ACCEPT

# block SSH by default
$IPT -A INPUT -p tcp --dport 2222 -j DROP

knockd -d &
exec /usr/sbin/sshd -D