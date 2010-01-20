from rbvm.model.database import *
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import rbvm.config as config

session = None

def install(drop_all=False):
	"""
	Installs the database, and if necessary, wipes it first.
	"""

	print "Connecting to database..."
	engine = create_engine(config.DATABASE_URI)
	Base.metadata.bind = engine

	if drop_all:
		print "Dropping old tables..."
		Base.metadata.drop_all()
	
	print "Installing new schema..."
	Base.metadata.create_all(engine)



