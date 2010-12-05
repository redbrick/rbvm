# coding=utf-8
import sqlalchemy
import random
import string
import hashlib
import os
import base64
import datetime

from sqlalchemy import Table,Column,MetaData,ForeignKey
from sqlalchemy.schema import Sequence
from sqlalchemy import Integer,String,DateTime,Unicode,SmallInteger,Text,Binary,Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relation,backref

import rbvm.lib.sqlalchemy_tool as database

session = None # Initialised at runtime by single-threaded daemons (multi threaded daemons use sqlalchemy_tool)

Base = declarative_base()

class User(Base):
    """
    User
    """
    # {{{
    __tablename__ = 'user_table'
    
    id = Column(Integer,Sequence('user_table_id_seq'),primary_key=True)
    username = Column(String(255),unique=True,nullable=False)
    salt = Column(String(10),nullable=False)
    password = Column(String(255),nullable=False)
    email_address = Column(String(255),nullable=False)
    
    def set_password(self,password_plain):
        salt = ''.join(random.Random().sample(string.letters + string.digits,9))
        hash = hashlib.sha256()
        hash.update(password_plain + salt)
        self.password = hash.hexdigest()
        self.salt = salt
        
    def __repr__(self):
        return "<User('%s')>" % (self.username)
    
    def __init__(self,username,email_address,password_plain=None):
        self.username = username
        
        if not password_plain:
            password_plain = "".join(random.sample(string.letters + string.digits,8))
        
        self.set_password(password_plain)
        self.email_address = email_address
    
    # }}}

user_group = Table('user_group',Base.metadata, # {{{
    Column('user_id',Integer,ForeignKey('user_table.id')),
    Column('group_id',Integer,ForeignKey('group_table.id'))
) # }}}

class Group(Base):
    """
    User gorup
    """
    # {{{
    __tablename__ = 'group_table'

    id = Column(Integer,Sequence('group_table_id_seq'),primary_key=True)
    name = Column(String(255))
    
    users = relation('User',secondary=user_group,backref='groups')

    def __repr__(self):
        return "<Group('%s')>" % (self.name)
    
    def __init__(self,name):
        self.name = name
    
    # }}}

class DiskImage(Base):
    """
    A VM disk image
    """
    # {{{
    __tablename__ = 'disk_image'

    id = Column(Integer,Sequence('disk_image_id_seq'),primary_key=True)
    name = Column(String(255))
    size = Column(Integer)
    filename = Column(Text,unique=True)
    virtual_machine_id = Column(ForeignKey('virtual_machine.id'))
    
    def __repr__(self):
        return "<DiskImage('%s')>" % (self.filename)
    
    def __init__(self,filename,size,user,virtual_machine):
        self.filename = filename
        self.size = size
        self.user_id = user.id
        self.virtual_machine_id = virtual_machine.id
    
    # }}}

class Property(Base):
    """
    A VM property
    """
    # {{{
    __tablename__ = 'property'
    
    id = Column(Integer,Sequence('property_id_seq'),primary_key=True)
    key = Column(String(255),nullable=False)
    value = Column(String(255))
    virtual_machine_id = Column(ForeignKey('virtual_machine.id'))
    
    def __repr__(self):
        return "<Property('%s','%s')>" % (self.key,self.value)
    
    def __init__(self,key,value,virtual_machine):
        self.virtual_machine_id = virtual_machine.id
        self.key = key
        self.value = value
    # }}}

class VirtualMachine(Base):
    """
    A virtual machine
    """
    # {{{
    __tablename__ = 'virtual_machine'

    id = Column(Integer,Sequence('virtual_machine_id_seq'),primary_key=True)
    name = Column(String(255))
    user_id = Column(ForeignKey('user_table.id'))
    pid = Column(Integer,nullable=True)
    memory = Column(Integer)
    cpu_cores = Column(Integer)
    last_launch = Column(DateTime,nullable=True)
    assigned_ip = Column(String(255))
    mac_address = Column(String(255))
    nic_device = Column(String(20)) # ne2k_pci,i82551,i82557b,i82559er,rtl8139,e1000,pcnet,virtio
    hpet = Column(Boolean)
    acpi = Column(Boolean)
    no_kvm_irqchip = Column(Boolean)
    vga_device = Column(String(20)) # cirrus,std,vmware
    boot_device = Column(String(255))
    properties = relation('Property',order_by='Property.id',backref='virtual_machine')
    
    def __repr__(self):
        return "<VirtualMachine('%s')>" % (self.name)
    
    def __init__(self,name,user):
        self.name = name
        self.user_id = user.id
    
    # }}}


"""
Which users may add or remove VMs from a given VLAN.
"""
user_admin_vlan = Table('user_admin_vlan', Base.metadata,
    Column('user_id',Integer,ForeignKey('user_table.id')),
    Column('vlan_id',Integer,ForeignKey('vlan.id'))
)

"""
Which user groups may add or remove VMs from a given VLAN.
"""
group_admin_vlan = Table('group_admin_vlan', Base.metadata,
    Column('user_id',Integer,ForeignKey('group_table.id')),
    Column('vlan_id',Integer,ForeignKey('vlan.id'))
)

"""
Virtual machine <-> VLAN relationships
"""
vm_vlan = Table('vm_vlan',Base.metadata,
    Column('vm_id',Integer,ForeignKey('virtual_machine.id')),
    Column('vlan_id',Integer,ForeignKey('vlan.id'))
)

class Vlan(Base):
    """
    A VLAN
    """
    __tablename__ = 'vlan'
    
    id = Column(Integer, Sequence('vlan_id_seq'), primary_key=True)
    system_identifier = Column(String(1024),unique=True) # The system identifier for this vlan. For example, 'br1' for a linux bridge backend. Has a crazily long size in case we ever port to something nuts like windows, which will probably want a GUID code for an identifier.
    
    virtual_machines = relation('VirtualMachine',secondary=vm_vlan,backref='vlans')
    admin_users = relation('User',secondary=user_admin_vlan,backref='adminned_vlan')
    admin_groups = relation('Group',secondary=group_admin_vlan,backref='adminned_vlans')
    
    def __repr__(self):
        return "<Vlan(%i,'%s')>" % (self.id, self.system_identifier)
    
    def __init__(self, system_identifier):
        self.system_identifier = system_identifier

class OneTimeToken(Base):
    """
    A token that can be sent to the client (in unreadable form) and sent
    back to verify a command's origin.
    """
    # {{{
    __tablename__ = 'one_time_token'
    
    id = Column(Integer,Sequence('one_time_token_id_seq'),primary_key=True)
    token = Column(String(255),index=True)
    timestamp = Column(DateTime)
    used = Column(Boolean)
    user_id = Column(ForeignKey('user_table.id'))
    
    def __repr__(self):
        return "<OneTimeToken('%s')>" % (self.token)
    
    def __init__(self,user):
        assert user is not None
        
        # Generate a random token
        self.token = base64.b64encode(os.urandom(200))[:255]
        self.timestamp = datetime.datetime.now()
        self.used = False
        self.user_id = user.id
    
    def check_and_expire(self,user):
        """
        Returns whether or not a token has been used before or is invalid,
        and marks the token as used.
        """
        
        seconds = 60 * 15
        delta = datetime.timedelta(seconds=seconds)
        
        try:
            assert user is not None
            assert self.user_id == user.id
            assert self.used == False and self.timestamp + delta > datetime.datetime.now()
        except AssertionError:
            return True
        
        self.used = True
        
        if session is None:
            database.session.commit()
        else:
            session.commit()
        
        return False
    # }}}
