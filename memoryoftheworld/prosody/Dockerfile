FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

RUN  echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

ADD build_prosody.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_prosody.sh
RUN /usr/local/bin/build_prosody.sh

ADD prosody.conf /etc/supervisor/conf.d/
ADD prosody.cfg.lua /etc/prosody/prosody.cfg.lua
RUN chmod +rw /etc/prosody/prosody.cfg.lua
ADD wildcard_memoryoftheworld.org_20130714_combined.crt /etc/prosody/certs/wildcard_memoryoftheworld.org_20130714_combined.crt
ADD wildcard_memoryoftheworld.org_20130714.key /etc/prosody/certs/wildcard_memoryoftheworld.org_20130714.key 
RUN chown prosody.prosody /etc/prosody/certs/wildcard_memoryoftheworld.org_20130714_combined.crt
RUN chown prosody.prosody /etc/prosody/certs/wildcard_memoryoftheworld.org_20130714.key
RUN chmod 600 /etc/prosody/certs/wildcard_memoryoftheworld.org_20130714_combined.crt
RUN chmod 600 /etc/prosody/certs/wildcard_memoryoftheworld.org_20130714.key

ADD biblibothekar.dat /var/lib/prosody/xmpp%2ememoryoftheworld%2eorg/accounts/
RUN chown prosody.prosody /var/lib/prosody/xmpp%2ememoryoftheworld%2eorg/accounts/biblibothekar.dat
RUN chmod -R 640 /var/lib/prosody/xmpp%2ememoryoftheworld%2eorg/accounts/biblibothekar.dat

ADD create_room.py /usr/local/bin/
RUN chmod +x /usr/local/bin/create_room.py
ADD .password /usr/local/bin/
ADD create_room.conf /etc/supervisor/conf.d/

RUN echo "127.0.0.1 xmpp.memoryoftheworld.org conference.memoryoftheworld.org" >> /etc/hosts

ADD dnsmasq.local /etc/dnsmasq.d/local
