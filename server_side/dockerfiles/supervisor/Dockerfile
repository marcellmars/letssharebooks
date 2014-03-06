FROM ubuntu:latest

MAINTAINER Marcell Mars "https://github.com/marcellmars"

ADD supervisor/supervisord.conf /etc/

ADD ssh/sshd_config_tunnel /etc/ssh/
ADD ssh/ssh_tunnel.conf /etc/supervisor/conf.d/

ADD dnsmasq/dnsmasq.conf /etc/supervisor/conf.d/
ADD dnsmasq/current_ip.sh /usr/local/bin/

ADD nginx/lsb /etc/nginx/sites-enabled/
ADD nginx/nginx.conf /etc/supervisor/conf.d/

ADD libraries/get_tunnel_ports.conf /etc/supervisor/conf.d/
ADD libraries/get_tunnel_ports.py /usr/local/bin/
ADD libraries/get_tunnel_ports.sh /usr/local/bin/
ADD libraries/library /etc/nginx/sites-enabled/
ADD libraries/library.conf /etc/supervisor/conf.d/

ADD build_lsb_in_ubuntu.sh 
