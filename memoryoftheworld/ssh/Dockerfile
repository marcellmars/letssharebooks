FROM ubuntu:latest

MAINTAINER Marcell Mars "https://github.com/marcellmars"

ADD build_sshd.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_sshd.sh
RUN /usr/local/bin/build_sshd.sh

ADD supervisord.conf /etc/

ADD sshd_config_tunnel /etc/ssh/
ADD ssh_tunnel.conf /etc/supervisor/conf.d/
