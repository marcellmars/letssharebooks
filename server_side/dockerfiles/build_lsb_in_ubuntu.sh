#!/bin/sh

mkdir -p /var/log/supervisor
mkdir -p /var/run/supervisor
locale-gen en_US en_US.UTF-8

echo "deb http://archive.ubuntu.com/ubuntu quantal main universe restricted multiverse " > /etc/apt/sources.list
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 3B4FE6ACC0B21F32
apt-get update

apt-get -y install python-pip
pip install supervisor
cp /var/host_files/supervisor/supervisord.conf /etc/supervisord.conf
mkdir -p /var/run/sshd

apt-get -y install openssh-server 
cp /var/host_files/ssh_tunnel/sshd_config_tunnel /etc/ssh/
cp /var/host_files/ssh_tunnel/ssh_tunnel.conf /etc/supervisor/conf.d/

useradd tunnel
passwd -d tunnel

apt-get -y install dnsmasq 
echo conf-dir=/etc/dnsmasq.d >> /etc/dnsmasq.conf
cp /var/host_files/dnsmasq/dnsmasq.conf /etc/supervisor/conf.d/
cp /var/host_files/dnsmasq/current_ip.sh /usr/local/bin/
chmod +x /usr/local/bin/current_ip.sh

apt-get -y install nginx 
echo "daemon off;" >> /etc/nginx/nginx.conf

cp /var/host_files/nginx/lsb /etc/nginx/sites-enabled/
cp /var/host_files/nginx/nginx.conf /etc/supervisor/conf.d/

apt-get -y install iproute
pip install cherrypy requests pymongo simplejson jinja2

cp /var/host_files/cherrypy/get_tunnel_ports.sh /usr/local/bin/
chmod +x /usr/local/bin/get_tunnel_ports.sh

cp /var/host_files/cherrypy/get_tunnel_ports.py /usr/local/bin/
cp /var/host_files/cherrypy/get_tunnel_ports.conf /etc/supervisor/conf.d/

mkdir -p /var/www/
cp /var/host_files/library/libraries/ /var/www/libraries/

cp /var/host_files/library/library /etc/nginx/sites-enabled/
cp /var/host_files/library/library.conf /etc/supervisor/conf.d/

useradd librarian

