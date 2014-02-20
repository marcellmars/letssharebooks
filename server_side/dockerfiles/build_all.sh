#!/bin/sh

cd supervisor/
#docker build -rm -no-cache -t librarian/supervisor .
#cd ../ssh_tunnel/
#docker build -rm -no-cache -t librarian/ssh_tunnel .
#cd ../dnsmasq/
#docker build -rm -no-cache -t librarian/dnsmasq .
cd ../nginx/
docker build -rm -no-cache -t librarian/nginx .
cd ../cherrypy/
docker build -rm -no-cache -t librarian/cherrypy .
cd ../library/
docker build -rm -no-cache -t librarian/library .
#cd ../mongodb/
#docker build -rm -no-cache -t librarian/mongodb .

