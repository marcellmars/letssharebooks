#!/bin/sh

apt-get update

apt-get -y install iproute
pip install cherrypy requests pymongo simplejson jinja2
