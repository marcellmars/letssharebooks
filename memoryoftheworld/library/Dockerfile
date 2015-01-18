FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

ADD build_library.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_library.sh
RUN /usr/local/bin/build_library.sh

ADD dnsmasq.local /etc/dnsmasq.d/local
ADD library.conf /etc/supervisor/conf.d/
ADD get_tunnel_ports.conf /etc/supervisor/conf.d/
ADD get_tunnel_ports.py /usr/local/bin/
RUN useradd librarian
