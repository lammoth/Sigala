# -*- coding: utf-8 -*-
## \namespace profesor
#  \brief Loader of DBus modules

import sys
import os
import logging
import logging.config
import dbus
import dbus.service
import dbus.mainloop.glib
import gobject

from dbus.mainloop.glib import DBusGMainLoop

from sigala.profesor.settings import DBUS_MODULES
from sigala.common.settings import LOGGING_CONFIG_FILE

logging.config.fileConfig(LOGGING_CONFIG_FILE)
linfo = logging.info
lerror = logging.error
ldebug = logging.debug

## \class SDbus
#  \brief Load different modules for access to internal structures
class SDbus:
    """
    Carga los diferentes módulos de acceso a las estructuras
    de datos internas del sistema
    """

    ## \fn __init__(self, bus, core)
    #  \brief Initialize loader of DBus modules
    #  \params bus core
    def __init__(self, bus, core):
        self.dbus_session = bus
        self.core = core
        l = self.load_modules()

    ## \fn load_modules(self)
    #  \brief Loads and register DBus modules
    def load_modules(self):
        linfo("Loading DBUS modules\n%s\n" % ('-'*80))
        # Loads and register DBus modules
        module_list = []
        modules = __import__(DBUS_MODULES, fromlist=["*",])
        for m in dir(modules):
            if m.startswith("sdbus"):
                module = modules.__dict__[m]
                try:
                    self.load_module(module)
                except Exception,mod_name:
                    lerror("Error loading module: '%s'" % mod_name)

    ## \fn load_module(self, module_name, bus, core)
    #  \brief Instantiate classes from modules
    def load_module(self, module_name):
        # Register a DBus module 'module_name'
        for t in dir(module_name):
            if t.startswith("S"):
                linfo("Instantiating '%s'" % t)
                mod_inst = module_name.__dict__[t](self.dbus_session, self.core)

if __name__=="__main__":
    from sigala.profesor.scoreprofe import SCoreProfe
    dbus_loop = DBusGMainLoop()
    session = dbus.SessionBus(mainloop=dbus_loop)
    main_loop = gobject.MainLoop()
    c = SCoreProfe()
    test = SDbus(session, c)
    main_loop.run()
