FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

ADD build_rsync.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_rsync.sh
RUN /usr/local/bin/build_rsync.sh

ADD rsyncd.conf /etc/rsyncd.conf
ADD rsync.conf /etc/supervisor/conf.d/
