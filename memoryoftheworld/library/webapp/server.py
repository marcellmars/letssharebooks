import os
import cherrypy
import zipfile
import traceback
import argparse
import time
import libraries
import settings
import utils
import simplejson
import logging.config
from jinja2 import Environment, FileSystemLoader

#------------------------------------------------------------------------------

LOG = logging.getLogger('motw.' + __name__)
LOG.setLevel(logging.DEBUG)

#------------------------------------------------------------------------------

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
ENVIRONMENT = Environment(loader=FileSystemLoader(
    '{}/templates'.format(CURRENT_DIR)))

CONF = {'/': {'tools.gzip.on': True},
        '/static': {'tools.staticdir.on': True,
                    'tools.staticdir.dir': os.path.join(CURRENT_DIR, 'static'),
                    'tools.staticdir.content_types': {'js': 'application/javascript',
                                                      'css': 'text/css',
                                                      'gif': 'image/gif'
                                                      }
                    },
        '/images': {'tools.staticdir.on': True,
                    'tools.staticdir.dir': os.path.join(CURRENT_DIR, 'images'),
                    'tools.staticdir.content_types': {'svg': 'image/svg+xml',
                                                      'png': 'image/png',
                                                      'gif': 'image/gif'
                                                      }
                    },
        '/favicon.ico': {'tools.staticfile.on': True,
                         'tools.staticfile.filename': os.path.join(CURRENT_DIR,
                                                                   'static/connected.ico')
                         }
        }

#------------------------------------------------------------------------------
# Exposed resources
#------------------------------------------------------------------------------


class Root(object):

    #--------------------------------------------------------------------------
    # HTML pages
    #--------------------------------------------------------------------------

    @cherrypy.expose
    def index(self):
        '''
        Index page with default (grid) view
        '''
        tmpl = ENVIRONMENT.get_template('index.html')
        return tmpl.render(app_name=settings.APP_NAME)

    @cherrypy.expose
    def b(self, uuid):
        '''
        Single book page (permalink)
        '''
        book = libraries.get_book(cherrypy.db, uuid=uuid)
        if book:
            tmpl = ENVIRONMENT.get_template('book.html')
            print("BOOK_KEYS: {}".format(book.keys()))
            return tmpl.render(
                book=book,
                this_url='https://library.{}/b/{}'.format(
                    settings.ENV['domain_url'], uuid),
                app_name=settings.APP_NAME,
                )
        else:
            tmpl = ENVIRONMENT.get_template('404.html')
            return tmpl.render()

    #--------------------------------------------------------------------------
    # API
    #--------------------------------------------------------------------------

    @cherrypy.expose
    def upload_catalog(self, uploaded_file):
        '''
        End-point for uploading user catalogs
        '''
        try:
            res = libraries.handle_uploaded_catalog(cherrypy.db,
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
            res = libraries.handle_uploaded_catalog(cherrypy.db,
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
        return libraries.get_catalog(cherrypy.db, uuid)

    @cherrypy.expose
    def get_catalogs(self):
        '''
        Returns whole catalog
        '''
        return libraries.get_catalogs(cherrypy.db)

    @cherrypy.expose
    def book(self, uuid):
        '''
        Single book page
        '''
        book = libraries.get_book(cherrypy.db, uuid=uuid)
        return utils.ser2json(book)

    @cherrypy.expose
    #@cherrypy.tools.json_in()
    def get_books(self):
        '''
        Ajax backend for fetching books
        '''
        query = {}
        # this could easily be handled by using json_in decorator. however,
        # cherrypy testing is hard using the same decorator. hence...
        cl = cherrypy.request.headers.get('Content-Length')
        if cl:
            rawbody = cherrypy.request.body.read(int(cl))
            # parse json from request body
            params = simplejson.loads(rawbody)
            last_id = params.get('last_id')
            query = params.get('query')
        books = libraries.get_books(cherrypy.db, last_id, query)
        return books

    @cherrypy.expose
    def get_active_librarians(self):
        '''
        Ajax backend for fetching active librarians
        '''
        librarians = libraries.get_active_librarians(cherrypy.db)
        return librarians

    @cherrypy.expose
    def add_portable(self, url):
        '''
        Register portable library from remote url and insert its books
        '''
        return libraries.add_portable(cherrypy.db, url)

    @cherrypy.expose
    def portables(self):
        '''
        Returns all registered portable libraries
        '''
        return libraries.get_portables(cherrypy.db)

    @cherrypy.expose
    def remove_portable(self, url):
        '''
        Removes registered portable library with given lib_uuid
        Just for testing...
        '''
        return libraries.remove_portable(cherrypy.db, url)

    @cherrypy.expose
    @utils.jsonp
    def status(self):
        '''
        Return some status info
        '''
        return libraries.get_status(cherrypy.db)

    @cherrypy.expose
    def autocomplete(self):
        '''
        Returns pre-computed autocomplete data
        '''
        return libraries.get_autocomplete(cherrypy.db)

    @cherrypy.expose
    def ping_autocomplete(self):
        '''
        Returns pre-computed autocomplete data
        '''
        return libraries.calculate_autocomplete(cherrypy.db)

#------------------------------------------------------------------------------
# app entry point
#------------------------------------------------------------------------------


def db_connect():
    time_delay = 5
    max_attempts = 5
    num_attempts = 0
    while num_attempts <= max_attempts:
        try:
            cherrypy.db = utils.connect_to_db(settings.ENV)
            libraries.init(cherrypy.db)
            LOG.info('connected to db.')
            return
        except Exception:
            LOG.error('db connection error. will try again.', exc_info=True)
            time.sleep(time_delay)
        num_attempts += 1
    if num_attempts == max_attempts:
        LOG.error('db connection error. did not connect...')

#------------------------------------------------------------------------------


def start_app(env):
    settings.set_env(env)
    logging.basicConfig(level=logging.DEBUG)
    # tell cherrypy to call "connect" for each thread, when it starts up
    # result is one db connection per thread
    #cherrypy.engine.subscribe('start_thread', thread_connect)
    db_connect()
    cherrypy.server.socket_host = settings.ENV['host']
    cherrypy.server.socket_port = settings.ENV['port']
    cherrypy.quickstart(Root(), '/', config=CONF)

#------------------------------------------------------------------------------

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='lsb server')
    parser.add_argument('--env', help="server environment (local|live|docker)",
                        default='live')
    args = parser.parse_args()
    start_app(args.env)
