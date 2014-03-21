#!/bin/sh

locale-gen en_US en_US.UTF-8

echo "deb http://archive.ubuntu.com/ubuntu quantal main universe restricted multiverse " > /etc/apt/sources.list
apt-get update

apt-get -y install openssl ssl-cert ca-certificates prosody

mkdir -p /var/run/prosody
chown prosody.prosody /var/run/prosody

mkdir -p /etc/ssl/certs/
mkdir -p /etc/ssl/private/
