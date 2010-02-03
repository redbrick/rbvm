import rbvm.config as config

# validate vmmon setting - only supports kvm for now
assert config.VMMON in ['kvm']

_vmmon = __import__("rbvm.%s" % config.VMMON, globals(), locals(), ['create_vm','check_vm_status'], -1)

create_vm = _vmmon.create_vm
check_vm_status = _vmmon.check_vm_status
power_on = _vmmon.power_on
