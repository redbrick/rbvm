# Copyright (c) 2010, Andrew Martin
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#     * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL ANDREW MARTIN BE LIABLE FOR ANY
# DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
# ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import os.path
import os
import datetime

class ProcessTree:
    """
    Scans /proc and builds a tree of ProcessTreeNodes representing
    processes on the system. Includes the print_tree() method for pretty
    output.
    """
    def __init__(self):
        """
        Builds the process tree. Takes no arguments.
        """
        self.init = None
        self.proclist = []
        proc = os.listdir('/proc')
        for fname in proc:
            
            try:
                pid = int(fname)
            except ValueError:
                continue
            ptn = ProcessTreeNode(pid, self.proclist)
            if ptn.valid is True:
                if pid == 1:
                    self.init = ptn
                
                self.proclist.append(ptn)
        
        for ptn in self.proclist:
            for ptn2 in self.proclist:
                if ptn.parent_pid == ptn2.pid:
                    ptn.parent = ptn2
                    ptn2.add_child(ptn)
    
    def get_process(self, pid):
        """
        Returns a ProcessTreeNode representing a given process. Requires an
        integer (the process ID) as an argument.
        """
        pid = int(pid)
        for proc in self.proclist:
            if proc.pid == pid:
                return proc
        
        return None
    
    def print_tree_step(self,level,proc):
        """
        Used by print_tree()
        """
        assert proc is not None
        indent = " " * level
        for child in proc.children:
            print "%s%i [%s]" % (indent, child.pid, ' '.join(child.cmdline))
            self.print_tree_step(level + 1, child)
    
    def print_tree(self):
        """
        Prints the process tree to stdout.
        """
        proc = self.get_process(1)
        print "1 init"
        self.print_tree_step(0,proc)

class ProcessTreeNode:
    """
    Represents a process
    """
    def __init__(self, pid, proclist):
        pid = int(pid)
        self.parent = None
        self.children = []
        self.pid = pid
        self._procdir = "/proc/%i" % pid
        self.parent_pid = None
        
        cmdline_fname = os.path.join(self._procdir,'cmdline')
        
        try:
            self.ctime = datetime.datetime.fromtimestamp(os.stat(cmdline_fname)[9])
        
            cmdline = open(cmdline_fname)
            cmdline_bin = cmdline.read()
            cmdline.close()
            self.cmdline = cmdline_bin.split("\x00")
        
            if pid != 1:
                status_file = open(os.path.join(self._procdir,'status'))
                lines = status_file.readlines()
                status_file.close()
            
                for l in lines:
                    if l.startswith("PPid:"):
                        ppid = l[6:]
                        self.parent_pid = int(ppid)
            self.valid = True
        except:
            self.valid = False
    
    def parent_is(self, compare_to):
        """
        Return True if the ProcessTreeNode passed in as compare_to is the parent of
        self. Otherwise return False.
        """
        if self.parent is None:
            return False
        return self.parent == compare_to
    
    def add_child(self,child):
        """
        Add the child passed via add_child as a child process.
        """
        self.children.append(child)
    
    def __repr__(self):
        return '<ProcessTreeNode(%i)>' % self.pid
    
    