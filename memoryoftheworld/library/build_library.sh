#!/bin/sh

apt-get update

apt-get -y install iproute build-essential python-dev python-lxml
pip install cherrypy requests simplejson jinja2
pip install https://github.com/mongodb/mongo-python-driver/archive/3.0.1.tar.gz
