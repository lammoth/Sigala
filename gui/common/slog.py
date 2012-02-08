#!/usr/bin/env python
# -*- coding: utf-8 -*-
##\namespace alumno

import sys
import logging
import logging.config

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from sigala.gui.common.ui_slog import Ui_SLog

##\class SLog
# \brief The window for show logs.
class SLog(QWidget, Ui_SLog):

    ## \fn __init__(self)
    # \brief Initialization interface for view logs.
    def __init__(self, logger):
        super(SLog, self).__init__(None)
        self.i10n()
        self.setupUi(self)

        self.connect_signals()

        self.logger = logger
        self.show_log()

    ## \fn i10n(self)
    # \brief Translates the GUI
    def i10n(self):
        locale = QLocale.system().name()
        self.qapp = QCoreApplication.instance()
        self.qtTranslator = QTranslator()
        if self.qtTranslator.load("sgui_common_" + locale, ":/tr"):
            logging.info("Cargando traducciones para: (%s)" % locale)
            self.qapp.installTranslator(self.qtTranslator)

    ## \fn connect_signals(self)
    # \brief Connects widgets' signals with different methods.
    def connect_signals(self):
        QObject.connect(self.closeButton, SIGNAL("clicked()"), self.close)

    ## \fn __init__(self)
    # \brief Show de log buffer in the window's text area.
    def show_log(self):
        # Must exist a "MemoryHandler" buffer with previous logs.
        find_hand=False
        for hand in self.logger.handlers:
            if isinstance(hand, logging.handlers.MemoryHandler):
                chand = hand
                find_hand=True
                continue

        #If it has been found, show logs ..
        formatter = logging.Formatter('<b>%(asctime)s</b> - %(levelname)s: %(message)s', '%H:%M:%S')
        if find_hand:
            # For rich formatting, here can be seen the log_entry attributes (levelname, lineno, etc...),
            # and create custom "html formatter" for them
            for log_entry in chand.buffer:
                msg = formatter.format(log_entry)
                if isinstance(msg, str):
                    msg=msg.decode('utf8', 'replace')
                self.textEdit.append(msg)

        #And then, (with or without previous logs) make a custom handler for update new logs..
        self.qtHand = QTextHandler(elem_for_append_to=self.textEdit)
        self.qtHand.setFormatter(formatter)

        self.logger.addHandler(self.qtHand)

    ## \fn closeEvent(self, event)
    # \brief Handle window close event.
    # \param event Event.
    def closeEvent(self, event):
        self.logger.removeHandler(self.qtHand)


##\class QTextHandler
# \brief A log handler for keep update the log's window.
class QTextHandler(logging.Handler):

    ## \fn __init__(self, elem_for_append_to)
    # \brief Initialization.
    # \param elem_for_append_to QT textEdit object for append new logs.
    def __init__(self, elem_for_append_to):
        logging.Handler.__init__(self)
        self.out_element = elem_for_append_to

    ## \fn handle(self, record)
    # \brief Redeclare the logging.Handler's handle method.
    # \param record New log record to show.
    def handle(self, record):
        l_msg = self.formatter.format(record)
        if isinstance(l_msg, str):
            l_msg = l_msg.decode('utf8', 'replace')
        self.out_element.append(l_msg)
        self.out_element.moveCursor(QTextCursor.End)
