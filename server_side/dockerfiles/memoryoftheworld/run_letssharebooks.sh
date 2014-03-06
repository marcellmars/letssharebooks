#! /bin/sh

docker stop lsb
docker rm $(docker ps -a -q)
docker run -i -t -dns=127.0.0.1 -name lsb -v /home/m/devel/letssharebooks/server_side/libraries:/var/www/libraries:ro -entrypoint /bin/bash --link mongodb:mongodb librarian/memoryoftheworld

