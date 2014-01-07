FROM librarian/supervisor

MAINTAINER Marcell Mars "https://github.com/marcellmars"

RUN mkdir -p /var/run/sshd

RUN apt-get -y install openssh-server 
ADD sshd_config_tunnel /etc/ssh/
ADD ssh_tunnel.conf /etc/supervisor/conf.d/

RUN useradd tunnel
RUN passwd -d tunnel

# sudo docker build -t librarian/ssh_tunnel .

