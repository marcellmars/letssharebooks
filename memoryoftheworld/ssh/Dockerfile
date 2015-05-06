FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

RUN  echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

ADD build_sshd.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_sshd.sh
RUN /usr/local/bin/build_sshd.sh

ADD sshd_config_tunnel /etc/ssh/
ADD ssh_tunnel.conf /etc/supervisor/conf.d/
ADD socket_server.conf /etc/supervisor/conf.d/

ADD socket_server.py /usr/local/bin/
RUN chmod +x /usr/local/bin/socket_server.py
