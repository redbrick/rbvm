#!/usr/bin/env python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from rbvm.model.database import *
import rbvm.config as config

import smtplib
import string
import random
from optparse import OptionParser

def main():
	parser = OptionParser()
	parser.add_option('-u','--username',default=None,help='the username to be created')
	parser.add_option('-e','--email',default=None,help='the email address of the new user')
	
	options, args = parser.parse_args()

	if options.username is None or options.email is None:
		print "Please supply a username and email address."
		return
	
	print "Connecting to database"
	engine = create_engine(config.DATABASE_URI)
	Session = sessionmaker()
	Session.configure(bind=engine)
	session = Session()

	# Check that the user doesn't exist
	user = session.query(User).filter(User.username==options.username).first()
	if user is not None:
		print "The user %s already exists!" % options.username
		return

	password = "".join(random.sample(string.letters + string.digits,8))
	user = User(options.username,options.email, password)
	session.add(user)
	session.commit()

	print "User created. Password is:\n\t%s" % password
	print "Emailing user at %s" % options.email
	s = smtplib.SMTP()
	s.connect()
	s.sendmail(config.EMAIL_ADDRESS, options.email, "From: %s\nTo: %s\nSubject: Your VM account has been created\n\nAn account has been created for you on the VM administration system. You\nmay log in at %s.\n\nYour details are:\n\nUsername: %s\nPassword: %s\n\nRegards,\n-Automated mailing monkey" % (config.EMAIL_ADDRESS, options.email, config.SITE_ADDRESS, options.username, password))
	s.quit()


if __name__ == '__main__':
	main()
