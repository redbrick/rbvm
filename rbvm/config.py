# Rudimentary config file for rbvm. To be replaced with a proper cfg file
# using that python config parser that I can't remember the name of.

DATABASE_URI = 'sqlite:////home/andrew/rbvm.db'

BASE_DIR = '/home/andrew/rbvm'
SESSION_DIR = BASE_DIR + '/sessions'
STATIC_DIR = BASE_DIR + '/static'
VIEW_DIR = BASE_DIR + '/views'
LOG_DIR = BASE_DIR + '/logs'

ACCESS_LOG = 'access.log'
ERROR_LOG = 'error.log'

HTTP_BIND_ADDRESS = '136.206.15.5'
HTTP_PORT = 8080

SHOW_TRACEBACKS = True
LOG_TO_SCREEN = True
ENVIRONMENT = 'production'

