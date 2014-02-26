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
                                                      }}}

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
        tmpl = ENVIRONMENT.get_template('book.html')
        return tmpl.render(book=book)

    @cherrypy.expose
    def upload_catalog(self, uploaded_file):
        '''
        End-point for uploading user catalogs
        '''
        try:
            res = libraries.handle_uploaded_catalog(
                uploaded_file,
                cherrypy.thread_data.db)
            return res
        except KeyError, e:
            return 'oooops, error: %s' % e
        except zipfile.BadZipfile, e:
            return 'oooops, error: %s' % e
        except simplejson.JSONDecodeError, e:
            return 'oooops, error: JSONDecode -- %s' % e
        except Exception, e:
            print traceback.print_exc()
            return 'oooops, error!'

    @cherrypy.expose
    def get_catalog(self, uuid):
        '''
        Returns whole catalog
        '''
        return libraries.get_catalog(cherrypy.thread_data.db, uuid)

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
def thread_connect(thread_index, env='local'):
    '''
    Creates a db connection and stores it in the current thread
    http://tools.cherrypy.org/wiki/Databases
    '''
    if env:
        settings.ENV = settings.SERVER[env]
        try:
            Mongo_client = MongoClient(settings.ENV['mongo_addr'],
                                       settings.ENV['mongo_port'])
            cherrypy.thread_data.db = Mongo_client[settings.DBNAME]
        except Exception as e:
            print 'unable to connect to mongodb!'
                
def start_app(env):
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
                        required=True)
    args = parser.parse_args()
    start_app(args.env)
