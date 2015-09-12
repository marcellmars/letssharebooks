FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

#---- this is convenient setup with cache for local development ---------------
# RUN echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

RUN apt-get update \
    && mkdir -p /var/run/sshd \
    && apt-get -y install openssh-server

RUN useradd tunnel \
    && passwd -d tunnel
   
ADD sshd_config_tunnel /etc/ssh/
ADD ssh_tunnel.conf /etc/supervisor/conf.d/
ADD socket_server.conf /etc/supervisor/conf.d/

ADD socket_server.py /usr/local/bin/
RUN chmod +x /usr/local/bin/socket_server.py
