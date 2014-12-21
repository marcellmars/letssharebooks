#!/bin/sh

apt-get update

apt-get -y install nginx
echo "daemon off;" >> /etc/nginx/nginx.conf
