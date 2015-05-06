FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

RUN  echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

ADD build_php5.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_php5.sh
RUN /usr/local/bin/build_php5.sh

ADD php5.conf /etc/supervisor/conf.d/
