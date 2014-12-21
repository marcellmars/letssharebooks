#!/bin/sh

apt-get update

mkdir -p /var/run/sshd

apt-get -y install openssh-server

useradd tunnel
passwd -d tunnel
