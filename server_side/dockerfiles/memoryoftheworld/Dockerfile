FROM ubuntu:latest

MAINTAINER Marcell Mars "https://github.com/marcellmars"

ADD build_lsb_in_ubuntu.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_lsb_in_ubuntu.sh
RUN /usr/local/bin/build_lsb_in_ubuntu.sh

ADD supervisor/supervisord.conf /etc/supervisord.conf
ADD supervisor/supervisord.conf /etc/supervisord.conf

ADD ssh/sshd_config_tunnel /etc/ssh/
ADD ssh/ssh_tunnel.conf /etc/supervisor/conf.d/

#ADD dnsmasq/dnsmasq_docker.conf /etc/supervisor/conf.d/
#ADD dnsmasq/dnsmasq_memoryoftheworld.conf /etc/supervisor/conf.d/

ADD dnsmasq/current_ip.sh /usr/local/bin/

#ADD nginx/tunnel_docker /etc/nginx/sites-enabled/
ADD nginx/tunnel_memoryoftheworld /etc/nginx/sites-enabled/
ADD nginx/candy /etc/nginx/sites-enabled/
ADD nginx/bosh /etc/nginx/sites-enabled/

ADD nginx/nginx.conf /etc/supervisor/conf.d/
ADD nginx/set_prosody_ip.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/set_prosody_ip.sh

ADD libraries/get_tunnel_ports.sh /usr/local/bin/
ADD libraries/get_tunnel_ports.py /usr/local/bin/

#ADD libraries/get_tunnel_ports_docker.conf /etc/supervisor/conf.d/
ADD libraries/get_tunnel_ports_memoryoftheworld.conf /etc/supervisor/conf.d/

#ADD libraries/library_docker /etc/nginx/sites-enabled/
ADD libraries/library_memoryoftheworld /etc/nginx/sites-enabled/

#ADD libraries/library_docker.conf /etc/supervisor/conf.d/
ADD libraries/library_memoryoftheworld.conf /etc/supervisor/conf.d/

ADD wordpress/wordpress.conf /etc/supervisor/conf.d/
ADD wordpress/wordpress     /etc/supervisor/conf.d/

##
# certificates should be already in place on docker host
##

ADD wildcard_memoryoftheworld.org_20130714_combined.crt /etc/ssl/certs/wildcard_memoryoftheworld.org_20130714_combined.crt
ADD wildcard_memoryoftheworld.org_20130714.key /etc/ssl/private/wildcard_memoryoftheworld.org_20130714.key 

ENTRYPOINT ["/usr/local/bin/supervisord"]
CMD []
