import os.path
import ConfigParser
import re

config = ConfigParser.SafeConfigParser()
config.read(['/etc/rbvm.conf-dist', '/etc/rbvm.conf', os.path.expanduser('~/rbvm.conf')])

try:
	DATABASE_URI = config.get('database','uri')
except:
	DATABASE_URI = 'sqlite:////var/lib/rbvm/rbvm.db'

try:
	BASE_DIR = config.get('web','basedir')
except:
	BASE_DIR = '/usr/share/pyshared/rbvm'

try:
	SESSION_DIR = config.get('web','sessiondir')
except:
	SESSION_DIR = '/tmp/rbvm/sessions'

try:
	STATIC_DIR = config.get('web','staticdir')
except:
	STATIC_DIR = '/usr/share/rbvm/static'

try:
	VIEW_DIR = config.get('web','viewdir')
except:
	VIEW_DIR = '/usr/share/rbvm/views'

try:
	LOG_DIR = config.get('web','logdir')
except:
	LOG_DIR = '/var/log/rbvm'

try:
	MODULE_DIR = config.get('general','moduledir')
except:
	MODULE_DIR = os.path.join(BASE_DIR, 'rbvm/modules')

try:
	IMAGE_DIR = config.get('vm','imagedir')
except:
	IMAGE_DIR = '/var/lib/rbvm/images'

try:
	ISO_DIR = config.get('vm','isodir')
except:
	ISO_DIR = '/var/lib/rbvm/iso'

# Default sizes - all in MB unless otherwise specified
try:
	DEFAULT_MEM = config.getint('vm','defaultram')
except:
	DEFAULT_MEM = 128

try:
	DEFAULT_IMAGE_SIZE = config.getint('vm','defaultimagesize')
except:
	DEFAULT_IMAGE_SIZE = 8192

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
	HTTP_BIND_ADDRESS = '127.0.0.1'

try:
	HTTP_PORT = config.getint('web','port')
except:
	HTTP_PORT = 8080

try:
	SHOW_TRACEBACKS = config.getboolean('debug','showtracebacks')
except:
	SHOW_TRACEBACKS = False

try:
	DEBUG_MODE = config.getboolean('debug','debugmode')
except:
	DEBUG_MODE = False

try:
	LOG_TO_SCREEN = config.getboolean('debug','logtoscreen')
except:
	LOG_TO_SCREEN = False

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
	EMAIL_ADDRESS = 'Your Name <your.address@domain.org>'

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
	TOOL_KVM = '/usr/bin/qemu-kvm'

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
	SYSTEM_USERNAME = 'rbvm'

try:
	SYSTEM_GROUP = config.get('general','sysgroup')
except:
	SYSTEM_GROUP = 'rbvm'

try:
	NETWORK_BRIDGE = config.get('vm','bridge')
except:
	NETWORK_BRIDGE = 'br0'

try:
	IFUP_SCRIPT = config.get('vm','ifupscript')
except:
	IFUP_SCRIPT = '/etc/rbvm-qemu-ifup'

try:
	IFDOWN_SCRIPT = config.get('vm','ifdownscript')
except:
	IFDOWN_SCRIPT = '/etc/rbvm-qemu-ifdown'

try:
	MAC_RANGE = config.get('vm','macrange')
	assert re.match(r'^[0-9a-fA-F]{2}\:[0-9a-fA-F]{2}\:[0-9a-fA-F]{2}\:00\:00\:00$', MAC_RANGE) is not None
except:
	MAC_RANGE = 'aa:bb:cc:00:00:00'
