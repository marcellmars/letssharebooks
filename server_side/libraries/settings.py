#------------------------------------------------------------------------------
# server configuration
#------------------------------------------------------------------------------
import os

SERVER = {
    'local': {
        'mongo_addr': '127.0.0.1',
        'mongo_port': 27017,
        'prefix_url': 'http://www',
        'host': '0.0.0.0',
        'port': 4321,
        'dbname': 'letssharebooks',
        },
    'test': {
        'mongo_addr': '127.0.0.1',
        'mongo_port': 27017,
        'prefix_url': 'http://www',
        'host': '0.0.0.0',
        'port': 4321,
        'dbname': 'letssharebooks_test',
        },
    'live': {
        'mongo_addr': 'localhost',
        'mongo_port': 27017,
        'prefix_url' : 'https://www',
        'host': '0.0.0.0',
        'port': 80,
        'dbname': 'letssharebooks',
        },
    'docker': {
        #'mongo_addr': os.environ["MONGODB_PORT_27017_TCP_ADDR"],
        'mongo_addr': '172.17.0.2',
        'mongo_port': 27017,
        'prefix_url': 'http://www',
        'host': '0.0.0.0',
        'port': 4321,
        'dbname': 'letssharebooks',
        }
    }

ENV = SERVER['docker']

#------------------------------------------------------------------------------
# search
#------------------------------------------------------------------------------

ITEMS_PER_PAGE = 16

#------------------------------------------------------------------------------
# Web app
#------------------------------------------------------------------------------

APP_NAME = 'memory of the world library'
