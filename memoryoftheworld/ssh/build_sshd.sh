#!/bin/sh

mkdir -p /var/log/supervisor
mkdir -p /var/run/supervisor
locale-gen en_US en_US.UTF-8

apt-get update

apt-get -y install python-pip
pip install supervisor
mkdir -p /var/run/sshd

apt-get -y install openssh-server

useradd tunnel
passwd -d tunnel
