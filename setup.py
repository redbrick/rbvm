#!/usr/bin/python2.6

from distutils.core import setup

setup(name='rbvm',
	version='0.1',
	description='Redbrick VM Management Tools',
	author='Andrew Martin',
	author_email='werdz@redbrick.dcu.ie',
	url='https://docs.redbrick.dcu.ie/rbvm',
	packages = [
		'rbvm', 
		'rbvm.controller',
		'rbvm.lib',
		'rbvm.model',
	],
	py_modules=['rbvm.modules.kvm'],
	license = 'bsd',)

