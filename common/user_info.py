# -*- coding: utf-8 -*-

##\namespace common
import sys
from pwd import getpwuid
from os import getuid

from subprocess import call as subcall


from PyQt4.QtCore import *
from PyQt4.QtGui import *

from sigala.common.netdev import NetDev
from sigala.common.settings import IDENTIFY_COMMAND

def get_sigala_user_name():
    settings = QSettings()
    nombre=settings.value("user/name", QVariant(None)).toString()
    return nombre

## \fn get_user_name
# \brief Returns the user name.
#\return string
def get_user_name():
    siguser = get_sigala_user_name()
    nombre = unicode(siguser)
    return nombre

##\fn get_hostname
#\brief Returns the FQDN
#\return string
def get_hostname():
    nd = NetDev()
    return nd.hostname()

##\fn generate_jid
#\brief Returns a JID for the user based on the MAC and the FQDN.
#\return string
def generate_jid(hostname=None):
    nd = NetDev()
    mac = nd.default_mac()
    name = filter(lambda k: k !=':', mac)
    server = (hostname, nd.hostname())[hostname is None]
    return str("%s@%s/SIGALA" % (name, server))

def identify_user():
    ret = subcall([IDENTIFY_COMMAND,])


if __name__=="__main__":
    u = get_user_name()
    print type(u)
    print u
    print generate_jid()
