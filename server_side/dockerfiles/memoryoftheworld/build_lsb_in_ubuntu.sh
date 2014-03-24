#!/bin/sh

locale-gen en_US en_US.UTF-8

dpkg-divert --local --rename --add /sbin/initctl
ln -sf /bin/true /sbin/initctl

mkdir -p /var/log/supervisor/
mkdir -p /var/run/supervisor/
mkdir -p /var/run/sshd/
mkdir -p /var/www/
mkdir -p /etc/ssl/certs/
mkdir -p /etc/ssl/private/

chmod ug+rx /usr/local/bin/current_ip.sh
chmod ug+rx /usr/local/bin/get_tunnel_ports.sh
chmod ug+rx /usr/local/bin/get_tunnel_ports.py

useradd librarian
useradd tunnel
passwd -d tunnel

echo "deb http://archive.ubuntu.com/ubuntu quantal main universe restricted multiverse " > /etc/apt/sources.list
apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 3B4FE6ACC0B21F32
apt-get update

apt-get -y install python-pip openssh-server dnsmasq nginx iproute openssl ssl-cert ca-certificates mysql-client mysql-server php5-curl php5-gd php5-intl php-pear php5-imagick php5-imap php5-mcrypt php5-memcache php5-ming php5-ps php5-pspell php5-recode php5-snmp php5-sqlite php5-tidy php5-xmlrpc php5-xsl

pip install supervisor cherrypy requests pymongo simplejson jinja2

echo conf-dir=/etc/dnsmasq.d >> /etc/dnsmasq.conf
echo "daemon off;" >> /etc/nginx/nginx.conf

# mysql
sed -i -e"s/^bind-address\s*=\s*127.0.0.1/bind-address = 0.0.0.0/" /etc/mysql/my.cnf

# php-fpm config from https://github.com/eugeneware/docker-wordpress-nginx/blob/master/Dockerfile
sed -i -e "s/;cgi.fix_pathinfo=1/cgi.fix_pathinfo=0/g" /etc/php5/fpm/php.ini
sed -i -e "s/upload_max_filesize\s*=\s*2M/upload_max_filesize = 100M/g" /etc/php5/fpm/php.ini
sed -i -e "s/post_max_size\s*=\s*8M/post_max_size = 100M/g" /etc/php5/fpm/php.ini
sed -i -e "s/;daemonize\s*=\s*yes/daemonize = no/g" /etc/php5/fpm/php-fpm.conf
find /etc/php5/cli/conf.d/ -name "*.ini" -exec sed -i -re 's/^(\s*)#(.*)/\1;\2/g' {} \;
