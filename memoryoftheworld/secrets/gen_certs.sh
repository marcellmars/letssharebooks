#!/bin/sh

rm templates/*
cp templates/originals/* templates/
touch templates/index.txt
echo '01' > templates/serial.txt

openssl req \
        -x509 \
        -config templates/openssl-ca.cnf \
        -subj "/C=US/ST=Maryland/L=Baltimore/O=Memory of the World/OU=Server Research Department/CN=javnaknjiznica.org" \
        -newkey rsa:4096 -sha256 \
        -nodes \
        -out templates/cacert.pem \
        -outform PEM

openssl req \
        -config templates/openssl-server.cnf \
        -newkey rsa:2048 -sha256 \
        -nodes \
        -subj "/C=US/ST=Maryland/L=Baltimore/O=Memory of the World/OU=Server Research Department/CN=javnaknjiznica.org" \
        -out templates/servercert.csr \
        -outform PEM

openssl ca \
        -config templates/openssl-ca_ext.cnf \
        -policy signing_policy \
        -extensions signing_req \
        -out templates/servercert.pem \
        -infiles templates/servercert.csr

mv serverkey.pem javnaknjiznica.org.key
mv templates/servercert.pem javnaknjiznica.org.crt
rm templates/*
echo "javnaknjiznica.org.key & javnaknjiznica.org.crt done!"
