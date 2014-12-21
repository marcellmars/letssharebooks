#!/bin/sh

mkdir -p /var/log/supervisor
mkdir -p /var/run/supervisor
locale-gen en_US en_US.UTF-8

apt-get update

apt-get -y install python-pip dnsmasq
pip install supervisor
echo conf-dir=/etc/dnsmasq.d >> /etc/dnsmasq.conf
echo user=root >> /etc/dnsmasq.conf
