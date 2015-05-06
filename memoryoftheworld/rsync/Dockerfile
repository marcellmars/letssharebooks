FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

RUN  echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

ADD build_rsync.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_rsync.sh
RUN /usr/local/bin/build_rsync.sh

ADD rsyncd.conf /etc/rsyncd.conf
ADD rsync.conf /etc/supervisor/conf.d/
