FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

#---- this is convenient setup with cache for local development ---------------
# RUN echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

RUN apt-get update \
    && apt-get -y install vsftpd libpam-pwdfile apache2-utils

RUN mkdir /etc/vsftpd \
    && mkdir -p /var/run/vsftpd/empty \
    && mkdir -p /tmp/anon \
    && useradd --home /home --gid nogroup -m --shell /bin/false vsftpd

RUN chmod -R 777 /tmp/anon
ADD vsftpd.pam /etc/pam.d/vsftpd
ADD etc_vsftpd.conf /etc/vsftpd.conf

ADD ftp.conf /etc/supervisor/conf.d/
ADD motw.crt /etc/ssl/certs/motw.crt
ADD motw.key /etc/ssl/private/motw.key
