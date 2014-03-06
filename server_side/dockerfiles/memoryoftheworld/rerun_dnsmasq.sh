#!/bin/sh

echo bind-interfaces > /etc/dnsmasq.d/local
echo listen-address=127.0.0.1 >> /etc/dnsmasq.d/local
echo server=8.8.8.8 >> /etc/dnsmasq.d/local
echo address=/dokr/`docker inspect -format '{{ .NetworkSettings.IPAddress }}' lssb` >> /etc/dnsmasq.d/local

if [ "`head -n 1 /etc/resolv.conf`" != "nameserver 127.0.0.1" ]; then
    echo "nameserver 127.0.0.1\n$(cat /etc/resolv.conf)" > /etc/resolv.conf
fi
service dnsmasq restart
