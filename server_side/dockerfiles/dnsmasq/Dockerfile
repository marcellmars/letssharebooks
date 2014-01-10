FROM librarian/ssh_tunnel

MAINTAINER Marcell Mars "https://github.com/marcellmars" # version:002

RUN apt-get -y install dnsmasq 
RUN echo conf-dir=/etc/dnsmasq.d >> /etc/dnsmasq.conf
ADD dnsmasq.conf /etc/supervisor/conf.d/
ADD current_ip.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/current_ip.sh

#ENTRYPOINT ["/usr/local/bin/supervisord"]
# sudo docker build -t librarian/dnsmasq .


