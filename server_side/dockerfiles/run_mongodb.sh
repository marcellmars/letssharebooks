#!/bin/sh

docker stop mongodb
docker rm $(sudo docker ps -a -q)
docker run -d -dns=127.0.0.1 -p 127.0.0.1:27017:27017 -name mongodb -t librarian/mongodb
