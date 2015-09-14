FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

#---- this is convenient setup with cache for local development ---------------
# RUN echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

ADD run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

ADD build_calibre.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_calibre.sh
RUN /usr/local/bin/build_calibre.sh

ADD tgz/.config /root/.config/
ADD calibre.conf /etc/supervisor/conf.d/
ADD print_log.conf /etc/supervisor/conf.d/
ADD dnsmasq.local /etc/dnsmasq.d/local

RUN pip install tailer
ADD print_log.py /usr/local/bin/
RUN chmod +x /usr/local/bin/print_log.py

ADD mock_calibre_library_0 /root/mock_calibre_library_0
ADD mock_calibre_library_1 /root/mock_calibre_library_1
