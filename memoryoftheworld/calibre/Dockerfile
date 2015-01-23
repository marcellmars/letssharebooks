FROM librarian/motw

ADD run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

ADD build_calibre.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_calibre.sh
RUN /usr/local/bin/build_calibre.sh

ADD tgz/.config /home/developer/.config
RUN chmod -R ugo+rwx /home/developer/.config/calibre/
ADD calibre.conf /etc/supervisor/conf.d/
ADD print_log.conf /etc/supervisor/conf.d/
ADD dnsmasq.local /etc/dnsmasq.d/local

RUN pip install tailer
ADD print_log.py /usr/local/bin/
RUN chmod +x /usr/local/bin/print_log.py

ENV HOME /home/developer
