"""
Command-line utilities
"""
import sys

from rbvm.model.database import *
import rbvm.config as config
import rbvm.vmmon
import rbvm.usage

def help(session, args, force):
	"""
	Displays help
	"""
	if len(args) < 1:
		key = 'index'
	else:
		key = args[0]
	
	if key not in rbvm.usage.usage:
		print "Unknown command"
	else:
		print rbvm.usage.usage[key]

def showvm(session, args, force):
	"""
	Outputs detailed information on a VM.
	"""
	try:
		id = int(args[0])
	except:
		print "Invalid VM identifier"
		sys.exit(1)
	
	vm = rbvm.vmmon.get_vm(id, session=session)
	if vm is None:
		print "Could not find VM."
		sys.exit(1)
	
	owner = session.query(User).filter(User.id==vm.user_id).one()
	status_boolean = rbvm.vmmon.check_vm_status(vm)
	
	format = "%20s : %s"
	print format % ("ID", str(vm.id))
	print format % ("Name", str(vm.name))
	print format % ("Username", str(owner.username))
	print format % ("Last known PID", str(vm.pid))
	print format % ("CPU cores",str(vm.cpu_cores))
	print format % ("Last launch", str(vm.last_launch))
	print format % ("Assigned IP", str(vm.assigned_ip))
	print format % ("MAC address", str(vm.mac_address))
	print format % ("NIC device setting", str(vm.nic_device))
	print format % ("HPET", "Enabled" if vm.hpet else "Disabled")
	print format % ("ACPI", "Enabled" if vm.acpi else "Disabled")
	print format % ("KVM IRQ chip", "Disabled" if vm.no_kvm_irqchip else "Enabled") # daargh, double negatives
	print format % ("VGA device setting", str(vm.vga_device))
	print format % ("Boot device", "CD drive" if vm.boot_device == 'd' else "Hard disk")
	print format % ("Current status", "Powered on" if status_boolean is True else "Powered off")

def listusers(session, args, force):
	"""
	Outputs a list of users in tabular format
	"""
	users = session.query(User).all()
	print "%-10s | %s" % ("Username","Email address")
	
	for user in users:
		print "%-10s | %s" % (user.username, user.email_address)

def listvms(session, args, force):
	"""
	Outputs a list of VMs in tabular format
	"""
	vms = session.query(VirtualMachine).all()
	print "Note: PID is the last known pid; ignore this field if the VM is powered off."
	print
	header_format = "%-5s | %-35s | %-10s | %-6s | %6s"
	line_format = "%5i | %-35.35s | %-10s | %-6s | %6s"
	header_tup_end = ()
	showips = False
	if len(args) > 0 and args[0] == 'showips':
		showips = True
		header_format = header_format + " | %s"
		header_tup_end = ('Assigned IP',)
		line_format = line_format + " | %s"
	
	print header_format % (("ID","VM name","Username","Status","PID") + header_tup_end)
	for vm in vms:
		owner = session.query(User).filter(User.id==vm.user_id).one()
		status_boolean = rbvm.vmmon.check_vm_status(vm)
		status = "Off"
		if status_boolean is True:
			status = "On"
		
		line_tup = (vm.id, vm.name, owner.username, status, str(vm.pid))
		
		if showips:
			line_tup = line_tup + (str(vm.assigned_ip),)
		
		print line_format % line_tup

def resetpw(session, args, force):
	"""
	Resets a user's password
	"""
	username = args[0]
	
	password = "".join(random.sample(string.letters + string.digits,8))
	user = session.query(User).filter(User.username==username).first()
	if user is None:
		print "User %s not found." % username
		sys.exit(1)
	
	user.set_password(password)
	session.commit()
	print "Password for user %s has been changed to: %s" % (username, password)
	print "Emailing user at %s" % user.email_address
	s = smtplib.SMTP()
	s.connect()
	s.sendmail(config.EMAIL_ADDRESS, user.email_address, "From: %s\nTo: %s\nSubject: Your VM account password has been reset\n\nYour VM account password has been reset. The new password is:\n\n%s\n\nRegards,\n-Automated mailing monkey" % (config.EMAIL_ADDRESS, user.email_address, password))
	s.quit()

def changename(session, args, force):
	"""
	Allows a VM's name to be changed.
	"""
	vm_id = args[0]
	int(vm_id)
	vm = rbvm.vmmon.get_vm(vm_id, session=session)
	
	name = args[1]
	rbvm.vmmon.change_vm_name(vm, name, session=session)
	print "VM name changed to %s" % name

def changeip(session, args, force):
	"""
	Allows a VM's assigned IP to be changed.
	"""
	vm_id = args[0]
	ip = args[1]
	int(vm_id)
	
	vm = rbvm.vmmon.get_vm(vm_id, session=session)
	rbvm.vmmon.set_assigned_ip(vm, ip, force=force, session=session, commit=True)
	print "VM IP changed to %s" % ip

commands = {
	'listusers': listusers,
	'listvms': listvms,
	'help': help,
	'showvm': showvm,
	'resetpw': resetpw,
	'changename': changename,
	'changeip': changeip,
}