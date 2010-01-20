import cherrypy
import hashlib
from rbvm.lib.sqlalchemy_tool import session
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
	@require_login
	@template.output('login.html')
	def login(self, username=None, password=None):
		if username and password:
			user_object = session.query(User).filter(User.username == username).first()
			if not user_object:
				return template.render(error='Invalid username or password')
			pwhash = hashlib.sha256()
			pwhash.update(password)
			pwhash.update(user_object.salt)
			hash_hex = pwhash.hexdigest()
			if pwhash_hex == user_object.password:
				cherrypy.session['authenticated'] = True
				cherrypy.session['username'] = user_object.username
				raise cherrypy.HTTPRedirect('/')
		return template.render()
		
