FROM librarian/cherrypy

MAINTAINER Marcell Mars "https://github.com/marcellmars" # version:002

RUN cp -a /var/www/

ADD library.conf /etc/supervisor/conf.d/

ENTRYPOINT ["/usr/local/bin/supervisord"]
# sudo docker build -t librarian/library .
