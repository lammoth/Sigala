# -*- coding: utf-8 -*-
##\namespace dbus

import dbus
import dbus.service

from sigala.profesor.idbusmodule import IDbusModule

##\class SItalcModule
#\brief Italc module for accesing the data.
class SItalcModule(dbus.service.Object, IDbusModule):
    ##\fn __init__(self, bus, core)
    #\brief Instanciates a dbus module
    #\param bus DBus bus to register with.
    #\param core Reference to the application's core.
    def __init__(self, bus, core):
        self.core = core
        name = dbus.service.BusName('org.cga.sigala', bus)
        self.path = '/org/cga/sigala/italc'
        dbus.service.Object.__init__(self, name, self.path)

    ##\fn get_user_data(self)
    #\brief Returns data needed by italc to make the configuration file.
    @dbus.service.method('org.cga.sigala.italc')
    def get_user_data(self):
        if not hasattr(self.core, "muc_name"):
             # No MUC/resource right now.
            return None
        else:
            classroom = self.core.muc_name
            # We don't want to accidentally mess with the users dict, so we copy it.
            users = dict(self.core.users)
            # We will return a more compact dict.
            pupils = dict()
            for user in users:
                name = users[user]["nick"]
                ip = users[user]["IP"]
                pupils[name] = ip

        return classroom, pupils
