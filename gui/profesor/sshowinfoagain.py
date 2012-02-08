#!/usr/bin/env python
# -*- coding: utf-8 -*-
# \namespace common

from PyQt4.QtCore import *
from PyQt4.QtGui import *

##\class SShowInfoAgain
#\brief Shows a message dialog with a "never show again" checkbox.
class SShowInfoAgain(QDialog):
    def __init__(self, text, parent=None):
        QDialog.__init__(self, parent)

        layout = QVBoxLayout()

        self.texto = QLabel()
        self.texto.setOpenExternalLinks(True)
        self.texto.setText(text)

        self.again = QCheckBox(QApplication.translate("SShowInfoAgain", "No volver a mostrar esta información.", None, QApplication.UnicodeUTF8))
        self.boton = QPushButton(QApplication.translate("SShowInfoAgain", "Aceptar"))
        self.connect(self.boton, SIGNAL("clicked()"), self.accept)

        layout.addWidget(self.texto)
        layout.addWidget(self.again)
        layout.addWidget(self.boton)

        self.setLayout(layout)
        self.setWindowTitle(QApplication.translate("SShowInfoAgain", "Información", None, QApplication.UnicodeUTF8))

    ## \fn ask(self)
    # \brief Returns a boolean indicating if the user wants the dialog to be shown again.
    # \return boolean
    def ask(self):
        return not self.again.isChecked()


if __name__=="__main__":
    import sys
    app = QApplication(sys.argv)
    s = SShowInfoAgain(u"Esta es una descripción de los compartidos.<br>Para más ayuda, visite la <a href='http://cga.org.es'>web del CGA</a>")
    s.exec_()
    res = s.ask()
    if res:
        print "Se volverá a preguntar"
    else:
        print "NO se volverá a preguntar"

