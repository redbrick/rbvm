import os
import os.path
import sys

import rbvm.config as config

_modules = {}

# Load all our modules.
sys.path.append(config.MODULE_DIR)
for f in os.listdir(os.path.abspath(config.MODULE_DIR)):
	module_name, ext = os.path.splitext(f)
	if ext == '.py' and not module_name.startswith('._'):
		module = __import__(module_name, globals(), locals(), ['create_vm','check_vm_status','power_on','mount_iso','reset_vm','power_off','list_block_devices','set_boot_device'], -1)
		_modules[module_name] = module

# Validate vmmon setting
assert config.VMMON in _modules.keys()
_vmmon = _modules[config.VMMON]

create_vm = _vmmon.create_vm
check_vm_status = _vmmon.check_vm_status
power_on = _vmmon.power_on
mount_iso = _vmmon.mount_iso
reset_vm = _vmmon.reset_vm
power_off = _vmmon.power_off
list_block_devices = _vmmon.list_block_devices
set_boot_device = _vmmon.set_boot_device