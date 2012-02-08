# -*- coding: utf-8 -*-

import os
import signal

##\class SRunningControl
#\brief Checks if a process is running
class SRunningControl:
    def __init__(self, pid_file):
        self.pid_file = pid_file

    def is_running(self):
        try:
            with open(self.pid_file, "r") as f:
                try:
                    # Read the PID from the file
                    pid = int(f.read().strip())
                except ValueError:
                    # Something weird happened with the PID (not an int?). Assume it's
                    # an invalid PID.
                    return False
        except IOError, m:
            # NO such file. No running process
            return False
        # We have a PID, but is it really a SIGALA one?
        if not self.is_sigala_process(pid):
            # Remove the PID file, it doesn't contain a SIGALA PID...
            self.remove()
            return False
        else:
            return True

    def remove(self):
        try:
            os.unlink(self.pid_file)
        except OSError:
            # No such file, maybe SIGALA finished while checking...
            pass

    def create(self):
        pid = os.getpid()
        with open(self.pid_file, "w") as f:
            f.write("%s" % pid)
        os.chmod(self.pid_file, 0666)

    def is_sigala_process(self, pid):
        procpath="/proc/%s/cmdline" % pid
        try:
            cmdline=open(procpath,"r").read()
        except IOError:
            # No such file? So, no such process either. Maybe the process 
            # finished while we were checking it.
            return False
        # If the command line includes "cga-sigala[-client]" then 
        # it's a SIGALA process
        return cmdline.find("cga-sigala") != -1

