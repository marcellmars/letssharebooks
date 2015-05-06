FROM ubuntu:latest

MAINTAINER Marcell Mars "https://github.com/marcellmars"

RUN  echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

ADD build_motw_base.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_motw_base.sh
RUN /usr/local/bin/build_motw_base.sh

ADD supervisord.conf /etc/
ADD dnsmasq.conf /etc/supervisor/conf.d/
ADD dnsmasq.local /etc/dnsmasq.d/local
