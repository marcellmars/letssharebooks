FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

ADD build_php5.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_php5.sh
RUN /usr/local/bin/build_php5.sh

ADD php5.conf /etc/supervisor/conf.d/
