# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'sigala.ui'
#
# Created: Fri Jul  9 09:09:36 2010
#      by: PyQt4 UI code generator 4.4.4
#
# WARNING! All changes made in this file will be lost!

from PyQt4 import QtCore, QtGui

class Ui_SGuiAlumno(object):
    def setupUi(self, SGuiAlumno):
        SGuiAlumno.setObjectName("SGuiAlumno")
        SGuiAlumno.resize(197, 301)
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap(":/img/cigala.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        SGuiAlumno.setWindowIcon(icon)
        self.centralwidget = QtGui.QWidget(SGuiAlumno)
        sizePolicy = QtGui.QSizePolicy(QtGui.QSizePolicy.Maximum, QtGui.QSizePolicy.Preferred)
        sizePolicy.setHorizontalStretch(0)
        sizePolicy.setVerticalStretch(0)
        sizePolicy.setHeightForWidth(self.centralwidget.sizePolicy().hasHeightForWidth())
        self.centralwidget.setSizePolicy(sizePolicy)
        self.centralwidget.setAcceptDrops(False)
        self.centralwidget.setObjectName("centralwidget")
        self.gridLayout_2 = QtGui.QGridLayout(self.centralwidget)
        self.gridLayout_2.setMargin(0)
        self.gridLayout_2.setVerticalSpacing(0)
        self.gridLayout_2.setObjectName("gridLayout_2")
        self.gridLayout = QtGui.QGridLayout()
        self.gridLayout.setHorizontalSpacing(0)
        self.gridLayout.setObjectName("gridLayout")
        self.ResourceListWidget = QtGui.QListWidget(self.centralwidget)
        self.ResourceListWidget.setProperty("cursor", QtCore.QVariant(QtCore.Qt.ArrowCursor))
        self.ResourceListWidget.setAlternatingRowColors(True)
        self.ResourceListWidget.setSpacing(3)
        self.ResourceListWidget.setObjectName("ResourceListWidget")
        self.gridLayout.addWidget(self.ResourceListWidget, 0, 0, 1, 1)
        self.connectButton = QtGui.QPushButton(self.centralwidget)
        self.connectButton.setEnabled(True)
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap(":/img/connect.svg"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        icon1.addPixmap(QtGui.QPixmap(":/img/disconnect.svg"), QtGui.QIcon.Normal, QtGui.QIcon.On)
        self.connectButton.setIcon(icon1)
        self.connectButton.setCheckable(True)
        self.connectButton.setObjectName("connectButton")
        self.gridLayout.addWidget(self.connectButton, 1, 0, 1, 1)
        self.gridLayout_2.addLayout(self.gridLayout, 0, 0, 1, 1)
        SGuiAlumno.setCentralWidget(self.centralwidget)
        self.menubar = QtGui.QMenuBar(SGuiAlumno)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 197, 23))
        self.menubar.setObjectName("menubar")
        self.menuHerramientas = QtGui.QMenu(self.menubar)
        self.menuHerramientas.setObjectName("menuHerramientas")
        self.menuAyuda = QtGui.QMenu(self.menubar)
        self.menuAyuda.setObjectName("menuAyuda")
        SGuiAlumno.setMenuBar(self.menubar)
        self.actionCompartidos = QtGui.QAction(SGuiAlumno)
        self.actionCompartidos.setObjectName("actionCompartidos")
        self.actionAcercaDe = QtGui.QAction(SGuiAlumno)
        self.actionAcercaDe.setIcon(icon)
        self.actionAcercaDe.setObjectName("actionAcercaDe")
        self.actionLog = QtGui.QAction(SGuiAlumno)
        self.actionLog.setObjectName("actionLog")
        self.menuHerramientas.addAction(self.actionCompartidos)
        self.menuHerramientas.addSeparator()
        self.menuHerramientas.addAction(self.actionLog)
        self.menuAyuda.addSeparator()
        self.menuAyuda.addAction(self.actionAcercaDe)
        self.menubar.addAction(self.menuHerramientas.menuAction())
        self.menubar.addAction(self.menuAyuda.menuAction())

        self.retranslateUi(SGuiAlumno)
        QtCore.QMetaObject.connectSlotsByName(SGuiAlumno)

    def retranslateUi(self, SGuiAlumno):
        SGuiAlumno.setWindowTitle(QtGui.QApplication.translate("SGuiAlumno", "SIGALA cliente", None, QtGui.QApplication.UnicodeUTF8))
        self.ResourceListWidget.setToolTip(QtGui.QApplication.translate("SGuiAlumno", "Selecciona un grupo para conectar.", None, QtGui.QApplication.UnicodeUTF8))
        self.ResourceListWidget.setSortingEnabled(True)
        self.connectButton.setText(QtGui.QApplication.translate("SGuiAlumno", "Conectar", None, QtGui.QApplication.UnicodeUTF8))
        self.menuHerramientas.setTitle(QtGui.QApplication.translate("SGuiAlumno", "Herramientas", None, QtGui.QApplication.UnicodeUTF8))
        self.menuAyuda.setTitle(QtGui.QApplication.translate("SGuiAlumno", "Ayuda", None, QtGui.QApplication.UnicodeUTF8))
        self.actionCompartidos.setText(QtGui.QApplication.translate("SGuiAlumno", "Ficheros compartidos", None, QtGui.QApplication.UnicodeUTF8))
        self.actionAcercaDe.setText(QtGui.QApplication.translate("SGuiAlumno", "Acerca de...", None, QtGui.QApplication.UnicodeUTF8))
        self.actionLog.setText(QtGui.QApplication.translate("SGuiAlumno", "Visor de eventos", None, QtGui.QApplication.UnicodeUTF8))

import resources_rc

if __name__ == "__main__":
    import sys
    app = QtGui.QApplication(sys.argv)
    SGuiAlumno = QtGui.QMainWindow()
    ui = Ui_SGuiAlumno()
    ui.setupUi(SGuiAlumno)
    SGuiAlumno.show()
    sys.exit(app.exec_())

