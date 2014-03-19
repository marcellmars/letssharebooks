#!/bin/sh

locale-gen en_US en_US.UTF-8

mkdir -p /var/log/supervisor/
mkdir -p /var/run/supervisor/
mkdir -p /var/run/sshd/
mkdir -p /var/www/
mkdir -p /etc/ssl/certs/
mkdir -p /etc/ssl/private/

chmod ug+rx /usr/local/bin/current_ip.sh
chmod ug+rx /usr/local/bin/get_tunnel_ports.sh
chmod ug+rx /usr/local/bin/get_tunnel_ports.py

useradd librarian
useradd tunnel
passwd -d tunnel

echo "deb http://archive.ubuntu.com/ubuntu quantal main universe restricted multiverse " > /etc/apt/sources.list
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 3B4FE6ACC0B21F32
apt-get update

apt-get -y install python-pip openssh-server dnsmasq nginx iproute openssl ssl-cert ca-certificates

pip install supervisor cherrypy requests pymongo simplejson jinja2

echo conf-dir=/etc/dnsmasq.d >> /etc/dnsmasq.conf
echo "daemon off;" >> /etc/nginx/nginx.conf

