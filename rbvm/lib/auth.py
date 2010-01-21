import cherrypy
from rbvm.model.database import *
from rbvm.lib.sqlalchemy_tool import session

def get_user():
	"""
	Returns the currently logged in user
	"""

	if cherrypy.session.get('authenticated') != True:
		return None
	else:
		username = cherrypy.session.get('username')
		user = session.query(User).filter(User.username == username).first()
		return user

def require_login(func):
	"""
	Decorator to require a user to be logged in
	"""
	def wrapper(*args, **kwargs):
		if cherrypy.session.get('authenticated') == True:
			return func(*args, **kwargs)
		else:
			raise cherrypy.HTTPRedirect('/login')
	return wrapper

def require_nologin(func):
	"""
	Decorator to ensure that a user is not logged in
	"""

	def wrapper(*args, **kwargs):
		if cherrypy.session.get('authenticated') == True:
			raise cherrypy.HTTPRedirect('/')
		else:
			return func(*args,**kwargs)
	return wrapper


