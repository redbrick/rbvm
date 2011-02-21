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

from rbvm.errors import *

# This is a VM Monitor control module.
MOTULE_TYPE = 'vmmon'
MODULE_NAME = 'samplevmmon'
MODULE_VERSION = '1.0'

def get_vm_status(vm_object):
    """
    Return true or false, indicating whether or not the VM
    is powered on (True) or powered off (False).
    """
    raise NotARealImplementationError

def list_block_devices(vm_object):
    """
    Return a list of (identifier, type) tuples describing block
    devices on the VM.
    """
    raise NotARealImplementationError

def set_boot_priority(vm_object, device_list):
    """
    Takes a list of boot device identifiers and sets the boot priority
    list for this VM.
    """
    raise NotARealImplementationError

def mount_iso(vm_object, iso_object, device_identifier=None):
    """
    Mount an ISO image on the virtual machine. If a device_identifier
    is provided, try to mount it to that device. If none is given,
    default to the first optical device.
    """
    raise NotARealImplementationError

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
    raise NotARealImplementationError

def power_off(vm_object):
    """
    Hard power-off a VM.
    """
    raise NotARealImplementationError

def acpi_shutdown(vm_object):
    """
    Send ACPI shutdown to a VM.
    """
    raise NotARealImplementationError

def power_on(vm_object):
    """
    Power on a VM.
    """
    raise NotARealImplementationError

