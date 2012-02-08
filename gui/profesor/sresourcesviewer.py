#!/usr/bin/env python
# -*- coding: utf-8 -*-
##\namespace alumno

import sys
import os
import logging
import logging.config
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from threading import Lock

from sigala.gui.profesor.ui_resources_viewer import Ui_SResourceViewer
import sigala.gui.profesor.sigala_resources

##\class SResourceViewer
# \brief Window for show network resources.
class SResourceViewer(QWidget, Ui_SResourceViewer):

    ## \fn __init__(self)
    # \brief .
    def __init__(self, mdns, jid, users):
        super(SResourceViewer, self).__init__(None)
        self.setupUi(self)
        self.setWindowIcon(QIcon(":img/cigala.png"))
        self.connect_signals()
        self.jid = jid
        self.users = users
        self.resource_list = {}
        self.resource_list_lock = Lock()
        self.mdns = mdns
        self.view_resources()

    ## \fn connect_signals(self)
    # \brief Connects widgets' signals with different methods.
    def connect_signals(self):
        QObject.connect(self.bClose, SIGNAL("clicked()"), self.close)

    ## \fn closeEvent(self, event)
    # \brief Calls the close event handler.
    # \param event The event that generated the close request. Not used.
    def closeEvent(self, event):
        self.hide()

    ## \fn handle_resource_found(self, name, domain, address, port, info_dict)
    # \brief Handle the Resource Found event.
    # \param name Resource Name.
    # \param domain Resource Domain.
    # \param address Resource Address.
    # \param port Resource Port.
    # \param info_dict Aditional information necessary for configure resource.
    def handle_resource_found(self, name, domain, address, port, info_dict):
        info_keys = info_dict.keys()
        if 'muc_jid' in info_keys and 'muc_name' in info_keys and 'prof_name' in info_keys and 'prof_jid' in info_keys:
            info_dict['service_name'] = name
            with self.resource_list_lock:
                self.resource_list[info_dict['muc_jid']] = info_dict
            self.update_resources(self.resource_list, self.jid, self.users)

    ## \fn handle_resource_lost(self, *args)
    # \brief Handle the Resource Lost event.
    # \param *args Array with information about resource lost.
    def handle_resource_lost(self, *args):
        resource_index = None
        for resource in self.resource_list.values():
            if resource['service_name'] == args[0]:
                resource_index = resource['muc_jid']
                continue
        if resource_index is not None:
            resource = self.resource_list[resource_index]
            with self.resource_list_lock:
                del self.resource_list[resource_index]
            self.update_resources(self.resource_list, self.jid, self.users)

    def update_resources(self, resource_list, jid, users):
       self.resourcesList.clear()
       for resource in resource_list.values():
           if (resource['prof_jid'] != jid):
               item = QListWidgetItem(resource['muc_name'])
               for user in users.values():
                   if (user['jid'].split('@')[0])[1:] == resource['prof_jid'].split('@')[0]:
                       item = QListWidgetItem(resource['muc_name'] + ' (usuario -' + user['nick'] + ')')
               item.setToolTip(resource['prof_name'])
               self.resourcesList.addItem(item)

    def view_resources(self):
        self.mdns.browse(self.handle_resource_found, self.handle_resource_lost)
