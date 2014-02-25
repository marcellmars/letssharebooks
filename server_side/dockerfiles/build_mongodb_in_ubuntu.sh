#!/bin/sh

apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 7F0CEB10
echo 'deb http://downloads-distro.mongodb.org/repo/ubuntu-upstart dist 10gen' | tee /etc/apt/sources.list.d/10gen.list
dpkg-divert --local --rename --add /sbin/initctl
ln -s /bin/true /sbin/initctl
rm /var/lib/apt/lists/* -vf
apt-get update
apt-get install mongodb-10gen
mkdir -p /data/db
