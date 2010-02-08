# coding=utf-8
import os
import os.path
import re
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
	
	user = session.query(User).filter(User.username==vm_properties.username).first()
	
	try:
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

def check_vm_status(vm_object):
	"""
	Checks whether or not a VM is running. This is achieved by checking the 
	last PID and launch time information in the database match the 
	information in /proc.
	"""
	assert vm_object is not None

	known_pid = vm_object.pid
	last_launch = vm_object.last_launch

	if known_pid is None or last_launch is None:
		return False # missing data, so it's probably not running
	
	cmd_path = '/proc/' + str(known_pid) + '/cmdline'
	
	if not os.path.exists(cmd_path):
		print cmd_path
		return False # can't find proc info, VM not running
	
	timestamp = os.stat(cmd_path)[9] # ctime
	ts_min = timestamp - 10
	ts_max = timestamp + 10
	
	dt_min = datetime.datetime.fromtimestamp(ts_min)
	dt_max = datetime.datetime.fromtimestamp(ts_max)
	
	if last_launch < dt_min or last_launch > dt_max:
		print "b"
		return False # the process is the wrong age, not the VM

	f = open(cmd_path, 'r')
	cmdline = f.read(8192)
	f.close()
	cmds = cmdline.split("\x00")
	if cmds[0] != config.TOOL_KVM:
		print "c"
		return False # it's not KVM :( return false
	else:
		return True # all checks pass, the vm seems to be running

def write_to_monitor(vm_object,data):
	"""
	Sends data to a VM's monitor.
	"""
	assert vm_object is not None
	assert check_vm_status(vm_object) is True
	
	monitor_pt = vm_object.monitor_pt
	
	m_w = os.open(monitor_pt,os.O_WRONLY)
	os.write(m_w,data)
	os.close(m_w)

def read_from_monitor(vm_object):
	"""
	Reads data from a VM's monitor.
	"""
	assert vm_object is not None
	assert check_vm_status(vm_object) is True
	
	monitor_pt = vm_object.monitor_pt
	
	m_r = os.open(monitor_pt,os.O_RDONLY)
	data = os.read(m_r,4096)
	os.close(m_r)
	
	return data

def power_on(vm_object):
	"""
	Attempts to turn the power on 
	
	Notes:
	add the following to sudoers:
	Defaults:username !requiretty
	Cmnd_Alias RBVM = /sbin/ifconfig, /usr/sbin/brctl, /usr/sbin/tunctl
	username ALL=NOPASSWD:RBVM
	
	add the following to /etc/qemu-ifup:
	#!/bin/sh
	sudo /sbin/ifconfig $1 0.0.0.0 promisc up
	sudo /usr/sbin/brctl addif br0 $1
	
	Returns the vnc password if successful
	"""
	# Collect options and build a kvm parameter list
	# generate vnc password
	# execute kvm as -daemonize, collect the pt names, save them.
	# save pid, timestamp
	
	assert vm_object is not None
	assert check_vm_status(vm_object) is False
	
	# Prepare parameters/settings
	smp_param = None
	mem_param = None
	vnc_param = None
	hd_param = None
	disk_images = []
	
	for prop in vm_object.properties:
		if prop.key == 'disk_image':
			disk_images.append(os.path.join(config.IMAGE_DIR,prop.value))
		
		if prop.key == 'ram':
			try:
				mem_param = int(prop.value)
			except ValueError:
				pass
		
		if prop.key == 'cpu_cores':
			try:
				smp_param = int(prop.value)
			except ValueError:
				pass
	
	assert len(disk_images) > 0 and len(disk_images) < 27
	alphabet = "abcdefghijklmnopqrstuvwxyz"
	hd_param = ""
	for i in range(0,len(disk_images)):
		hd_param = hd_param + " -hd%c %s" % (alphabet[i],disk_images[i])
	
	vnc_param = "%s:%i,password" % (config.VNC_IP,vm_object.id)
	
	assert smp_param is not None
	assert mem_param is not None
	assert vnc_param is not None
	assert hd_param is not "" and hd_param is not None
	
	# Generate vnc password:
	vnc_password = "".join(random.sample(string.letters + string.digits,8))
	
	# Assign the tap interface
	tap = "tap%i" % vm_object.id
	tunctl_params = [config.TOOL_SUDO,config.TOOL_TUNCTL,'-u',config.SYSTEM_USERNAME,'-t',tap]
	subprocess.call(tunctl_params)
	
	# Run brctl delif just to ensure that the tap isn't on the bridge before continuing
	brctl_params = [config.TOOL_SUDO,config.TOOL_BRCTL,'delif',config.NETWORK_BRIDGE,tap]
	subprocess.call(brctl_params) # we don't really care if this fails - in fact, we hope it will.
	
	# Run the vmm
	kvm_params = "-net nic -net tap,ifname=%s,script=/etc/qemu-ifup %s -smp %i -m %i -serial pty -monitor pty -vnc %s" % (tap,hd_param,smp_param, mem_param, vnc_param)
	kvm_param_list = [config.TOOL_KVM] + kvm_params.split()
	
	proc = subprocess.Popen(kvm_param_list,close_fds=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE)
	pid = proc.pid
	proc_outfd = proc.stdout.fileno()
	proc_errfd = proc.stderr.fileno()
	
	proc_outdata = os.read(proc_outfd,512)
	proc_errdata = os.read(proc_errfd,512)
	proc_errdata = proc_errdata + os.read(proc_errfd,512) # read two lines
	
	#print "stdout:\n%s" % proc_outdata
	#print "stderr:\n%s" % proc_errdata
	
	proc.stdout.close()
	proc.stderr.close()
	
	# Try to find the names of the two pts
	m = re.match(r'char device redirected to ([a-zA-Z0-9/]*)\nchar device redirected to ([a-zA-Z0-9/]*)', proc_errdata) # why does this come out via stderr? :/
	
	# First line is the monitor, second line is the serial console
	monitor_pt = m.group(1)
	serial_pt = m.group(2)
	
	m_r = os.open(monitor_pt,os.O_RDONLY)
	m_w = os.open(monitor_pt,os.O_WRONLY)
	data = os.read(m_r,4096)
	#print "monitor device says:\n%s" % data
	assert data.startswith("QEMU ")
	
	os.write(m_w,"change vnc password\n")
	os.read(m_r,4096)
	os.write(m_w,vnc_password + "\n")
	
	os.close(m_w)
	os.close(m_r)
	
	vm_object.console_pt = serial_pt
	vm_object.monitor_pt = monitor_pt
	vm_object.last_launch = datetime.datetime.now()
	vm_object.pid = pid
	
	try:
		session.commit()
	except:
		database.session.commit()
	
	return vnc_password
