import os
import os.path
import sys

import rbvm.config as config

_modules = {}

# Load all our modules.
sys.path.append(config.MODULE_DIR)
for f in os.listdir(os.path.abspath(config.MODULE_DIR)):
	module_name, ext = os.path.splitext(f)
	if ext == '.py':
		module = __import__(module_name, globals(), locals(), ['create_vm','check_vm_status','power_on','mount_iso','reset_vm'], -1)
		_modules[module_name] = module

# Validate vmmon setting
assert config.VMMON in _modules.keys()
_vmmon = _modules[config.VMMON]

create_vm = _vmmon.create_vm
check_vm_status = _vmmon.check_vm_status
power_on = _vmmon.power_on
mount_iso = _vmmon.mount_iso
reset_vm = _vmmon.reset_vm