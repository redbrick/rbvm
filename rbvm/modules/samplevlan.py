# coding=utf-8
"""
 ____  _____    _    ____    __  __ _____ _ 
|  _ \| ____|  / \  |  _ \  |  \/  | ____| |
| |_) |  _|   / _ \ | | | | | |\/| |  _| | |
|  _ <| |___ / ___ \| |_| | | |  | | |___|_|
|_| \_\_____/_/   \_\____/  |_|  |_|_____(_)
                                            
A sample implementation of a VLAN control module. A VLAN control module allows 
a VM monitor to interface with the underlying VLAN mechanism (i.e. linux 
bridging, userspace VLANs, etc) in use by the system administrator. 

Two initial VLAN control modules are planned - one to interface with
linux bridge-utils (brctl, etc) and another to use KVM's built-in userland
vlan support.

None of the functions that are "public" actually do anything directly. They
all take a single tuple argument specifying the VM monitor in use 
 - e.g. ('name','version'), or ('kvm', '0.1'), and return a function to be used
by that VM monitor whenever it requires it. This function is written
specifically for that VM monitor to talk to this VLAN implementation.

This approach was chosen as writing a generic VM monitor interface is extremely
difficult, given the differences in how various underlying VM monitors and VLAN
implementations may operate.
"""
from rbvm.errors import *

# This is a VLAN control module.
MODULE_TYPE = 'vlan'
MODULE_NAME = 'samplevlan'
MODULE_VERSION = '1.0'

SUPPORTED_VMMON = [('samplevmmon', '1.0')]

def get_vlan_create_action(vmmon_implementation):
    """Return a function that allows the VM monitor specified to create a VLAN
    entry.
    """
    raise NotARealImplementationError

def get_vlan_delete_action(vmmon_implementation):
    """Return a function that allows the VM monitor specified to delete a VLAN
    entry.
    """
    raise NotARealImplementationError

def get_vlan_initialise_action(vmmon_implementation):
    """Return a function that allows the VM monitor specified to initialise a
    VLAN, if required. For example, the function returned by this by the 
    linux bridge VLAN implementation would run brctl addbr brX.
    """
    raise NotARealImplementationError

def get_vlan_shutdown_action(vmmon_implementation):
    """Return a function that allows the VM monitor specified to shut down a 
    VLAN.
    """
    raise NotARealImplementationError

def get_check_vlan_status_action(vmmon_implementation):
    """Return a function that allows the VM monitor specified to determine 
    whether or not a VLAN has been initialised with the underlying mechanism. If
    no initialisation is required, the function returned by this function should
    always return True.
    """
    raise NotARealImplementationError

def get_vm_add_action(vmmon_implementation):
    """Return a function that allows the VM monitor specified to add a VM to
    a VLAN.
    """
    raise NotARealImplementationError

def get_vm_remove_action(vmmon_implementation):
    """Return a function allowing the VM monitor specified to remove a VM from
    a VLAN.
    """
    raise NotARealImplementationError

def get_vm_connection_status_action(vlan_object,vmmon_implementation):
    """Return a function that allows the VM monitor specified to check the
    status of a virtual machine regarding this VLAN (i.e. whether or not this
    VM is connected to this VLAN or not).
    """
    raise NotARealImplementationError
    
