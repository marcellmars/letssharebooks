#! /bin/sh

# mongodb should be run before like this:
# sudo docker run -p 127.0.0.1:27017:27017 -name="mongodb" -t librarian/mongodb

rm -rf library/libraries
cp -a ../libraries/ library/libraries/

docker stop lsb
docker rm $(docker ps -a -q)
docker build -no-cache -t librarian/library library/
docker run -name="lsb" -p 127.0.0.1:4321:4321 -link mongodb:mongodb -t librarian/library&
sleep 4
echo bind-interfaces > /etc/dnsmasq.d/local
echo listen-address=127.0.0.1 >> /etc/dnsmasq.d/local
echo server=8.8.8.8 >> /etc/dnsmasq.d/local
echo address=/dokr/`docker inspect -format '{{ .NetworkSettings.IPAddress }}' lsb` >> /etc/dnsmasq.d/local

if [ "`head -n 1 /etc/resolv.conf`" != "nameserver 127.0.0.1" ]; then
    echo "nameserver 127.0.0.1\n$(cat /etc/resolv.conf)" > /etc/resolv.conf
fi
service dnsmasq restart
