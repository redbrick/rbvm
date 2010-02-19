# coding=utf-8
import os
import os.path
import re
import random
import string
import subprocess
import time
import datetime
from rbvm.model.database import *
import rbvm.lib.sqlalchemy_tool as database
import rbvm.lib.ptree as ptree
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
	
	try:
		if vm_properties.macaddress is not None:
			assert re.match(r'^[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}:[0-9a-fA-F]{2}$',vmproperties.macaddress) is not None
			mac_address = vm_properties.macaddress
		else:
			raise Exception
	except:
		g = re.match(r'^([0-9a-fA-F]{2}):([0-9a-fA-F]{2}):([0-9a-fA-F]{2}).*',config.MAC_RANGE)
		assert g is not None
		a = int(g.group(1),16)
		b = int(g.group(2),16)
		c = int(g.group(3),16)
		d = random.randint(0,255)
		e = random.randint(0,255)
		f = random.randint(0,255)
		
		mac_address = "%02X:%02X:%02X:%02X:%02X:%02X" % (a,b,c,d,e,f)
	
	if vm_properties.ip is not None:
		
		print "IP specified, checking previous allocations"
		conflict = True
		try:
			other_vm = session.query(VirtualMachine).filter(VirtualMachine.assigned_ip==vm_properties.ip).first()
			assert other_vm is not None
		except Exception,e:
			print str(e)
			print "No conflict found"
			conflict = False
		if conflict is True:
			print "***************************************************************************"
			print " WARNING: IP allocation conflict! The IP requested is already allocated!"
			print "***************************************************************************"
			if vm_properties.force is False:
				print "Aborting. Pleae specify -f or --force if you wish to continue anyway."
				return
			else:
				print "Apparently you want to force this, continuing (even though it's stupid)."
	
	print "Creating virtual machine..."
	print "VM Properties:"
	print "RAM:\t\t%iMB" % vm_properties.mem
	print "Disk size:\t%iMB" % vm_properties.disk
	print "User:\t\t%s" % vm_properties.username
	print "MAC addr:\t%s" % mac_address
	print "IP address:\t%s" % str(vm_properties.ip)
	print ""
	
	try:
		disk_image_size = int(vm_properties.disk)
		ram_size = int(vm_properties.mem)
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
	vm.memory = ram_size
	vm.cpu_cores = cpu_cores
	vm.mac_address = mac_address
	vm.assigned_ip = vm_properties.ip
	session.add(vm)
	session.commit()
	print "VM created, populating disk image list."
	prop_disk = Property("disk_image",image_name,vm)
	session.add(prop_disk)
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
		return False # can't find proc info, VM not running
	
	timestamp = os.stat(cmd_path)[9] # ctime
	ts_min = timestamp - 10
	ts_max = timestamp + 10
	
	dt_min = datetime.datetime.fromtimestamp(ts_min)
	dt_max = datetime.datetime.fromtimestamp(ts_max)
	
	if last_launch < dt_min or last_launch > dt_max:
		return False # the process is the wrong age, not the VM

	f = open(cmd_path, 'r')
	cmdline = f.read(8192)
	f.close()
	cmds = cmdline.split("\x00")
	if cmds[0] != config.TOOL_KVM:
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

def write_to_serial(vm_object,data):
	"""
	Sends data to a VM's serial line.
	"""
	assert vm_object is not None
	assert check_vm_status(vm_object) is True
	
	serial_pt = vm_object.console_pt
	
	m_w = os.open(serial_pt,os.O_WRONLY)
	os.write(m_w,data)
	os.close(m_w)

def read_from_serial(vm_object):
	"""
	Reads data from a VM's serial line.
	"""
	assert vm_object is not None
	assert check_vm_status(vm_object) is True
	
	serial_pt = vm_object.console_pt
	
	m_r = os.open(serial_pt,os.O_RDONLY)
	data = os.read(m_r,4096)
	os.close(m_r)
	
	return data

def mount_iso(vm_object, iso_name):
	"""
	Verify that a VM is powered on, and mount an ISO
	"""
	assert vm_object is not None
	assert iso_name is not None
	assert check_vm_status(vm_object) is True
	
	iso_list = []
	for f in os.listdir(os.path.abspath(config.ISO_DIR)):
		module_name, ext = os.path.splitext(f)
		if ext == '.iso':
			iso_list.append(f)
	assert iso_name in iso_list
	
	iso_full_path = os.path.join(config.ISO_DIR,iso_name)
	monitor_cmd = "change ide1-cd0 " + iso_full_path + "\n"
	write_to_monitor(vm_object,monitor_cmd)

def reset_vm(vm_object):
	"""
	Verify that a VM is powered on, and reset it
	"""
	assert vm_object is not None
	assert check_vm_status(vm_object) is True
	
	monitor_cmd = "system_reset\n"
	write_to_monitor(vm_object,monitor_cmd)

def power_off(vm_object):
	"""
	Verify that a VM is powered on and power it off.
	"""
	
	assert vm_object is not None
	assert check_vm_status(vm_object) is True
	
	monitor_cmd = "quit\n"
	write_to_monitor(vm_object,monitor_cmd)

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
	
	assert len(disk_images) > 0 and len(disk_images) < 27
	alphabet = "abcdefghijklmnopqrstuvwxyz"
	hd_param = ""
	for i in range(0,len(disk_images)):
		hd_param = hd_param + " -hd%c %s" % (alphabet[i],disk_images[i])
	
	vnc_param = "%s:%i,password" % (config.VNC_IP,vm_object.id)
	
	smp_param = vm_object.cpu_cores
	mem_param = vm_object.memory
	mac_param = vm_object.mac_address
	
	assert smp_param is not None
	assert mem_param is not None
	assert vnc_param is not None
	assert hd_param != "" and hd_param is not None
	assert mac_param is not None
	
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
	kvm_params = "-net nic,macaddr=%s -net tap,ifname=%s,script=%s,downscript=%s %s -smp %i -m %i -serial pty -monitor pty -vnc %s -daemonize" % (mac_param,tap,config.IFUP_SCRIPT,config.IFDOWN_SCRIPT,hd_param,smp_param, mem_param, vnc_param)
	kvm_param_list = [config.TOOL_KVM] + kvm_params.split()
	
	proc = subprocess.Popen(kvm_param_list,close_fds=True,stderr=subprocess.PIPE)
	known_pid = proc.pid
	proc_errdata = proc.stderr.read()
	proc.stderr.close()
	
	pt = ptree.ProcessTree()
	pid = None
	for ptn in pt.proclist:
		proc_hit = True
		if len(ptn.cmdline) - 1 == len(kvm_param_list):
			for i in range(0,len(kvm_param_list)):
				if ptn.cmdline[i] != kvm_param_list[i]:
					proc_hit = False
		else:
			proc_hit = False
		
		if proc_hit is True:
			if ptn.pid != known_pid:
				pid = ptn.pid
	
	if pid is None:
		raise "Could not find PID of child process"
	
	monitor_pt = None
	serial_pt = None
		
	# Try to find the names of the two pts
	m = re.match(r'char device redirected to ([a-zA-Z0-9/]*)\nchar device redirected to ([a-zA-Z0-9/]*)', proc_errdata) # why does this come out via stderr? :/

	# First line is the monitor, second line is the serial console
	monitor_pt = m.group(1)
	serial_pt = m.group(2)
	
	m_r = None
	m_w = None
	for i in range(0, 10):
		try:
			if m_r is None:
				m_r = os.open(monitor_pt, os.O_RDONLY)
			if m_w is None:
				m_w = os.open(monitor_pt, os.O_WRONLY)
		except OSError:
			time.sleep(1)
	
	assert m_r is not None
	assert m_w is not None
	
	data = os.read(m_r,4096)
	
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
