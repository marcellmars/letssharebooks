#!/bin/sh

apt-get update
apt-get -y install rsync

mkdir /etc/rsync.d/
touch /etc/rsync.d/rsyncd.secrets
chown root /etc/rsync.d/rsyncd.secrets
