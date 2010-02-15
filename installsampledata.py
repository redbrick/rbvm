#!/usr/bin/env python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from rbvm.model.database import *
import rbvm.config as config

def populate():
	print "Connecting to database"
	engine = create_engine(config.DATABASE_URI)

	Session = sessionmaker()
	Session.configure(bind=engine)
	session = Session()

	print "Adding sample groups"
	admins = Group('Admins')
	users = Group('Users')
	session.add(admins)
	session.add(users)
	session.commit()

	
if __name__ == '__main__':
	populate()
