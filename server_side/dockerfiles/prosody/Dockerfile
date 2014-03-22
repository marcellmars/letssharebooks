FROM ubuntu:latest

MAINTAINER Marcell Mars "https://github.com/marcellmars"

ADD build_prosody_in_ubuntu.sh /usr/local/bin/
RUN chmod +x /usr/local/bin/build_prosody_in_ubuntu.sh
RUN /usr/local/bin/build_prosody_in_ubuntu.sh

ADD prosody.cfg.lua /etc/prosody/prosody.cfg.lua
RUN chmod +rw /etc/prosody/prosody.cfg.lua
ADD wildcard_memoryoftheworld.org_20130714_combined.crt /etc/ssl/certs/wildcard_memoryoftheworld.org_20130714_combined.crt
ADD wildcard_memoryoftheworld.org_20130714.key /etc/ssl/private/wildcard_memoryoftheworld.org_20130714.key 

ENTRYPOINT ["/usr/bin/prosodyctl", "start"]
CMD []

