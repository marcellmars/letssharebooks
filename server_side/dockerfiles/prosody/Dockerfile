FROM ubuntu:latest

MAINTAINER Marcell Mars "https://github.com/marcellmars"

ADD build_prosody_in_ubuntu.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_prosody_in_ubuntu.sh
RUN /usr/local/bin/build_prosody_in_ubuntu.sh

ADD prosody.cfg.lua /etc/prosody/prosody.cfg.lua
RUN chmod +rw /etc/prosody/prosody.cfg.lua
ADD wildcard_memoryoftheworld.org_20130714_combined.crt /etc/ssl/certs/wildcard_memoryoftheworld.org_20130714_combined.crt
ADD wildcard_memoryoftheworld.org_20130714.key /etc/ssl/private/wildcard_memoryoftheworld.org_20130714.key 
RUN chown prosody.prosody /etc/ssl/certs/wildcard_memoryoftheworld.org_20130714_combined.crt
RUN chown prosody.prosody /etc/ssl/private/wildcard_memoryoftheworld.org_20130714.key
RUN chmod g+r /etc/ssl/certs/wildcard_memoryoftheworld.org_20130714_combined.crt
RUN chmod g+r /etc/ssl/private/wildcard_memoryoftheworld.org_20130714.key

USER prosody
ENV __FLUSH_LOG 1
EXPOSE 5222 5269 5280 5347 5281
ENTRYPOINT ["/usr/bin/prosodyctl", "start"]
CMD []

