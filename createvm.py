#!/usr/bin/env python

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from rbvm.model.database import *
import rbvm.vmmon
import rbvm.config as config
from optparse import OptionParser

if __name__ == '__main__':
	parser = OptionParser()
	parser.add_option('-m','--mem',type="int",help="memory allocation for this VM",default=config.DEFAULT_MEM)
	parser.add_option('-d','--disk',type="int",help="default disk image size",default=config.DEFAULT_IMAGE_SIZE)
	parser.add_option('-c','--cpucores',type="int",help="number of cpu cores",default=config.DEFAULT_CPU_CORES)
	parser.add_option('-u','--username',help="this VM's user",default="root")
	parser.add_option('-t','--test',action='store_true',default=False,help="test run, do nothing")
	parser.add_option('-a','--macaddress',help='VM MAC address')
	parser.add_option('-i','--ip',help='IP address')
	parser.add_option('-f','--force',action='store_true',default=False,help='force on IP conflict')
	
	vm_properties, args = parser.parse_args()
	
	if not vm_properties.test:
		print "Connecting to VM database"
		engine = create_engine(config.DATABASE_URI)
		Session = sessionmaker()
		Session.configure(bind=engine)
		session = Session()
		
		rbvm.vmmon.create_vm(vm_properties,session,True)

