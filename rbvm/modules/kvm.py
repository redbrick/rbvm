# coding=utf-8
import os
import os.path
import re
import random
import string
import subprocess
import time
import datetime
import cherrypy
import socket

from rbvm.errors import *
from rbvm.model.database import *
import rbvm.lib.sqlalchemy_tool as database
import rbvm.lib.ptree as ptree
import rbvm.config as config

# This is a VM monitor control module.
MODULE_TYPE = 'vmmon'

# KVM abstraction layer

def set_assigned_ip(vm_object, new_ip, force=False, session=database.session, commit=True):
    """
    Allows a VM's assigned IP address to be set.
    """
    print "IP assignment requested, checking previous allocations"
    conflict = True
    try:
        other_vm = session.query(VirtualMachine).filter(VirtualMachine.assigned_ip==new_ip).first()
        assert other_vm is not None
    except Exception,e:
        print str(e)
        print "No conflict found"
        conflict = False
    
    if conflict is True:
        print "***************************************************************************"
        print " WARNING: IP allocation conflict! The IP requested is already allocated!"
        print "***************************************************************************"
        if force is False:
            print "Aborting. Please specify -f or --force if you wish to continue anyway."
            return
        else:
            print "Apparently you want to force this, continuing (even though it's stupid)."
    
    vm_object.assigned_ip = new_ip
    if commit:
        session.commit()


def get_vm(vm_id, session=database.session):
    """
    Returns a VM object with the corresponding identifier
    """
    if session is None:
        raise MissingDatabaseSessionError
    
    vm_id = int(vm_id)
    vm = session.query(VirtualMachine).filter(VirtualMachine.id==vm_id).first()
    return vm


def change_vm_name(vm_object, name, session=database.session):
    """
    Allows a VM's name to be changed.
    """
    vm_object.name = name
    session.commit()


def create_vm(vm_properties, session=database.session, print_output=False):
    """
    Creates a virtual machine
    """
    
    if session is None:
        raise MissingDatabaseSessionError
    
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
    
    vm_name = "VM created at %s" % (datetime.datetime.now().isoformat())
    
    vm = VirtualMachine(vm_name, user)
    if vm_properties.ip is not None:
        set_assigned_ip(vm, vm_properties.ip, force=vm_properties.force, commit=False)
    
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
    
    
    
    vm.memory = ram_size
    vm.cpu_cores = cpu_cores
    vm.mac_address = mac_address
    vm.assigned_ip = vm_properties.ip
    vm.nic_driver = 'ne2k_pci'
    vm.boot_device = 'd'
    
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
        if config.DEBUG_MODE is True:
            cherrypy.log("DEBUG: check_vm_status for vm %i (known pid: %i) failed on os.path.exists(cmd_path)." % (vm_object.id, vm_object.pid))
        return False # can't find proc info, VM not running
    
    f = open(cmd_path, 'r')
    cmdline = f.read(8192)
    f.close()
    cmds = cmdline.split("\x00")
    if cmds[0] != config.TOOL_KVM:
        if config.DEBUG_MODE is True:
            cherrypy.log("DEBUG: check_vm_status for vm %i (known pid: %i) failed on KVM tool check." % (vm_object.id, vm_object.pid))
        return False # it's not KVM :( return false
    else:
        return True # all checks pass, the vm seems to be running


def get_monitor_socket(vm_object):
    """
    Returns a TCP stream socket connected to the VM's monitor.
    """
    assert vm_object is not None
    assert check_vm_status(vm_object) is True
    
    monitor_tcp_port = config.MONITOR_BASE_PORT + vm_object.id
    monitor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    monitor_socket.connect((config.IO_LISTEN_ADDRESS, monitor_tcp_port))
    return monitor_socket


def get_serial_socket(vm_object):
    """
    Returns a TCP stream socket connected to the VM's serial
    port.
    """
    assert vm_object is not None
    assert check_vm_status(vm_object) is True
    
    serial_tcp_port = config.SERIAL_BASE_PORT + vm_object.id
    serial_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serial_socket.connect((config.IO_LISTEN_ADDRESS, serial_tcp_port))
    return serial_socket


def get_parallel_socket(vm_object):
    """
    Returns a TCP stream socket connected to the VM's parallel
    port.
    """
    assert vm_object is not None
    assert check_vm_status(vm_object) is True
    
    parallel_tcp_port = config.PARALLEL_BASE_PORT + vm_object.id
    parallel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    parallel_socket.connect((config.IO_LISTEN_ADDRESS, parallel_tcp_port))
    return parallel_socket


def list_block_devices(vm_object):
    """
    Returns a list of (name, type) tuples showing block devices on 
    the VM
    """
    assert vm_object is not None
    assert check_vm_status(vm_object) is True
    
    monitor_socket = get_monitor_socket(vm_object)
    monitor_socket.send("info block\n")
    block_info = socket.recv(4096)
    monitor_socket.close()
    
    lines = block_info.splitlines()
    
    devices = []
    for line in lines:
        m = re.match(r'([^:]+): type=(.*?) removable=[01].*$', line)
        if m is not None:
            # device match
            devices.append((m.group(1),m.group(2)))
    
    return devices


def set_boot_device(vm_object,boot_list):
    """
    Sets the boot device of a VM
    """
    assert vm_object is not None
    assert check_vm_status(vm_object) is True
    assert boot_list in ['c','d']
    
    monitor_socket = get_monitor_socket(vm_object)
    monitor_socket.send("boot_set %s\n" % boot_list)
    monitor_socket.recv(4096)
    monitor_socket.close()


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
    
    monitor_socket = get_monitor_socket(vm_object)
    monitor_socket.send(monitor_cmd)
    monitor_socket.recv(4096)
    monitor_socket.close()


def reset_vm(vm_object):
    """
    Verify that a VM is powered on, and reset it
    """
    assert vm_object is not None
    assert check_vm_status(vm_object) is True
    
    monitor_socket = get_monitor_socket(vm_object)
    monitor_cmd = "system_reset\n"
    
    monitor_socket.send(monitor_cmd)
    monitor_socket.recv(4096)
    monitor_socket.close()


def power_off(vm_object):
    """
    Verify that a VM is powered on and power it off.
    """
    
    assert vm_object is not None
    assert check_vm_status(vm_object) is True
    
    monitor_socket = get_monitor_socket(vm_object)
    
    monitor_cmd = "quit\n"
    monitor_socket.send(monitor_cmd)
    try:
        monitor_socket.close()
    except:
        pass


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
    acpi_param = vm_object.acpi
    boot_param = vm_object.boot_device
    nic_param = vm_object.nic_device
    no_kvm_irqchip_param = vm_object.no_kvm_irqchip
    
    if no_kvm_irqchip_param is None:
        no_kvm_irqchip_param = False
    
    if nic_param not in ['ne2k_pci','i82551','i82557b','i82559er','rtl8139','e1000','pcnet','virtio']:
        nic_param = 'ne2k_pci'
    
    if boot_param not in ['c','d']:
        boot_param = 'd'
    
    if acpi_param is None:
        acpi_param = True
    
    monitor_tcp_port = config.MONITOR_BASE_PORT + vm_object.id
    serial_tcp_port = config.SERIAL_BASE_PORT + vm_object.id
    parallel_tcp_port = config.PARALLEL_BASE_PORT + vm_object.id
    
    assert smp_param is not None
    assert mem_param is not None
    assert vnc_param is not None
    assert hd_param != "" and hd_param is not None
    assert mac_param is not None
    assert boot_param in ['d','c']
    assert nic_param in ['ne2k_pci','i82551','i82557b','i82559er','rtl8139','e1000','pcnet','virtio']
    assert monitor_tcp_port > 1024
    assert serial_tcp_port > 1024
    assert parallel_tcp_port > 1024
    assert monitor_tcp_port != serial_tcp_port
    assert monitor_tcp_port != parallel_tcp_port
    assert serial_tcp_port != parallel_tcp_port
    assert vm_object.id + 5900 != monitor_tcp_port
    assert vm_object.id + 5900 != parallel_tcp_port
    assert vm_object.id + 5900 != serial_tcp_port
    assert no_kvm_irqchip_param is True or no_kvm_irqchip_param is False
    assert acpi_param is True or acpi_param is False
    
    # Generate vnc password:
    vnc_password = "".join(random.sample(string.letters + string.digits,8))
    
    # Assign the tap interface
    tap = "tap%i" % vm_object.id
    tunctl_params = [config.TOOL_SUDO,config.TOOL_TUNCTL,'-u',config.SYSTEM_USERNAME,'-t',tap]
    subprocess.call(tunctl_params)
    
    # Run brctl delif just to ensure that the tap isn't on the bridge before continuing
    brctl_params = [config.TOOL_SUDO,config.TOOL_BRCTL,'delif',config.NETWORK_BRIDGE,tap]
    subprocess.call(brctl_params) # we don't really care if this fails - in fact, we hope it will.
    
    if no_kvm_irqchip_param is True:
        no_kvm_irqchip_str = " -no-kvm-irqchip"
    else:
        no_kvm_irqchip_str = ""
    
    if acpi_param is False:
        acpi_str = " -no-acpi"
    else:
        acpi_str = ""
    
    # Run the vmm
    kvm_params = "-net nic,macaddr=%s,model=%s -net tap,ifname=%s,script=%s,downscript=%s %s -smp %i -m %i -serial tcp:%s:%i,server,nowait -monitor tcp:%s:%i,server,nowait -parallel tcp:%s:%i,server,nowait -vnc %s -boot order=%s%s %s -daemonize" % (mac_param,nic_param,tap,config.IFUP_SCRIPT,config.IFDOWN_SCRIPT,hd_param,smp_param, mem_param, config.IO_LISTEN_ADDRESS, serial_tcp_port, config.IO_LISTEN_ADDRESS, monitor_tcp_port, config.IO_LISTEN_ADDRESS, parallel_tcp_port, vnc_param, boot_param, no_kvm_irqchip_str, acpi_str)
    kvm_param_list = [config.TOOL_KVM] + kvm_params.split()
    
    if config.DEBUG_MODE is True:
        cherrypy.log("DEBUG: kvm_param_list is: %s" % str(kvm_param_list))
    
    proc = subprocess.Popen(kvm_param_list,close_fds=True)
    known_pid = proc.pid
    
    cherrypy.log("DEBUG: parent PID is: %i" % known_pid)
    
    for j in range(0,config.MAX_FORK_TIMEOUT):
        cherrypy.log("DEBUG: Trying to find child pid, attempt %i" % j)
        time.sleep(1)
        
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
        
        if pid is not None:
            break
    
    if pid is None:
        raise VMStartupError("Could not find PID of child process")
    
    monitor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    monitor_socket.connect((config.IO_LISTEN_ADDRESS, monitor_tcp_port))
    data = monitor_socket.recv(4096)
    assert data.startswith("QEMU ")
    monitor_socket.send("change vnc password\n")
    monitor_socket.recv(4096)
    monitor_socket.send(vnc_password + "\n")
    monitor_socket.recv(4096)
    monitor_socket.close()
    
    vm_object.last_launch = datetime.datetime.now()
    vm_object.pid = pid
    
    try:
        session.commit()
    except:
        database.session.commit()
    
    return vnc_password

