import rbvm.setup
from optparse import OptionParser
import rbvm.config as config

if __name__ == '__main__':
	parser = OptionParser()
	parser.addoption('-c','--clear',action='store_true',default=False,help='drop all tables before installing')

	options, args = parser.parse_args()
	rbvm.setup.install(drop_all=options.clear)

