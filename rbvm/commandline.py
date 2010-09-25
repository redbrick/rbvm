"""
Command-line utilities
"""
import sys

from rbvm.model.database import *
import rbvm.config as config
import rbvm.vmmon
import rbvm.usage

def help(session, args):
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

def showvm(session, args):
	"""
	Outputs detailed information on a VM.
	"""
	try:
		id = int(args[0])
	except:
		print "Invalid VM identifier"
		sys.exit(1)
	
	vm = session.query(VirtualMachine).filter(VirtualMachine.id==id).first()
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

def listusers(session, args):
	"""
	Outputs a list of users in tabular format
	"""
	users = session.query(User).all()
	print "%-10s | %s" % ("Username","Email address")
	
	for user in users:
		print "%-10s | %s" % (user.username, user.email_address)

def listvms(session, args):
	"""
	Outputs a list of VMs in tabular format
	"""
	vms = session.query(VirtualMachine).all()
	print "Note: PID is the last known pid; ignore this field if the VM is powered off."
	
	print "%-5s | %-35s | %-10s | %-6s | %6s" % ("ID","VM name","Username","Status","PID")
	for vm in vms:
		owner = session.query(User).filter(User.id==vm.user_id).one()
		status_boolean = rbvm.vmmon.check_vm_status(vm)
		status = "Off"
		if status_boolean is True:
			status = "On"
		
		print "%5i | %-35.35s | %-10s | %-6s | %6i" % (vm.id, vm.name, owner.username, status, vm.pid)

def resetpw(session, args):
	"""
	Resets a user's password
	"""
	try:
		username = args[0]
	except:
		print "Invalid or missing username"
	
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

commands = {
	'listusers': listusers,
	'listvms': listvms,
	'help': help,
	'showvm': showvm,
	'resetpw': resetpw,
}