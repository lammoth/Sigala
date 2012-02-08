#!/usr/bin/python
# -*- coding: utf-8 -*-
## \namespace profesor

import subprocess
import time
import sys
import os
import random
import logging

from sigala.common.settings import LOGGING_CONFIG_FILE

from sigala.common.netdev import NetDev

from sigala.profesor.settings import SHARED_PRIVATE_DIR
from sigala.profesor.settings import SHARED_DIR

##\class SSharedDir
# \brief Creates shared dir resource
class SSharedDir:
    ##\fn __init__(self, groupname)
    # \brief Initialization webdav parameters
    # \param[in] groupname: Group name
    def __init__(self, groupname):
        logging.config.fileConfig(LOGGING_CONFIG_FILE)
        self.log = logging.getLogger('sigala.server')
        self.dir = SHARED_DIR
        try:
            self.IP = '%s' % NetDev().default_ip()
        except:
            self.log.error("Error al obtener IP por defecto!")
        self.port = '8008'
        self.user = ''.join(random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 8))
        self.password = ''.join(random.sample('ABCDEFGHIJKLMNOPQRSTUVWXYZ', 8))
        self.group = groupname
        self.create_dirs()

    ##\fn start(self)
    # \brief Start webdav serrver
    def start(self):
        self.popen(['davserver', '-D', self.dir, '-H', self.IP, '-P', self.port, '-u', self.user, '-p', self.password, '-d' ,'start'])

    ##\fn stop(self)
    # \brief Stop webdav server
    def stop(self):
        self.popen(['davserver', '-D', self.dir, '-H', self.IP, '-P', self.port, '-u', self.user, '-p', self.password, '-d' ,'stop'])

    ##\fn create_dirs(self)
    # \brief Initialization of shared directories
    def create_dirs(self):
        if os.access(self.dir, os.F_OK) == False:
            os.mkdir(self.dir, 0755)
        if os.access(SHARED_PRIVATE_DIR, os.F_OK) == False:
            os.mkdir(SHARED_PRIVATE_DIR, 0755)
# La carpeta de grupo la crean los clientes
#       if os.access(os.path.join(SHARED_PRIVATE_DIR, self.group), os.F_OK) == False:
#           os.mkdir(os.path.join(SHARED_PRIVATE_DIR, self.group), 0755)
                
    ##\fn popen(self, cmd)
    # \brief Aux method for executing system command
    # \param[in] cmd: system command and options
    def popen(self, cmd):
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=sys.stderr, stdin=subprocess.PIPE)
        res = process.communicate()
        return process, res
