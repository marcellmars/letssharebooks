FROM librarian/nginx

MAINTAINER Marcell Mars "https://github.com/marcellmars" # version:002

RUN apt-get -y install iproute2 
RUN pip install cherrypy requests pymongo simplejson jinja2

ADD get_tunnel_ports.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/get_tunnel_ports.sh

ADD get_tunnel_ports.py /usr/local/bin/
ADD get_tunnel_ports.conf /etc/supervisor/conf.d/

#ENTRYPOINT ["/usr/local/bin/supervisord"]
# sudo docker build -t librarian/cherrypy .
