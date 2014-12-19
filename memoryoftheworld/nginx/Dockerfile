FROM ubuntu:latest

MAINTAINER Marcell Mars "https://github.com/marcellmars"

ADD build_nginx.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_nginx.sh
RUN /usr/local/bin/build_nginx.sh

ADD supervisord.conf /etc/
ADD nginx.conf /etc/supervisor/conf.d/
ADD dnsmasq.conf /etc/supervisor/conf.d/
ADD tunnels /etc/nginx/sites-enabled/
ADD dnsmasq.local /etc/dnsmasq.d/local
