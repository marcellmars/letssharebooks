FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

#---- this is convenient setup with cache for local development ---------------
# RUN echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

RUN apt-get update \
    && apt-get -y install rsync

RUN mkdir /etc/rsync.d/ \
    && touch /etc/rsync.d/rsyncd.secrets \
    && chown root /etc/rsync.d/rsyncd.secrets

ADD rsyncd.conf /etc/rsyncd.conf
ADD rsync.conf /etc/supervisor/conf.d/
