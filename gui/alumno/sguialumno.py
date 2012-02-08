# -*- coding: utf-8 -*-
##\namespace alumno

import sys
import logging

from subprocess import Popen

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from sigala.sshareddirclient.sshareddirclient import SSharedDirClient

from sigala.gui.common.slog import SLog

from sigala.gui.alumno.ui_sguialumno import Ui_SGuiAlumno
import sigala.gui.alumno.resources_rc


##\class ResourceItem
# \brief A Custom List Widget Item. Inherited from QT List Widget Item.
class ResourceItem(QListWidgetItem):
    muc_jid = None

    ## \fn setEnabled(self, enabled=True)
    # \brief Update QListWidgetItem Flgas to enable/disable element.
    # \param enabled Boolean, indicates enable/disable state to set.
    def setEnabled(self, enabled=True):
        if enabled:
            self.setFlags(Qt.NoItemFlags | Qt.ItemIsEnabled)
        else:
            self.setFlags(Qt.NoItemFlags)

    ## \fn isEnabled(self)
    # \brief Return boolean value indicates if item is enabled or disabled.
    def isEnabled(self):
        return (self.flags() == Qt.ItemIsEnabled)


##\class SGuiAlumno
# \brief The student's GUI. Inherited from QT main window and the user UI.
class SGuiAlumno(QMainWindow, Ui_SGuiAlumno):

    ## \fn __init__(self)
    # \brief GUI constructor, sets up the GUI and other things.
    def __init__(self):
        super(SGuiAlumno, self).__init__(None)
        self.setupUi(self)
        self._create_sysTrayIcon()

        self.connect_signals()

        # Posición inicial de la ventana.
        self._center()
        self._position = self.pos()

        # Shared dir client window
        self.shared_win=None

    ## \fn set_core_handlers(self, handlers)
    # \brief Set core dict handlers.
    # \param handlers Handlers dictionary in the form EVENT:method
    # \param parent Parent of the GUI
    def set_core_handlers(self, handlers):
        self.core_handlers = handlers

    ## \fn connect_signals(self)
    # \brief Connects widgets' signals with different methods.
    def connect_signals(self):
        QObject.connect(self.connectButton, SIGNAL("clicked()"), self._connect_button_clicked)
        QObject.connect(self.trayIcon, SIGNAL("activated(QSystemTrayIcon::ActivationReason)"), self._trayIcon_action)
        QObject.connect(self.ResourceListWidget, SIGNAL("itemActivated(QListWidgetItem *)"), self._item_activated)
        QObject.connect(self.actionAcercaDe, SIGNAL("triggered()"), self.show_about)
        QObject.connect(self.actionCompartidos, SIGNAL("triggered()"), self.show_shared)
        QObject.connect(self.actionLog, SIGNAL("triggered()"), self.show_log)

        # Signals from others threads (Qt.AutoConnection / Qt.QueuedConnection):
        QObject.connect(self, SIGNAL("msgReceived"), self._message, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("connectionStablished"), self.update_gui, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("connectionLost"), self.update_gui, Qt.QueuedConnection)
        QObject.connect(self, SIGNAL("hideSharedClient"), self._hide_sharedclient, Qt.QueuedConnection)


    ## \fn _center(self)
    # \brief Center main window on screen.
    def _center(self):
        screen = QDesktopWidget().screenGeometry()
        size = self.geometry()
        self.move((screen.width()-size.width())/2, (screen.height()-size.height())/2)

    ## \fn _create_sysTrayIcon(self)
    # \brief Create the systray icon an their menu for exit aplication.
    def _create_sysTrayIcon(self):
        self.trayIcon = QSystemTrayIcon(self)
        self.trayIcon.setIcon(QIcon(":/img/cigala.png"))
        self.trayIcon.show()

        self.context_menu = QMenu()
        self.action_close = self.context_menu.addAction(QIcon(":/img/cigala.png"), QApplication.translate("SGuiAlumno", "&Salir"))
        self.connect(self.action_close, SIGNAL("triggered(bool)"), self.close)
        self.trayIcon.setContextMenu(self.context_menu)

    ## \fn _show_about(self)
    # \brief Open a dialog with information about this program.
    def show_about(self):
        msg = QString(u"""Sistema Integral de Gestión de Aulas y Localización de Alumnado
\N{COPYRIGHT SIGN} CGA 2010""")
        title="SIGALA"
        QMessageBox.about(self, title, msg)

    def show_shared(self):
        shared_info = self.core_handlers["GET_SHARED_INFO"]()
        try:
            if shared_info:
                self.shared_win=SSharedDirClient(parent=None, data=shared_info)
                self.shared_win.setAttribute(Qt.WA_DeleteOnClose)
                self.shared_win.show()
            else:
                self._message(QApplication.translate("SGuiAlumno","No hay ficheros compartidos en el grupo actual \
                                                      o no estás conectado a ningún grupo.", None, QApplication.UnicodeUTF8))
        except:
            self._message(QApplication.translate("SGuiAlumno","No hay ficheros compartidos en el grupo actual \
                                                  o no estás conectado a ningún grupo.", None, QApplication.UnicodeUTF8))

    ## \fn _show_log(self)
    # \brief Open a event log's window..
    def show_log(self):
        self.log_win=SLog(logging.getLogger('sigala.client'))
        self.log_win.show()


    ## \fn _trayIcon_action(self, reason)
    # \brief Set the application state (iconize/uniconize) from reason parameter.
    # \param reason Action identify constant.
    def _trayIcon_action(self, reason):
        if reason == QSystemTrayIcon.Trigger:
            self.core_handlers["RECONNECT"]()
            if self.isVisible():
                self.iconize()
            else:
                self.uniconize()

    ## \fn _hideEvent(self, event)
    # \brief Handle the hide event.
    # \param event Event.
    def hideEvent(self, event):
        if event.spontaneous():
            self.iconize()

    ## \fn iconize(self)
    # \brief Iconize the application.
    def iconize(self):
        self._position = self.pos()
        self.hide()

    ## \fn uniconize(self)
    # \brief Uniconize the application.
    def uniconize(self):
        if not self.isVisible():
            self.move(self._position)
            self.show()

    ## \fn update_gui(self)
    # \brief Update the gui apperance from variables resource_list and resource_name.
    # \param resource_list Contains the resource list to show en ListWidget.
    # \param resource_name Contaions the resource name wich we connected, in case we connected.
    def update_gui(self, resource_list, resource_name=None):
        self.ResourceListWidget.clear()
        self.trayIcon.setIcon(QIcon(":/img/cigala.png"))
        self._check_button(False)

        for resource in resource_list.values():
            item = ResourceItem(resource['muc_name'])
            item.setToolTip(resource['prof_name'])
            item.muc_jid = resource['muc_jid']
            item.setIcon(QIcon(":/img/led_gray.png"))

            if resource_name is not None:
                # This means has connected
                self._check_button(True)
                item.setEnabled(item.muc_jid==resource_name)

                item.setIcon(QIcon(":/img/led_green.png"))
                self.trayIcon.setIcon(QIcon(":/img/cigala_connected.png"))

            self.ResourceListWidget.addItem(item)

    ## \fn _connect_button_clicked(self)
    # \brief Handle the clicked event for the connection button.
    def _connect_button_clicked(self):
        checked = self.connectButton.isChecked()
        if checked and self.join_resource():
            self._check_button(True)
        else:
            self._check_button(False)
            self.exit_resource()
            try:
                self.shared_win.done(0)
            except:
                pass
            finally:
                self.shared_win=None

    ## \fn _check_button_clicked(self)
    # \brief Check the connection button state and change their appearance in consecuence.
    # \param check Indicates if a button is checked or not.
    def _check_button(self, check):
        if check:
            self.connectButton.setText(QApplication.translate("SGuiAlumno", "Desconectar"))
            self.connectButton.setChecked(True)
        else:
            self.connectButton.setText(QApplication.translate("SGuiAlumno", "Conectar"))
            self.connectButton.setChecked(False)

    ## \fn _item_activated(self, item)
    # \brief Handle event for a list item activated (enter, double click, etc.)
    # \param item Item wich have been activated.
    def _item_activated(self, item):
        self.join_resource()

    ## \fn join_resource(self)
    # \brief Handle event for connect to a group wich is selected in ListWidget.
    def join_resource(self):
        selected_item = self.ResourceListWidget.currentItem()
        if selected_item is not None:
            row = self.ResourceListWidget.row(selected_item)
            item = self.ResourceListWidget.item(row)

            if not item.isEnabled():
                self.core_handlers["REQUEST_JOIN_MUC"](item.muc_jid)

            return True
        else:
            self._check_button(False)
            self._message(QApplication.translate("SGuiAlumno",'Debes seleccionar un grupo para conectar.'))
            return False

    ## \fn _message(self, message=None, title=None)
    # \brief Show a "Info" message with a custom title and text.
    # \param message Message to show.
    # \param title Window title ("Information" by default).
    def _message(self, message=None, title=None):
        if title is None:
            title = QApplication.translate("SGuiAlumno", "Información", None, QApplication.UnicodeUTF8)
        message = QApplication.translate("SGuiAlumno", message, None, QApplication.UnicodeUTF8)
        QMessageBox.information(self,   title, message, QMessageBox.Ok)

    ## \fn _error(self, message=None, title=None)
    # \brief Show a "Error" message with a custom title and text.
    # \param message Message to show.
    # \param title Window title ("Error" by default).
    def _error(self, message=None, title=None):
        if title is None:
            title = QApplication.translate("SGuiAlumno", "Error")
        QMessageBox.critical(self,  title, message, QMessageBox.Ok)

    ## \fn exit_resource(self)
    # \brief Handle event for disconnect.
    def exit_resource(self):
        self.core_handlers["REQUEST_EXIT_MUC"]()

    ## \fn closeEvent(self, event)
    # \brief Handle window close event.
    # \param event Event.
    def closeEvent(self, event):
        if event.spontaneous():
            event.ignore()
            self.iconize()
        else:
            self.core_handlers["EXIT_APPLICATION"]()

    def _hide_sharedclient(self, *args):
        try:
            self.shared_win.close()
        except Exception, e :
            print "Error al cerrar:", e

if __name__=="__main__":
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)
    s = SGuiAlumno()
    sys.exit(app.exec_())
