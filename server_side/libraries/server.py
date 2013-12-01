import os
import cherrypy
import requests
import glob
import simplejson
import pymongo
import zipfile
import traceback
import argparse
import libraries
import settings
from jinja2 import Environment, FileSystemLoader
from pymongo import MongoClient

#------------------------------------------------------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ENVIRONMENT = Environment(loader=FileSystemLoader('{}/templates'.format(CURRENT_DIR)))
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
        tmpl = ENVIRONMENT.get_template('index.html')
        return tmpl.render(app_name=settings.APP_NAME)

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
            print traceback.print_exc()
            return 'oooops, error!'

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
        page = req.get('page')
        query = req.get('query')
        return libraries.get_books(DB, page, query)

#------------------------------------------------------------------------------
# app entry point
#------------------------------------------------------------------------------
def start_app(env):
    if env:
        settings.ENV = settings.SERVER[env]
    try:
        global DB
        Mongo_client = MongoClient(settings.ENV['mongo_addr'],
                                   settings.ENV['mongo_port'])
        DB = Mongo_client[settings.DBNAME]
    except Exception, e:
        print 'unable to connect to mongodb!'
        return
    
    cherrypy.server.socket_host = settings.ENV['host']
    cherrypy.server.socket_port = settings.ENV['port']
    cherrypy.quickstart(Root(), '/', config=CONF)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='lsb server')
    parser.add_argument('--env', help="server environment (local|live|docker)")
    args = parser.parse_args()
    start_app(args.env)
