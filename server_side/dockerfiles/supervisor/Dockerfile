FROM ubuntu:latest

MAINTAINER Marcell Mars "https://github.com/marcellmars"

RUN mkdir -p /var/log/supervisor
RUN mkdir -p /var/run/supervisor
RUN locale-gen en_US en_US.UTF-8

RUN echo "deb http://archive.ubuntu.com/ubuntu quantal main universe restricted multiverse " > /etc/apt/sources.list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 3B4FE6ACC0B21F32
RUN apt-get update

RUN apt-get -y install python-pip
RUN pip install supervisor
ADD supervisord.conf /etc/supervisord.conf

# sudo docker build -t librarian/ssh_tunnel .

