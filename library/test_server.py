#------------------------------------------------------------------------------
# -*- coding: utf-8 -*-
# some lsb tests
#------------------------------------------------------------------------------

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

def tearDownModule():
    cherrypy.engine.exit()

setup_module = setUpModule
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
            return [[12345]]

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
        '''
        Tests index page with some text
        '''
        response = self.request('/')
        self.assertEqual(response.output_status, '200 OK')
        self.assertGreater(response.body[0].find('memory of the world'), -1)

    def test_upload_catalog(self):
        '''
        Tris to upload good and bad library
        '''
        # this library should be uploaded with no problems
        res = upload_catalog(self, 'fixtures/library.json')
        self.assertEqual(res, '3b876484-0dbd-461f-935a-e58b08c06547')

        # this library should be the only one
        res = self.request('/get_catalogs', method='GET')
        self.assertEqual(res.body, ['1'])

        # bad json file
        res = upload_catalog(self, 'fixtures/bad_library.json')
        self.assertEqual(res[:20], 'Error in JSONDecode ')

    def test_get_books(self):
        '''
        Tests if main get_books function works after upload
        '''
        # first upload some books
        res = upload_catalog(self, 'fixtures/library.json')
        self.assertEqual(res, '3b876484-0dbd-461f-935a-e58b08c06547')
        # and now try to get them
        r = self.request('/get_books', method='GET')
        self.assertEqual(r.output_status, '200 OK')
        data = simplejson.loads(r.body[0])
        self.assertEqual(data['total'], 2)
        self.assertEqual(len(data['books']), 2)

    def test_search(self):
        '''
        Search by author, title or librarian
        '''
        # first upload some books
        res = upload_catalog(self, 'fixtures/library.json')
        self.assertEqual(res, '3b876484-0dbd-461f-935a-e58b08c06547')
        # search author
        params = {'page':1, 'query':{'authors':'Heidegger'}}
        r = self.request('/get_books', method='POST',
                         data=simplejson.dumps(params))
        self.assertEqual(r.output_status, '200 OK')
        data = simplejson.loads(r.body[0])
        self.assertEqual(data['total'], 1)
        self.assertEqual(len(data['books']), 1)
        self.assertEqual(data['books'][0]['authors'][0], 'Martin Heidegger')
        # search title
        params = {'page':1, 'query':{'title':'music'}}
        r = self.request('/get_books', method='POST',
                         data=simplejson.dumps(params))
        self.assertEqual(r.output_status, '200 OK')
        data = simplejson.loads(r.body[0])
        self.assertEqual(data['total'], 1)
        self.assertEqual(len(data['books']), 1)
        self.assertEqual(
            data['books'][0]['title'],
            'Archipelagos Of Sound : music and its history within the imperial world order')
        # search librarian
        params = {'page':1, 'query':{'librarian':'LibrAn0n'}}
        r = self.request('/get_books', method='POST',
                         data=simplejson.dumps(params))
        self.assertEqual(r.output_status, '200 OK')
        data = simplejson.loads(r.body[0])
        self.assertEqual(data['total'], 2)

    def test_for_duplicates(self):
        '''
        '''
        # try to upload same catalog twice
        res = upload_catalog(self, 'fixtures/library.json')
        self.assertEqual(res, '3b876484-0dbd-461f-935a-e58b08c06547')
        r = self.request('/get_books', method='GET')
        # fetch first catalog
        self.assertEqual(r.output_status, '200 OK')
        data = simplejson.loads(r.body[0])
        self.assertEqual(data['total'], 2)
        # upload second time
        res = upload_catalog(self, 'fixtures/library.json')
        self.assertEqual(res, '3b876484-0dbd-461f-935a-e58b08c06547')
        # and now try to get them
        r = self.request('/get_books', method='GET')
        self.assertEqual(r.output_status, '200 OK')
        data = simplejson.loads(r.body[0])
        self.assertEqual(data['total'], 2)

    def test_book(self):
        '''
        Test /book function. Mostly obsolete.
        '''
        res = upload_catalog(self, 'fixtures/library.json')
        self.assertEqual(res, '3b876484-0dbd-461f-935a-e58b08c06547')
        uuid = '62a47470-406d-4a88-9bc2-abc01fdd2a69'
        r = self.request('/book', method='POST', uuid=uuid)
        self.assertEqual(r.output_status, '200 OK')
        data = simplejson.loads(r.body[0])
        self.assertEqual(data['uuid'], uuid)

    def test_portable(self):
        '''
        Test portable library upload.
        Note: since portable requires library at some url, this test should
        somehow mock portable library, but this will work for now.
        '''
        lib_uuid = '4c876484-0dbd-461f-935a-e58b08c06567'
        # first upload some books
        res = upload_catalog(self, 'fixtures/portable.json')
        self.assertEqual(res, lib_uuid)
        # and now try to get them
        r = self.request('/get_books', method='GET')
        self.assertEqual(r.output_status, '200 OK')
        data = simplejson.loads(r.body[0])
        self.assertEqual(data['total'], 1)
        
#------------------------------------------------------------------------------

if __name__ == '__main__':
    import unittest
    unittest.main()
