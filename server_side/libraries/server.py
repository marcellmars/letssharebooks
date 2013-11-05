import os
import cherrypy
import requests
import glob
import simplejson
from pymongo import MongoClient
import pymongo
from jinja2 import Environment, FileSystemLoader
import zipfile
import traceback
import libraries

#------------------------------------------------------------------------------

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
    @cherrypy.expose
    def index(self):
        '''
        Index page
        '''
        tmpl = ENV.get_template('index.html')
        return tmpl.render()

    @cherrypy.expose
    def upload_catalog(self, uploaded_file):
        '''
        End-point for uploading user catalogs
        '''
        try:
            # read temporary file and write to disk
            content = uploaded_file.file.read()
            out = open(uploaded_file.filename, "wb")
            out.write(content)
            out.close()
            # unzip file
            zfile = zipfile.ZipFile(uploaded_file.filename)
            content = zfile.read('library.json')
            # decode from json and import to database
            catalog = simplejson.loads(content)
            libraries.import_catalog(DB, catalog)
            return 'ok %s' % uploaded_file.filename
        except Exception, e:
            return 'oooops, error: %s' % traceback.print_exc()

    @cherrypy.expose
    def get_catalog(self, uuid):
        '''
        Returns whole catalog
        '''
        return libraries.get_catalog(DB, uuid)

    @cherrypy.expose
    @cherrypy.tools.json_in()
    def get_books(self):
        '''
        Ajax backend for fetching books
        '''
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
