#------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
import cherrypy

from server import Root, thread_connect
from cptestcase import BaseCherryPyTestCase
import simplejson
from pymongo import MongoClient
import settings
import libraries

#------------------------------------------------------------------------------
# WARNING: this test suite is far from complete. testing database should be
# prepared before running these tests!
# 1. run local test server: $ python server.py --env test
# 2. cd test/; python upload.py --file library.json.zip 
#------------------------------------------------------------------------------
            
def setUpModule():
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

    def test_index(self):
        response = self.request('/')
        self.assertEqual(response.output_status, '200 OK')
        self.assertGreater(response.body[0].find('memory of the world'), -1)

    def test_get_books(self):
        params = {'page':1,
                  'query':{'authors':'','titles':'','search_all':''}}
        response = self.request('/get_books', method='POST',
                                data=simplejson.dumps(params))
        self.assertEqual(response.output_status, '200 OK')
        data = simplejson.loads(response.body[0])
        self.assertEqual(data['total'], 81)
        self.assertEqual(len(data['books']), 16)
        self.assertEqual(len(data['titles']), 81)
        self.assertEqual(len(data['authors']), 92)
        
#------------------------------------------------------------------------------

if __name__ == '__main__':
    import unittest
    unittest.main()
