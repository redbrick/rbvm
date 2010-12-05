# coding=utf-8
"""
A sample implementation of a VLAN control module. A VLAN control
module provides, and describes to the VM monitor module how to interface
with the underlying VLAN mechanism in use by the system administrator.

Two initial VLAN control modules are planned - one to interface with
linux bridge-utils (brctl, etc) and another to use KVM's built-in userland
vlan support.

Important actions are:
 * Create a VLAN with the underlying mechanism, if required.
 * Permanently delete a VLAN from the underlying mechanism, if required.
 * Initialise a VLAN with the underlying mechanism, if required.
 * Shut down the VLAN on the underlying mechanism, if required.
 * Return a tuple describing the action that the VM monitor module needs
   to take to add a VM to a VLAN.
 * Return a tuple describing the action that the VM monitor module needs
   to take to remove a VM from a VLAN, if any.

The VM monitor module, in all of this, is to be responsible for:

 * Carrying out actions as specified by the add/remove VM methods in this module.
 * Making sure that at initialisation, a VM is connected to all of the VLANs that
   it is supposed to be, in the database.
 * Making sure that the VLANs required are initialised prior to adding or removing
   virtual machines.
 * Something else was meant to go here. I'm hungry. #TODO remember what this was.
"""
from rbvm.errors import *

# This is a VLAN control module.
MODULE_TYPE = 'vlan'

def create_vlan(vlan_object):
    """
    Creates a VLAN with the underlying VLAN mechanism, if required.
    """
    raise NotARealImplementationError


def delete_vlan(vlan_object):
    """
    Permanently delete the VLAN with the underlying VLAN mechanism, if required.
    """
    raise NotARealImplementationError


def initialise_vlan(vlan_object):
    """
    Initialise the VLAN, if required. For example, the linux bridge-utils
    package requires "brctl addbr brX" to be run.
    """
    raise NotARealImplementationError


def shutdown_vlan(vlan_object):
    """
    Shut down the VLAN, if required.
    """
    raise NotARealImplementationErro


def check_vlan_status(vlan_object):
    """
    Check whether or not the VLAN has been initialised with the underlying
    mechanism. If no initialisation is required, just return true.
    """
    raise NotARealImplementationError


def get_vm_add_action(vlan_object,vmmon_implementation):
    """
    Return a tuple describing the action to be taken by the VM monitor module
    to add a virtual machine to the VLAN specified, if any.
    """
    raise NotARealImplementationError


def get_vm_remove_action(vlan_object,vmmon_implementation):
    """
    Return a tuple describing the action to be taken by the VM monitor module
    to remove a vitual machine from the VLAN specified, if any.
    """
    raise NotARealImplementationError

def get_vm_connection_status_action(vlan_object,vmmon_implementation):
    """
    Return a tuple describing the action to be taken by the VM monitor module
    to check the status of the virtual machine regarding this VLAN (whether
    it is connected or not).
    """