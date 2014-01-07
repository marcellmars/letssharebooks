FROM librarian/dnsmasq

MAINTAINER Marcell Mars "https://github.com/marcellmars" # version:002

RUN apt-get -y install nginx 
RUN echo "daemon off;" >> /etc/nginx/nginx.conf

ADD lsb /etc/nginx/sites-enabled/
# hm. symlink didn't work
#RUN cd /etc/nginx/sites-enabled/
#RUN ln -sf ../sites-available/lsb .

ADD nginx.conf /etc/supervisor/conf.d/

#ENTRYPOINT ["/usr/local/bin/supervisord"]
# sudo docker build -t librarian/nginx .

