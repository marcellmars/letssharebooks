FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

#---- this is convenient setup with cache for local development ---------------
# RUN echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

RUN locale-gen en_US en_US.UTF-8 \
    && apt-get -y install openssl ssl-cert ca-certificates prosody \
    && pip install sleekxmpp \
                   dnspython \
                   pyasn1 \
                   pyasn1-modules \
    && mkdir -p /var/run/prosody \
    && chown -R prosody.prosody /var/run/prosody \
    && mkdir -p /var/lib/prosody/xmpp%2ememoryoftheworld%2eorg/accounts/ \
    && chown -R prosody.prosody /var/lib/prosody

ADD prosody.conf /etc/supervisor/conf.d/
ADD prosody.cfg.lua /etc/prosody/prosody.cfg.lua
RUN chmod +rw /etc/prosody/prosody.cfg.lua

ADD lsb_domain.crt /etc/prosody/certs/
ADD lsb_domain.key /etc/prosody/certs/ 

RUN chown prosody.prosody /etc/prosody/certs/lsb_domain.crt \
    && chown prosody.prosody /etc/prosody/certs/lsb_domain.key \
    && chmod 600 /etc/prosody/certs/lsb_domain.crt \
    && chmod 600 /etc/prosody/certs/lsb_domain.key

ADD biblibothekar.dat /var/lib/prosody/xmpp%2ememoryoftheworld%2eorg/accounts/

RUN chown prosody.prosody /var/lib/prosody/xmpp%2ememoryoftheworld%2eorg/accounts/biblibothekar.dat \
    && chmod -R 640 /var/lib/prosody/xmpp%2ememoryoftheworld%2eorg/accounts/biblibothekar.dat

ADD create_room.py /usr/local/bin/
RUN chmod +x /usr/local/bin/create_room.py
ADD .password /usr/local/bin/
ADD create_room.conf /etc/supervisor/conf.d/

ADD dnsmasq.local /etc/dnsmasq.d/local
