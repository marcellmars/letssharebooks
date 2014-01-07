#! /bin/sh

echo bind-interfaces > /etc/dnsmasq.d/local
echo listen-address=127.0.0.1 >> /etc/dnsmasq.d/local
echo server=8.8.8.8 >> /etc/dnsmasq.d/local
echo address=/dokr/`hostname -I` >> /etc/dnsmasq.d/local
exit
