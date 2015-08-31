FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

RUN  echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

RUN apt-get update \
    && apt-get -y install nginx \
    && echo "daemon off;" >> /etc/nginx/nginx.conf

ADD nginx.conf /etc/supervisor/conf.d/
ADD gzip.conf /etc/nginx/conf.d/
ADD ssl.conf /etc/nginx/conf.d/

ADD dhparams.pem /etc/ssl/private/

ADD wildcard_memoryoftheworld.org_20130714_combined.crt /etc/ssl/certs/
ADD wildcard_memoryoftheworld.org_20130714.key /etc/ssl/private/

ADD otpisane.org.key /etc/ssl/private/
ADD otpisane.org.crt /etc/ssl/certs/
ADD woosign_bundle.crt /etc/ssl/private/

ADD dnsmasq.local /etc/dnsmasq.d/local

RUN mkdir -p /var/www/cache
RUN chmod -R ugo+rwx /var/www/cache