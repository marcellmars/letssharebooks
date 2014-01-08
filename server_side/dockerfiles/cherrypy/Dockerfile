FROM librarian/nginx

MAINTAINER Marcell Mars "https://github.com/marcellmars" # version:002

RUN pip install cherrypy requests pymongo simplejson jinja2

ENTRYPOINT ["/usr/local/bin/supervisord"]
# sudo docker build -t librarian/cherrypy .
