FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

ADD build_motw_base.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_motw_base.sh
RUN /usr/local/bin/build_motw_base.sh

ADD supervisord.conf /etc/
ADD dnsmasq.conf /etc/supervisor/conf.d/
ADD dnsmasq.local /etc/dnsmasq.d/local
