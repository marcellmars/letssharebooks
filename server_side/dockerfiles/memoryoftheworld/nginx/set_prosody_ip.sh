#!/bin/sh

sed -i 's,PROSODY_PORT_5281_TCP_ADDR,'"$PROSODY_PORT_5281_TCP_ADDR"',' /etc/nginx/sites-enabled/bosh
