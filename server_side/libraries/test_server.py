#------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
import cherrypy

from server import Root, thread_connect
from cptestcase import BaseCherryPyTestCase
import simplejson
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

def upload_catalog(test, filename):
    '''
    Shortcut for common uploading functionality to test
    '''
    with open(filename, 'rt') as f:
        r = test.request('/upload_catalog_json', method='POST',
                         uploaded_file=f.read())
        return r.body[0]

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

    def tearDown(self):
        # clear db
        self.db = utils.connect_to_db(settings.ENV)
        utils.remove_all_data(self.db)

    def test_index(self):
        response = self.request('/')
        self.assertEqual(response.output_status, '200 OK')
        self.assertGreater(response.body[0].find('memory of the world'), -1)

    def test_upload_catalog(self):
        # this library should be uploaded with no problems
        res = upload_catalog(self, 'test/library.json')
        self.assertEqual(res, '3b876484-0dbd-461f-935a-e58b08c06547')

        # this library should be the only one
        res = self.request('/get_catalogs', method='GET')
        self.assertEqual(res.body, ['1'])

        # bad json file
        res = upload_catalog(self, 'test/bad_library.json')
        self.assertEqual(res[:20], 'Error in JSONDecode ')

    def test_get_books(self):
        # first upload some books
        res = upload_catalog(self, 'test/library.json')
        self.assertEqual(res, '3b876484-0dbd-461f-935a-e58b08c06547')
        # and now try to get them
        params = {'page':1,
                  'query':{'authors':'','titles':'','search_all':''}}
        r = self.request('/get_books', method='POST',
                         data=simplejson.dumps(params))
        self.assertEqual(r.output_status, '200 OK')
        data = simplejson.loads(r.body[0])
        self.assertEqual(data['total'], 2)
        self.assertEqual(len(data['books']), 2)
        self.assertEqual(len(data['titles']), 2)
        self.assertEqual(len(data['authors']), 3)
        self.assertEqual(len(data['librarians']), 1)

    def test_for_duplicates(self):
        # try to upload same catalog twice
        res = upload_catalog(self, 'test/library.json')
        self.assertEqual(res, '3b876484-0dbd-461f-935a-e58b08c06547')
        res = upload_catalog(self, 'test/library.json')
        self.assertEqual(res, '3b876484-0dbd-461f-935a-e58b08c06547')
        # and now try to get them
        params = {'page':1,
                  'query':{'authors':'','titles':'','search_all':''}}
        r = self.request('/get_books', method='POST',
                         data=simplejson.dumps(params))
        self.assertEqual(r.output_status, '200 OK')
        data = simplejson.loads(r.body[0])
        self.assertEqual(data['total'], 2)

    def test_book(self):
        res = upload_catalog(self, 'test/library.json')
        self.assertEqual(res, '3b876484-0dbd-461f-935a-e58b08c06547')
        uuid = '62a47470-406d-4a88-9bc2-abc01fdd2a69'
        r = self.request('/book', method='POST', uuid=uuid)
        self.assertEqual(r.output_status, '200 OK')
        data = simplejson.loads(r.body[0])
        self.assertEqual(data['uuid'], uuid)


#------------------------------------------------------------------------------

if __name__ == '__main__':
    import unittest
    unittest.main()
