FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

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

ADD marcell.dat /var/lib/prosody/xmpp%2ememoryoftheworld%2eorg/accounts/
RUN chmod -R 640 /var/lib/prosody/xmpp%2ememoryoftheworld%2eorg/accounts/marcell.dat
RUN chown prosody.prosody /var/lib/prosody/xmpp%2ememoryoftheworld%2eorg/accounts/marcell.dat
