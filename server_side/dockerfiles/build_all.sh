#!/bin/sh

cd supervisor/
docker build -t librarian/supervisor .
cd ../ssh_tunnel/
docker build -t librarian/ssh_tunnel .
cd ../dnsmasq/
docker build -t librarian/dnsmasq .
cd ../nginx/
docker build -t librarian/nginx .
cd ../cherrypy/
docker build -t librarian/cherrypy .
cd ../library/
docker build -t librarian/library .
cd ../mongodb/
docker build -t librarian/mongodb .

