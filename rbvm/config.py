import os.path
import ConfigParser

config = ConfigParser.SafeConfigParser()
config.read(['rbvm/rbvm.conf-dist', '/etc/rbvm.conf', os.path.expanduser('~/rbvm.conf')])

try:
	DATABASE_URI = config.get('database','uri')
except:
	DATABASE_URI = 'sqlite:////home/andrew/rbvm.db'

try:
	BASE_DIR = config.get('web','basedir')
except:
	BASE_DIR = '/home/andrew/rbvm'

try:
	SESSION_DIR = config.get('web','sessiondir')
except:
	SESSION_DIR = BASE_DIR + '/sessions'

try:
	STATIC_DIR = config.get('web','staticdir')
except:
	STATIC_DIR = BASE_DIR + '/static'

try:
	VIEW_DIR = config.get('web','viewdir')
except:
	VIEW_DIR = BASE_DIR + '/views'

try:
	LOG_DIR = config.get('web','logdir')
except:
	LOG_DIR = BASE_DIR + '/logs'

try:
	MODULE_DIR = config.get('general','moduledir')
except:
	MODULE_DIR = os.path.join(BASE_DIR, 'rbvm/modules')

try:
	IMAGE_DIR = config.get('vm','imagedir')
except:
	IMAGE_DIR = '/var/lib/rbvm/images'

# Default sizes - all in MB unless otherwise specified
try:
	DEFAULT_MEM = config.getint('vm','defaultram')
except:
	DEFAULT_MEM = 128

try:
	DEFAULT_IMAGE_SIZE = config.getint('vm','defaultimagesize')
except:
	DEFAULT_IMAGE_SIZE = 4196

try:
	DEFAULT_CPU_CORES = config.getint('vm','defaultcores')
except:
	DEFAULT_CPU_CORES = 1

try:
	ACCESS_LOG = config.get('web','accesslog')
except:
	ACCESS_LOG = 'access.log'

try:
	ERROR_LOG = config.get('web','errorlog')
except:
	ERROR_LOG = 'error.log'

try:
	HTTP_BIND_ADDRESS = config.get('web','bindaddress')
except:
	HTTP_BIND_ADDRESS = '136.206.15.5'

try:
	HTTP_PORT = config.getint('web','port')
except:
	HTTP_PORT = 8080

try:
	SHOW_TRACEBACKS = config.getboolean('debug','showtracebacks')
except:
	SHOW_TRACEBACKS = True
try:
	LOG_TO_SCREEN = config.getboolean('debug','logtoscreen')
except:
	LOG_TO_SCREEN = True
try:
	ENVIRONMENT = config.getboolean('debug','cherrypyenvironment')
except:
	ENVIRONMENT = 'production'

try:
	SESSION_TIMEOUT = config.getint('web','sessiontimeout')
except:
	SESSION_TIMEOUT = 3600

try:
	EMAIL_ADDRESS = config.get('general','emailaddress')
except:
	EMAIL_ADDRESS = 'Redbrick Admins <admins@redbrick.dcu.ie>'

try:
	SITE_ADDRESS = config.get('general','siteaddress')
except:
	SITE_ADDRESS = 'http://localhost:8080/'

# Tools
try:
	TOOL_QEMU_IMG = config.get('tools','qemu-img')
except:
	TOOL_QEMU_IMG = '/usr/bin/qemu-img'

try:
	TOOL_KVM = config.get('tools','kvm')
except:
	TOOL_KVM = '/usr/bin/kvm'

try:
	VMMON = config.get('general','vmmon')
except:
	VMMON = 'kvm'

try:
	VNC_IP = config.get('vm','vncip')
except:
	VNC_IP = '127.0.0.1'

try:
	VNC_BASE_PORT = config.getint('vm','vncbaseport')
except:
	VNC_BASE_PORT = 5900

try:
	TOOL_SUDO = config.get('tools','sudo')
except:
	TOOL_SUDO = '/usr/bin/sudo'

try:
	TOOL_TUNCTL = config.get('tools','tunctl')
except:
	TOOL_TUNCTL = '/usr/sbin/tunctl'

try:
	TOOL_BRCTL = config.get('tools','brctl')
except:
	TOOL_BRCTL = '/usr/sbin/brctl'

try:
	SYSTEM_USERNAME = config.get('general','sysuser')
except:
	SYSTEM_USERNAME = 'andrew'

try:
	NETWORK_BRIDGE = config.get('vm','bridge')
except:
	NETWORK_BRIDGE = 'br0'


