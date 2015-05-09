FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

RUN  echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

ADD build_nginx.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_nginx.sh
RUN /usr/local/bin/build_nginx.sh

ADD nginx.conf /etc/supervisor/conf.d/
ADD gzip.conf /etc/nginx/conf.d/

ADD wildcard_memoryoftheworld.org_20130714_combined.crt /etc/ssl/certs/
ADD wildcard_memoryoftheworld.org_20130714.key /etc/ssl/private/

ADD dnsmasq.local /etc/dnsmasq.d/local

RUN mkdir -p /var/www/cache
RUN chmod -R ugo+rwx /var/www/cache