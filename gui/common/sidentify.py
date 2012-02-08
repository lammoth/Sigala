#!/usr/bin/env python
# -*- coding: utf-8 -*-

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from sigala.common.user_info import get_user_name

import sigala.gui.alumno.resources_rc

class identifyWindow(QDialog):
    def __init__(self, parent=None):
        QDialog.__init__(self, parent)
        self.settings=QSettings()
        label=QLabel(u"""Por favor, introduce tu nombre y apellidos.""")
        self.tNombre=QLineEdit()
        self.tNombre.setText(get_user_name())
        self.bAceptar=QPushButton("Aceptar")

        self.connect(self.bAceptar, SIGNAL("clicked()"), self.enterUserName)

        layout=QVBoxLayout()
        layout.addWidget(label)
        layout.addWidget(self.tNombre)
        layout.addWidget(self.bAceptar)
        self.setLayout(layout)

        self.setWindowIcon(QIcon(":/img/cigala.png"))

        self.setWindowTitle(u"Identificación")

    def enterUserName(self):
        username=unicode(self.tNombre.text())
        if len(username.strip(' ')) > 0:
            self.setUserName(username)
            self.accept()

    def setUserName(self, username):
        self.settings.setValue("user/name", QVariant(username))



if __name__=="__main__":
    import sys
    app=QApplication(sys.argv)
    app.setOrganizationName("cga")
    app.setApplicationName("SIGALA")
    v=identifyWindow()
    v.show()
    app.exec_()
    
