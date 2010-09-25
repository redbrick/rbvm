# The next few variables are help strings for the "help" command. How
# interesting.
usage = {}

usage['index'] = """
rbvmctl is the rbvm command line utility. Any of the following subcommands
will work:

    listusers       Displays a list of users.
    listvms         Displays a list of virtual machines.
    showvm          Displays detailed information on a virtual machine.
    resetpw         Allows a user's password to be reset.
    help            Displays help information.

To get more information on a specific item, run 'rbvmctl help topicname',
where topicname is one of the commands listed above.
"""

usage['listusers'] = """
The listusers command will display a table of users registered with the
system, and their email addresses. There are no extra arguments or options
for this command.
"""

usage['listvms'] = """
The listvms command will display a table of virtual machines on the system.
The following columns are given:

    ID              A unique numeric identifier given to each VM.
    VM name         A descriptive name given to a VM. This may be modified by
                    the user through the web interface.
    Username        The username of the user to whom this VM belongs.
    Status          The current detected status (powered on or powerd off) of
                    this VM.
    PID             The last known process ID of this virtual machine on the
                    host system. If the VM is powered off, this is the PID
                    that was set the last time the VM ran.

There are no extra arguments or options for this command.
"""

usage['resetpw'] = """
The resetpw command allows a user's password to be reset. The new password
will be generated at random and will automatically be emailed to the address
associated with that user in the database. Use the listusers command to view
the information on file for each user.

The resetpw command requires an argument specifying the username of the user
whose password is to be reset. For example:

rbvmctl resetpw bob

will reset the password for the user 'bob'.
"""

usage['help'] = """
Are you serious?
"""

usage['showvm'] = """
Displays detailed technical information on a virtual machine. The showvm
command requires an argument specifying the numeric identifier associated
with the VM. To get a list of identifiers, use the listvms command.
"""