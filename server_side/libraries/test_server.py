#------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
import cherrypy

from server import Root, thread_connect
from cptestcase import BaseCherryPyTestCase
import simplejson
import requests
from pymongo import MongoClient
import libraries
import settings
import utils

#------------------------------------------------------------------------------
            
def setUpModule():
    # use test environment
    settings.ENV = settings.SERVER['test']
    cherrypy.tree.mount(Root(), '/')
    cherrypy.engine.subscribe('start_thread', thread_connect)
    cherrypy.engine.start()
setup_module = setUpModule

def tearDownModule():
    cherrypy.engine.exit()
teardown_module = tearDownModule

#------------------------------------------------------------------------------

class TestCherryPyApp(BaseCherryPyTestCase):

    def setUp(self):
        
        def fake_get_active_tunnels():
            '''
            fake active tunnels for tests
            '''
            return [12345]

        # fake get_active_tunnels call
        libraries.get_active_tunnels = fake_get_active_tunnels
        # clear db
        self.db = utils.connect_to_db(settings.ENV)
        utils.remove_all_data(self.db)
        

    def test_index(self):
        response = self.request('/')
        self.assertEqual(response.output_status, '200 OK')
        self.assertGreater(response.body[0].find('memory of the world'), -1)

    def test_upload_catalog(self):
        # this library should be uploaded with no problems
        with open('test/library.json', 'rt') as f:
            r = self.request('/upload_catalog_json', method='POST',
                             uploaded_file=f.read())
            self.assertEqual(r.body, ['3b876484-0dbd-461f-935a-e58b08c06547'])

        # bad json file
        with open('test/bad_library.json', 'rt') as f:
            r = self.request('/upload_catalog_json', method='POST',
                             uploaded_file=f.read())
            self.assertEqual(r.body,
                             ['Error in JSONDecode :: Expecting object: line 5 column 14 (char 139)'])


    def test_get_books(self):
        # first upload some books
        with open('test/library.json', 'rt') as f:
            r = self.request('/upload_catalog_json', method='POST',
                             uploaded_file=f.read())
            self.assertEqual(r.body, ['3b876484-0dbd-461f-935a-e58b08c06547'])
        # and now try to get them
        params = {'page':1,
                  'query':{'authors':'','titles':'','search_all':''}}
        r = self.request('/get_books', method='POST',
                         data=simplejson.dumps(params))
        self.assertEqual(r.output_status, '200 OK')
        data = simplejson.loads(r.body[0])
        self.assertEqual(data['total'], 81)
        self.assertEqual(len(data['books']), 16)
        self.assertEqual(len(data['titles']), 81)
        self.assertEqual(len(data['authors']), 92)

    def test_for_duplicates(self):
        # try to upload same catalog twice
        with open('test/library.json', 'rt') as f:
            r = self.request('/upload_catalog_json', method='POST',
                             uploaded_file=f.read())
            self.assertEqual(r.body, ['3b876484-0dbd-461f-935a-e58b08c06547'])
        with open('test/library.json', 'rt') as f:
            r = self.request('/upload_catalog_json', method='POST',
                             uploaded_file=f.read())
            self.assertEqual(r.body, ['3b876484-0dbd-461f-935a-e58b08c06547'])
        # and now try to get them
        params = {'page':1,
                  'query':{'authors':'','titles':'','search_all':''}}
        r = self.request('/get_books', method='POST',
                         data=simplejson.dumps(params))
        self.assertEqual(r.output_status, '200 OK')
        data = simplejson.loads(r.body[0])
        self.assertEqual(data['total'], 81)
            
        
#------------------------------------------------------------------------------

if __name__ == '__main__':
    import unittest
    unittest.main()
