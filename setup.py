#!/usr/bin/python2.6

from distutils.core import setup
from distutils.command.install import install

setup(name = 'rbvm',
	version = '0.1',
	description = 'Redbrick VM Management Tools',
	author = 'Andrew Martin',
	author_email = 'werdz@redbrick.dcu.ie',
	url = 'https://docs.redbrick.dcu.ie/rbvm',
	packages = [
		'rbvm', 
		'rbvm.controller',
		'rbvm.lib',
		'rbvm.model',
	],
	py_modules = ['rbvm.modules.kvm'],
	license = 'bsd',
	data_files = [
		('/etc',[
			'rbvm.conf-dist',
			'rbvm-qemu-ifup', # there's a voice shouting in my head that these should go somewhere else, but the "normal" qemu ifupdown scripts are under /etc too :/
			'rbvm-qemu-ifdown',
		]),
		('/usr/bin',[
			'rbvm-createvm',
			'rbvm-createuser',
			'rbvm-installdb',
			'rbvmwebd'
		]),
		('/usr/share/rbvm/static',[
			'static/global.css'
		]),
		('/usr/share/rbvm/views',[
			'views/base.html',
			'views/domountiso.html',
			'views/index.html',
			'views/login.html',
			'views/logout.html',
			'views/manage.html',
			'views/mountiso.html',
			'views/poweroff.html',
			'views/poweron.html',
			'views/resetvm.html',
			'views/tokenerror.html'
		])
	],
	cmdclass = {'install':install},
)

