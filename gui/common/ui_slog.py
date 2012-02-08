# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'slog.ui'
#
# Created: Fri Jul  9 10:35:50 2010
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_SLog(object):
    def setupUi(self, SLog):
        SLog.setObjectName("SLog")
        SLog.resize(631, 274)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/img/cigala.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SLog.setWindowIcon(icon)
        self.verticalLayout = QtGui.QVBoxLayout(SLog)
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(SLog)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.textEdit = QtGui.QTextEdit(SLog)
        self.textEdit.setReadOnly(True)
        self.textEdit.setObjectName("textEdit")
        self.verticalLayout.addWidget(self.textEdit)
        self.horizontalLayout = QtGui.QHBoxLayout()
        self.horizontalLayout.setObjectName("horizontalLayout")
        spacerItem = QtGui.QSpacerItem(40, 20, QtGui.QSizePolicy.Expanding, QtGui.QSizePolicy.Minimum)
        self.horizontalLayout.addItem(spacerItem)
        self.closeButton = QtGui.QPushButton(SLog)
        self.closeButton.setObjectName("closeButton")
        self.horizontalLayout.addWidget(self.closeButton)
        self.verticalLayout.addLayout(self.horizontalLayout)

        self.retranslateUi(SLog)
        QtCore.QMetaObject.connectSlotsByName(SLog)

    def retranslateUi(self, SLog):
        SLog.setWindowTitle(QtGui.QApplication.translate("SLog", "Visor de eventos", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SLog", "Eventos:", None, QtGui.QApplication.UnicodeUTF8))
        self.closeButton.setText(QtGui.QApplication.translate("SLog", "Cerrar", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SLog = QtGui.QWidget()
    ui = Ui_SLog()
    ui.setupUi(SLog)
    SLog.show()
    sys.exit(app.exec_())

