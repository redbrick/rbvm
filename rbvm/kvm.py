import os.path
import random
import string
import subprocess
import datetime
from rbvm.model.database import *
import rbvm.lib.sqlalchemy_tool as database
import rbvm.config as config
# KVM abstraction layer

def create_vm(vm_properties, session=database.session, print_output=False):
	"""
	Creates a virtual machine
	"""
	if session is None:
		raise "No database session present"
	
	try:
		user = session.query(User).filter(User.username==vm_properties.username).one()
		assert user is not None
	except:
		print "Could not find the user %s" % (vm_properties.username)
		print "Cannot continue."
		return
	
	print "Creating virtual machine..."
	print "VM Properties:"
	print "RAM:\t\t%iMB" % vm_properties.mem
	print "Disk size:\t%iMB" % vm_properties.disk
	print "User:\t\t%s" % vm_properties.username
	print ""
	
	try:
		disk_image_size = int(vm_properties.disk)
		ram_size = int(vm_properties.disk)
		cpu_cores = int(vm_properties.cpucores)
	except ValueError:
		print "Invalid input supplied."
		return
	
	# Create the physical disk image
	print "Creating physical disk images"
	valid_name = False
	image_name = None
	full_path = None
	while not valid_name:
		image_name = "disk_%s.img" % "".join(random.sample(string.hexdigits,20))
		print "Trying image name %s" % image_name
		full_path = os.path.join(config.IMAGE_DIR,image_name)
		if not os.path.exists(full_path):
			print "Filename free, creating image"
			valid_name = True
	
	qemu_img_retcode = subprocess.call([config.TOOL_QEMU_IMG, "create", "-f", "qcow2", full_path, "%iM" % disk_image_size])
	if qemu_img_retcode != 0:
		print "Error creating qemu image: subprocess returned error code %i" % qemu_img_retcode
		return
	
	print "Disk image created. Adding VM entry to database."
	
	vm_name = "VM created at %s" % (datetime.datetime.now().isoformat())
	vm = VirtualMachine(vm_name, user)
	session.add(vm)
	session.commit()
	print "VM created, populating properties."
	prop_mem = Property("ram",str(ram_size),vm)
	prop_disk = Property("disk_image",image_name,vm)
	prop_cpu = Property("cpu_cores",str(cpu_cores),vm)
	session.add(prop_mem)
	session.add(prop_disk)
	session.add(prop_cpu)
	session.commit()
	print "Complete"

