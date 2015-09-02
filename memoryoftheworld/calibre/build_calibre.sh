#!/bin/sh

##

# export uid=1000 gid=1000
# mkdir -p /home/developer
# echo "developer:x:${uid}:${gid}:Developer,,,:/home/developer:/bin/bash" >> /etc/passwd
# echo "developer:x:${uid}:" >> /etc/group
# echo "developer ALL=(ALL) NOPASSWD: ALL" > /etc/sudoers.d/developer
# chmod 0440 /etc/sudoers.d/developer
# chown ${uid}:${gid} -R /home/developer/
chmod +x /usr/local/bin/run.sh

apt-get update

apt-get -y install python wget xz-utils xdg-utils imagemagick openssh-client
wget -nv -O- https://raw.githubusercontent.com/kovidgoyal/calibre/master/setup/linux-installer.py | PYTHONIOENCODING="utf-8" python -c "import sys; main=lambda:sys.stderr.write('Download failed\n'); exec(sys.stdin.read()); main()"

