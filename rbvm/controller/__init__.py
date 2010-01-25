import cherrypy
import hashlib
import cherrypy.lib.sessions
import rbvm.lib.sqlalchemy_tool as database
import rbvm.lib.template as template
from rbvm.lib.auth import get_user, require_login, require_nologin
from rbvm.model.database import *
import rbvm.config as config

class Root:
	@cherrypy.expose
	@require_login
	@template.output('index.html')
	def index(self):
		return template.render()
	
	@cherrypy.expose
	@require_nologin
	@template.output('login.html')
	def login(self, username=None, password=None):
		if username and password:
			user_object = database.session.query(User).filter(User.username == username).first()
			if not user_object:
				return template.render(error='Invalid username or password')
			pwhash = hashlib.sha256()
			pwhash.update(password + user_object.salt)
			hash_hex = pwhash.hexdigest()
			print "Checking password"
			if hash_hex == user_object.password:
				cherrypy.session['authenticated'] = True
				cherrypy.session['username'] = user_object.username
				raise cherrypy.HTTPRedirect('/')
		return template.render()
	
	@cherrypy.expose
	@template.output('logout.html')
	def logout(self):
		cherrypy.lib.sessions.expire()
		return template.render()
