FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

#---- this is convenient setup with cache for local development ---------------
# RUN echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

RUN apt-get update \
    && apt-get -y install nginx

ADD nginx.conf /etc/supervisor/conf.d/
ADD gzip.conf /etc/nginx/conf.d/
ADD ssl.conf /etc/nginx/conf.d/

RUN mkdir -p /etc/nginx/docker_volumes
ADD etc_nginx.conf /etc/nginx/nginx.conf
ADD lsb_domains /etc/sites-enabled/lsb_domains

ADD lsb_domain.crt /etc/ssl/certs/lsb_domain.crt
ADD lsb_domain.key /etc/ssl/private/lsb_domain.key

ADD dhparams.pem /etc/ssl/private/dhparams.pem

ADD dnsmasq.local /etc/dnsmasq.d/local

RUN mkdir -p /var/www/cache
RUN chmod -R ugo+rwx /var/www/cache

ADD lsb_domains /etc/nginx/sites-enabled/

ADD static_web/ /var/www/