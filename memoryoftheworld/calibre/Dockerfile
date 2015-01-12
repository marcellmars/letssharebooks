FROM librarian/motw

ADD tgz/.config /home/developer/.config
ADD run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

ADD build_calibre.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_calibre.sh
RUN /usr/local/bin/build_calibre.sh

ADD calibre.conf /etc/supervisor/conf.d/

ENV HOME /home/developer
