FROM ubuntu:latest

MAINTAINER Marcell Mars "https://github.com/marcellmars"

#---- this is convenient setup with cache for local development ---------------
# RUN echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

RUN locale-gen en_US en_US.UTF-8

RUN apt-get update \
    && apt-get -y install python-pip \
                       dnsmasq-base \
    && pip install supervisor \
                   supervisor-stdout \
                   tailer \
    && echo conf-dir=/etc/dnsmasq.d >> /etc/dnsmasq.conf \
    && echo user=root >> /etc/dnsmasq.conf

ADD print_log.py /usr/local/bin/
RUN chmod +x /usr/local/bin/print_log.py

ADD supervisord.conf /etc/ 
ADD dnsmasq.conf /etc/supervisor/conf.d/
ADD dnsmasq.local /etc/dnsmasq.d/local
