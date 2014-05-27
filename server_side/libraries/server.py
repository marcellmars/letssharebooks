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
import utils
import simplejson
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
                                                      }},
        '/images': {'tools.staticdir.dir': os.path.join(CURRENT_DIR, 'images'),
                    'tools.staticdir.content_types': {'svg': 'image/svg+xml',
                                                      'png': 'image/png',
                                                      'gif': 'image/gif'
                                                      }},
        '/favicon.ico': {'tools.staticfile.on': True,
                         'tools.staticfile.filename': os.path.join(CURRENT_DIR, 'static/connected.ico')}
        }

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
    def book(self, uuid):
        '''
        Single book page
        '''
        book = libraries.get_book(cherrypy.thread_data.db, uuid=uuid)
        return book

    @cherrypy.expose
    def upload_catalog(self, uploaded_file):
        '''
        End-point for uploading user catalogs
        '''
        try:
            res = libraries.handle_uploaded_catalog(cherrypy.thread_data.db,
                                                    uploaded_file)
            return res
        except zipfile.BadZipfile as e:
            return 'Error during file unzipping :: {}'.format(e)
        except simplejson.JSONDecodeError as e:
            return 'Error in JSONDecode :: {}'.format(e)
        except Exception as e:
            print traceback.print_exc()
            return 'oooops, error!'

    @cherrypy.expose
    def upload_catalog_json(self, uploaded_file):
        '''
        End-point for uploading user catalogs in json format
        Mostly for testing purposes
        '''
        try:
            res = libraries.handle_uploaded_catalog(cherrypy.thread_data.db,
                                                    uploaded_file,
                                                    zipped=False)
            return res
        except simplejson.JSONDecodeError as e:
            return 'Error in JSONDecode :: {}'.format(e)
        except Exception as e:
            print traceback.print_exc()
            return 'oooops, error!'

    @cherrypy.expose
    def get_catalog(self, uuid):
        '''
        Returns whole catalog
        '''
        return libraries.get_catalog(cherrypy.thread_data.db, uuid)

    @cherrypy.expose
    def get_catalogs(self):
        '''
        Returns whole catalog
        '''
        return libraries.get_catalogs(cherrypy.thread_data.db)

    @cherrypy.expose
    #@cherrypy.tools.json_in()
    def get_books(self):
        '''
        Ajax backend for fetching books
        '''
        # this could easily be handled by using json_in decorator. however,
        # cherrypy testing is hard using the same decorator. hence...
        cl = cherrypy.request.headers['Content-Length']
        rawbody = cherrypy.request.body.read(int(cl))
        # parse json from request body
        params = simplejson.loads(rawbody)
        page = params.get('page')
        query = params.get('query')
        books = libraries.get_books(cherrypy.thread_data.db, page, query)
        return books

#------------------------------------------------------------------------------
# app entry point
#------------------------------------------------------------------------------

def thread_connect(thread_index):
    '''
    Creates a db connection and stores it in the current thread
    http://tools.cherrypy.org/wiki/Databases
    '''
    cherrypy.thread_data.db = utils.connect_to_db(settings.ENV)

#------------------------------------------------------------------------------

def start_app(env):
    settings.ENV = settings.SERVER[env]
    # tell cherrypy to call "connect" for each thread, when it starts up
    # result is one db connection per thread
    cherrypy.engine.subscribe('start_thread', thread_connect)
    cherrypy.server.socket_host = settings.ENV['host']
    cherrypy.server.socket_port = settings.ENV['port']
    cherrypy.quickstart(Root(), '/', config=CONF)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='lsb server')
    parser.add_argument('--env', help="server environment (local|live|docker)",
                        default='docker')
    args = parser.parse_args()
    start_app(args.env)
