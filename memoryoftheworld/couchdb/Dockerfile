FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

#---- this is convenient setup with cache for local development ---------------
# RUN echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

RUN apt-get update &&\
    apt-get install -y software-properties-common

RUN add-apt-repository ppa:couchdb/stable -y

RUN apt-get update &&\
    apt-get install -y couchdb

RUN apt-get clean && \
    rm -rf /var/lib/apt/lists/*


RUN mkdir /var/run/couchdb
RUN sed -i -r 's/;bind_address = 127.0.0.1/bind_address = 0.0.0.0/' /etc/couchdb/local.ini

#ADD create_couchdb_admin_user.sh /create_couchdb_admin_user.sh
ADD couchdb.conf /etc/supervisor/conf.d/
