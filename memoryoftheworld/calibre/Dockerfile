FROM librarian/motw

RUN  echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

RUN apt-get update \
    && apt-get -y install python \
                          wget \
                          xz-utils \
                          xdg-utils \
                          imagemagick \
                          openssh-client \
    && wget -nv -O- https://raw.githubusercontent.com/kovidgoyal/calibre/master/setup/linux-installer.py | PYTHONIOENCODING="utf-8" python -c "import sys; main=lambda:sys.stderr.write('Download failed\n'); exec(sys.stdin.read()); main()"

ADD run.sh /usr/local/bin/run.sh
RUN chmod +x /usr/local/bin/run.sh

ADD tgz/.config /root/.config/
ADD calibre.conf /etc/supervisor/conf.d/
ADD dnsmasq.local /etc/dnsmasq.d/local

ADD mock_calibre_library_0 /root/mock_calibre_library_0
ADD mock_calibre_library_1 /root/mock_calibre_library_1
