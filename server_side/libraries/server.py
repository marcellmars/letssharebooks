import os
import cherrypy
import requests
import glob
import simplejson
from pymongo import MongoClient
import pymongo
from jinja2 import Environment, FileSystemLoader
import libraries

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ENV = Environment(loader=FileSystemLoader('{}/templates'.format(CURRENT_DIR)))
CONF = {'/static': {'tools.staticdir.on': True,
                    'tools.staticdir.dir': os.path.join(CURRENT_DIR, 'static'),
                    'tools.staticdir.content_types': {'js': 'application/javascript',
                                                      'css': 'text/css',
                                                      'gif': 'image/gif'
                                                      }}}
DB = None

#------------------------------------------------------------------------------
# Exposed resources
#------------------------------------------------------------------------------
class Root(object):
    # basic index page
    @cherrypy.expose
    def index(self):
        tmpl = ENV.get_template('index.html')
        return tmpl.render()

    # ajax backend for fetching books
    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def render_page(self):
        json_books = JSONBooks()
        json_request = cherrypy.request.json
        return json_books.get_metadata(
            json_request['start'],
            json_request['offset'],
            json_request['query'].encode('utf-8'))

    # end-point for uploading user catalogs
    @cherrypy.expose
    def upload_catalog(self, uploaded_file):
        try:
            content = uploaded_file.file.read()
            catalog = simplejson.loads(content)
            libraries.import_catalog(DB, catalog)
            return 'ok %s' % uploaded_file.filename
        except Exception, e:
            return 'oooops, error: %s' % e.message

    @cherrypy.expose
    def get_catalog(self, uuid):
        return libraries.get_catalog(DB, uuid)

    # ajax backend for fetching books
    @cherrypy.expose
    @cherrypy.tools.json_in()
    def get_books(self):
        req = cherrypy.request.json
        return libraries.get_books(DB, req['page'])

#------------------------------------------------------------------------------
# app entry point
#------------------------------------------------------------------------------
def start_app(port=4321, production=False):
    mongo_addr = '127.0.0.1'
    mongo_port = 27017
    PREFIX_URL = 'http://www'
    if production == 'live':
        mongo_addr = 'localhost'
        mongo_port = 27017
        PREFIX_URL = 'https://www'
    elif production == 'docker':
        mongo_addr = '172.17.42.1'
        mongo_port = 27017
        PREFIX_URL = 'http://www'

    try:
        global DB
        Mongo_client = MongoClient(mongo_addr, mongo_port)
        DB = Mongo_client.letssharebooks
    except Exception, e:
        print 'unable to connect to mongodb!'
        return
    
    cherrypy.server.socket_host = '0.0.0.0'
    cherrypy.server.socket_port = 4321
    cherrypy.quickstart(Root(), '/', config=CONF)

if __name__ == '__main__':
    start_app()
