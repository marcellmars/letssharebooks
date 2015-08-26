#!/bin/sh

apt-get update

apt-get -y install iproute build-essential python-dev libxml2-dev
pip install cherrypy requests simplejson jinja2 lxml
pip install https://github.com/mongodb/mongo-python-driver/archive/3.0.1.tar.gz
