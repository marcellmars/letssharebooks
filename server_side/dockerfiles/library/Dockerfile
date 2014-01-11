FROM librarian/cherrypy

MAINTAINER Marcell Mars "https://github.com/marcellmars" # version:002

RUN mkdir -p /var/www/
ADD libraries/ /var/www/libraries/

ADD library /etc/nginx/sites-enabled/
ADD library.conf /etc/supervisor/conf.d/

RUN useradd librarian

ENTRYPOINT ["/usr/local/bin/supervisord"]
# sudo docker build -t librarian/library .
