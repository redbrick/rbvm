#!/usr/bin/env python
import cherrypy
import string
import os.path
import rbvm.controller
import sqlalchemy
import rbvm.lib.sqlalchemy_tool
import rbvm.config as config

def env_init():
	"""
	Sets up the application environment
	"""
	cherrypy.config.update({'environment': config.ENVIRONMENT,
		'log.screen':config.LOG_TO_SCREEN,
		'log.error_file': os.path.join(config.LOG_DIR, config.ERROR_LOG),
		'log.access_file':os.path.join(config.LOG_DIR, config.ACCESS_LOG),
		'show_tracebacks':config.SHOW_TRACEBACKS,
		'server.socket_host':config.HTTP_BIND_ADDRESS,
		'server.socket_port':config.HTTP_PORT})
	
	cherrypy.tree.mount(rbvm.controller.Root())
	cherrypy.tree.apps[''].config = {
		'/' : {
			'tools.sessions.on':True,
			'tools.sessions.storage_type':'file',
			'tools.sessions.storage_path':config.SESSION_DIR,
			'tools.sessions.timeout':config.SESSION_TIMEOUT,
			'tools.encode.encoding':'utf-8',
			'tools.SATransaction.on':True,
			'tools.SATransaction.dburi':config.DATABASE_URI,
			'tools.SATransaction.echo':False,
			'tools.SATransaction.convert_unicode':True,
		},
		'/static': {
			'tools.staticdir.on' : True,
			'tools.staticdir.dir': config.STATIC_DIR
		}
	}


def standalone():
	"""
	Run a standalone server
	"""
	cp_version = string.split(cherrypy.__version__,'.')
	env_init()
	if int(cp_version[1]) == 0:
		#Use quickstart for cp 3.0.x
		cherrypy.server.quickstart()
		cherrypy.engine.start()
	else:
		cherrypy.server.start()
		cherrypy.engine.block()

def mod_python_server():
	"""
	Set up for running under mod_python
	"""
	env_init()

if __name__ == '__main__':
	standalone()
