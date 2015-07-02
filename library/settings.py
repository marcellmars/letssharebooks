#------------------------------------------------------------------------------
# server configuration
#------------------------------------------------------------------------------
import os
import libraries
import utils

ENV_NAME = None
ENV = None

SERVER = {
    'local': {
        'mongo_addr': '127.0.0.1',
        'mongo_port': 27017,
        'host': '0.0.0.0',
        'port': 4321,
        'domain_url': 'memoryoftheworld.org',
        'dbname': 'letssharebooks',
        },
    'test': {
        'mongo_addr': '127.0.0.1',
        'mongo_port': 27017,
        'host': '0.0.0.0',
        'port': 4321,
        'domain_url': 'memoryoftheworld.org',
        'dbname': 'letssharebooks_test',
        },
    'live': {
        'mongo_addr': utils.get_mongo_live_addr(),
        'mongo_port': 27017,
        'host': '0.0.0.0',
        'port': 4321,
        'domain_url': 'memoryoftheworld.org',
        'dbname': 'letssharebooks',
        },
    'docker': {
        'mongo_addr': os.environ.get("MONGODB_PORT_27017_TCP_ADDR"),
        'mongo_port': 27017,
        'host': '0.0.0.0',
        'port': 4321,
        'domain_url': 'memoryoftheworld.org',
        'dbname': 'letssharebooks',
        }
    }

def set_env(env):
    global ENV
    global ENV_NAME
    ENV_NAME = env
    ENV = SERVER[ENV_NAME]
    libraries.setup_active_tunnels_func()

#------------------------------------------------------------------------------
# search
#------------------------------------------------------------------------------

ITEMS_PER_PAGE = 16

#------------------------------------------------------------------------------
# Web app
#------------------------------------------------------------------------------

APP_NAME = 'memory of the world library'
