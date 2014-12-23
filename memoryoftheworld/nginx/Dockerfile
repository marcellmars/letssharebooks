FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

ADD build_nginx.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_nginx.sh
RUN /usr/local/bin/build_nginx.sh

ADD nginx.conf /etc/supervisor/conf.d/
ADD tunnels /etc/nginx/sites-enabled/
ADD library /etc/nginx/sites-enabled/

ADD wildcard_memoryoftheworld.org_20130714_combined.crt /etc/ssl/certs/
ADD wildcard_memoryoftheworld.org_20130714.key /etc/ssl/private/
