# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'resources_viewer.ui'
#
# Created: Fri Jul  9 09:09:11 2010
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_SResourceViewer(object):
    def setupUi(self, SResourceViewer):
        SResourceViewer.setObjectName("SResourceViewer")
        SResourceViewer.resize(250, 350)
        SResourceViewer.setMinimumSize(QtCore.QSize(250, 350))
        SResourceViewer.setMaximumSize(QtCore.QSize(250, 350))
        self.verticalLayout_4 = QtGui.QVBoxLayout(SResourceViewer)
        self.verticalLayout_4.setObjectName("verticalLayout_4")
        self.verticalLayout = QtGui.QVBoxLayout()
        self.verticalLayout.setObjectName("verticalLayout")
        self.label = QtGui.QLabel(SResourceViewer)
        self.label.setObjectName("label")
        self.verticalLayout.addWidget(self.label)
        self.verticalLayout_4.addLayout(self.verticalLayout)
        self.verticalLayout_2 = QtGui.QVBoxLayout()
        self.verticalLayout_2.setObjectName("verticalLayout_2")
        self.resourcesList = QtGui.QListWidget(SResourceViewer)
        self.resourcesList.setObjectName("resourcesList")
        self.verticalLayout_2.addWidget(self.resourcesList)
        self.verticalLayout_4.addLayout(self.verticalLayout_2)
        self.verticalLayout_3 = QtGui.QVBoxLayout()
        self.verticalLayout_3.setContentsMargins(145, -1, -1, -1)
        self.verticalLayout_3.setObjectName("verticalLayout_3")
        self.bClose = QtGui.QPushButton(SResourceViewer)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Minimum)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.bClose.sizePolicy().hasHeightForWidth())
        self.bClose.setSizePolicy(sizePolicy)
        self.bClose.setObjectName("bClose")
        self.verticalLayout_3.addWidget(self.bClose)
        self.verticalLayout_4.addLayout(self.verticalLayout_3)

        self.retranslateUi(SResourceViewer)
        QtCore.QMetaObject.connectSlotsByName(SResourceViewer)

    def retranslateUi(self, SResourceViewer):
        SResourceViewer.setWindowTitle(QtGui.QApplication.translate("SResourceViewer", "Grupos", None, QtGui.QApplication.UnicodeUTF8))
        self.label.setText(QtGui.QApplication.translate("SResourceViewer", "Grupos existentes:", None, QtGui.QApplication.UnicodeUTF8))
        self.resourcesList.setToolTip(QtGui.QApplication.translate("SResourceViewer", "Grupos existentes en la red (su grupo no se muestra)", None, QtGui.QApplication.UnicodeUTF8))
        self.bClose.setText(QtGui.QApplication.translate("SResourceViewer", "Cerrar", None, QtGui.QApplication.UnicodeUTF8))


if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SResourceViewer = QtGui.QWidget()
    ui = Ui_SResourceViewer()
    ui.setupUi(SResourceViewer)
    SResourceViewer.show()
    sys.exit(app.exec_())

