import cherrypy
from genshi.core import Stream
from genshi.output import encode, get_serializer
from genshi.template import Context, TemplateLoader
import rbvm.config as config
from rbvm.lib.auth import get_user

loader = TemplateLoader(config.VIEW_DIR, auto_reload=True)

def output(filename, method='html', encoding='utf-8', **options):
	"""
	Decorator to pecify a template to be applied.
	"""
	def decorate(func):
		def wrapper(*args, **kwargs):
			cherrypy.thread_data.template = loader.load(filename)
			opt = options.copy()
			if method == 'html':
				opt.setdefault('doctype','html')

			serializer = get_serializer(method, **opt)
			stream = func(*args,**kwargs)
			if not isinstance(stream, Stream):
				return stream

			return encode(serializer(stream),method=serializer,encoding=encoding)
		return wrapper
	return decorate

def render(*args,**kwargs):
	"""
	Renders the required template
	"""
	if args:
		assert len(args) == 1, "Expected precisely one argument, got %r" % (args,)
		template = loader.load(args[0])
	else:
		template = cherrypy.thread_data.template
	
	if 'error' not in kwargs:
		kwargs['error'] = None
	
	kwargs['user'] = get_user()
	ctxt = Context(url=cherrypy.url)
	ctxt.push(kwargs)
	return template.generate(ctxt)

