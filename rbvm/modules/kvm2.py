# coding=utf-8
"""
 ____  _____    _    ____    __  __ _____ _ 
|  _ \| ____|  / \  |  _ \  |  \/  | ____| |
| |_) |  _|   / _ \ | | | | | |\/| |  _| | |
|  _ <| |___ / ___ \| |_| | | |  | | |___|_|
|_| \_\_____/_/   \_\____/  |_|  |_|_____(_)
                                            
Sample implementation of a VM monitor module.

The vm_object parameter being sent to most functions is an instance of a VM
bean. (Yeah, Python doesn't have beans, but I've been spending too much time
around Java recently). This could then be backed with any datastore, as long
as it provides the information that the VM monitors require. Haven't yet come
up with a definitive interface for those beans.
"""

import datetime

from rbvm.errors import *
import rbvm.config as config

# This is a VM Monitor control module.
MOTULE_TYPE = 'vmmon'
MODULE_NAME = 'kvm2'
MODULE_VERSION = '0.1'
MODULE_CN = 'ie.dcu.redbrick.rbvm.kvm2'

TS_FMT = '%Y-%m-%d %H:%M:%S'

def _get_monitor_socket(vm_object):
    """
    Returns a TCP stream socket connected to the VM's monitor.
    """
    assert get_vm_status(vm_object) is True
    
    monitor_base_port = config.get_module_config_int(MODULE_NAME, 'monitorbase', 4000)
    monitor_tcp_port = vm_object.get_unique_number(monitor_base_port, monitor_base_port + 500)
    
    monitor_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    monitor_socket.connect((config.IO_LISTEN_ADDRESS, monitor_tcp_port))
    return monitor_socket

def _get_serial_socket(vm_object):
    """
    Returns a TCP stream socket connected to the VM's serial
    port.
    """
    assert get_vm_status(vm_object) is True
    
    serial_base_port = config.get_module_config_int(MODULE_NAME, 'serialbase', 4500)
    
    serial_tcp_port = vm_object.get_unique_number(serial_base_port, serial_base_port + 500)
    serial_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    serial_socket.connect((config.IO_LISTEN_ADDRESS, serial_tcp_port))
    return serial_socket


def _get_parallel_socket(vm_object):
    """
    Returns a TCP stream socket connected to the VM's parallel
    port.
    """
    assert get_vm_status(vm_object) is True
    
    parallel_base_port = config.get_module_config_int(MODULE_NAME, 'parallelbase', 5000)
    
    parallel_tcp_port = vm_object.get_unique_number(parallel_base_port, parallel_base_port + 500)
    
    parallel_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    parallel_socket.connect((config.IO_LISTEN_ADDRESS, parallel_tcp_port))
    return parallel_socket

def get_vm_status(vm_object):
    """
    Return true or false, indicating whether or not the VM
    is powered on (True) or powered off (False).
    """
    known_pid = vm_object.get_property(MODULE_CN + '.known_pid')
    last_launch = datetime.datetime.strptime(vm_object.get_property(MODULE_CN + '.last_launch'))
    
    if known_pid is None or last_launch is None:
        return False # missing data
    
    try:
        known_pid = int(known_pid)
        last_launch = datetime.datetime.strptime(last_launch, TS_FMT)
    except:
        return False # invalid data
    
    cmd_path = '/proc/' + str(known_pid) + '/cmdline'
    
    if not os.path.exists(cmd_path):
        if config.DEBUG_MODE is True:
            cherrypy.log("DEBUG: check_vm_status for vm %i (known pid: %i) failed on os.path.exists(cmd_path)." % (vm_object.get_unique_identifier(), known_pid))
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

def list_block_devices(vm_object):
    """
    Return a list of (identifier, type) tuples describing block
    devices on the VM.
    
    type will be one of: floppy, hd, cdrom
    """
    
    monitor_socket = _get_monitor_socket(vm_object)
    monitor_socket.send("info block\n")
    block_info = socket.recv(4096)
    monitor_socket.close()

    devices = []
    for line in lines:
        m = re.match(r'([^:]+): type=(.*?) removable=[01].*$', line)
        if m is not None:
            # device match
            devices.append((m.group(1),m.group(2)))
    
    return devices

def set_boot_priority(vm_object, device_list):
    """
    Takes a list of boot device identifiers and sets the boot priority
    list for this VM.
    """
    known_block_devices = list_block_devices(vm_object)
    
    # check that the device exists
    assert device_list[0] in [x[0] for x in known_block_devices]
    
    top_type = device_list[0][1]
    boot_order = None
    if top_type == 'hd':
        boot_order = 'c'
    else:
        boot_order = 'd'
    
    monitor_socket = _get_monitor_socket(vm_object)
    monitor_socket.send("boot_set %s\n" % boot_order)
    monitor_socket.recv(4096)
    monitor_socket.close()

def mount_iso(vm_object, iso_object, device_identifier=None):
    """
    Mount an ISO image on the virtual machine. If a device_identifier
    is provided, try to mount it to that device. If none is given,
    default to the first optical device.
    """

    if device_identifier is None:
        device_identifier = "ide1-cd0"

    monitor_cmd = "change %s %s\n" % (device_identifier, iso_object.get_image_path())
    
    monitor_socket = _get_monitor_socket(vm_object)
    monitor_socket.send(monitor_cmd)
    monitor_socket.recv(4096)
    monitor_socket.close()

def mount_disk_image(vm_object, image_object, device_identifier=None):
    """
    Mount a disk image on the virtual machine. If a device_identifier is
    provided, try to mount it to that device. If none is given, default
    to the first unused block device. If no block devices are available,
    and no device identifier is given, raise a NoFreeDevicesException.
    """
    raise NotARealImplementationError

def reset_vm(vm_object):
    """
    Reset the VM (press the virtual reset button).
    """
    monitor_socket = _get_monitor_socket(vm_object)
    monitor_cmd = "system reset\n"

    monitor_socket.send(monitor_cmd)
    monitor_socket.recv(4096)
    monitor_socket.close()

def power_off(vm_object):
    """
    Hard power-off a VM.
    """
    monitor_socket = _get_monitor_socket(vm_object)
    monitor_cmd = "quit\n"

    monitor_socket.send(monitor_cmd)
    try:
        monitor_socket.close()
    except:
        pass

def acpi_shutdown(vm_object):
    """
    Send ACPI shutdown to a VM.
    """
    
    # Apparently, KVM doesn't support this :(

    raise NotARealImplementationError

def power_on(vm_object):
    """
    Power on a VM.
    """

    assert get_vm_status(vm_object) is False
    
    smp_param = None
    mem_param = None
    vnc_param = None
    hd_param = None
    disk_images = []

    # TODO finish
