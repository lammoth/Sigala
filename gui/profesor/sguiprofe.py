# -*- coding: utf-8 -*-

##\namespace profesor

import sys
import os
import logging
import logging.config

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from sigala.gui.profesor.sshowinfoagain import SShowInfoAgain

from sigala.common.user_info import get_user_name
from sigala.common.user_info import identify_user

from sigala.common.settings import LOGGING_CONFIG_FILE

from sigala.common.exception import SInvalidGroupName

from sigala.gui.common.slog import SLog

from sigala.gui.profesor.ui_sguiprofe import Ui_SGuiProfe
from sigala.gui.profesor.sapplauncher import SAppLauncher
import sigala.gui.profesor.sigala_resources

from sigala.profesor.settings import DESKTOP_APP_DIR
from sigala.profesor.settings import SHARED_INFO_TEXT
from sigala.profesor.settings import SHARED_DIR
from sigala.profesor.settings import SHARED_PRIVATE_DIR
from sigala.profesor.settings import SIGALA_HTML_HELP_FILE

logging.config.fileConfig(LOGGING_CONFIG_FILE)
linfo = logging.info
lerror = logging.error
ldebug = logging.debug

##\class SGuiProfe
# \brief The teacher's GUI. Inherited from QT main window and the user UI.
class SGuiProfe(QMainWindow, Ui_SGuiProfe):

    ## \fn __init__(self, handlers, parent)
    # \brief GUI constructor, sets up the GUI and other things.
    # \param handlers Handlers dictionary in the form EVENT:method
    # \param parent Parent of the GUI
    def __init__(self, handlers, parent=None):
        super(SGuiProfe, self).__init__(parent)
        self.settings = QSettings()
        self.setupUi(self)
        self.handlers = handlers
        # Setup the various widgets signals
        self._setupSignals()
        # Populates the Tools menu
        self._loadApps()
        # Sets up the shared dir application's menu entry.
        self._setup_shared_app()

    ## \fn _setupSignals(self)
    # \brief Connects widgets' signals with different methods.
    def _setupSignals(self):
        self.connect(self.bGrupoAction, SIGNAL("clicked()"), self.manage_resource)
        self.connect(self.bAbrirCerrarGrupo, SIGNAL("toggled(bool)"),
                    self.manage_open_close)
        self.connect(self.bKick, SIGNAL("clicked()"), self.kick_user)
        self.connect(self.bBan, SIGNAL("clicked()"), self.ban_user)
        self.connect(self.bIdent, SIGNAL("clicked()"), self.ident_user)
        self.connect(self.bUnBan, SIGNAL("clicked()"), self.unban_user)
        self.connect(self.actionLog, SIGNAL("triggered()"), self.show_log)
        self.connect(self.actionAcercaDe, SIGNAL("triggered()"), self.show_about)
        self.connect(self.bViewResources, SIGNAL("clicked()"), self.show_resources)
        self.connect(self.actionAyuda, SIGNAL("triggered()"), self.showHelp)

    ## \fn showHelp(self)
    # \brief Launches the system application to show help
    def showHelp(self):
        QDesktopServices.openUrl(QUrl(SIGALA_HTML_HELP_FILE))

    ## \fn _loadApps(self)
    # \brief Populates the Tools menu with the .desktop files found
    # in the DESKTOP_APP_DIR directory.
    def _loadApps(self):
        linfo("Loading apps\n%s\n" % ('-'*80))
        if not os.path.isdir(DESKTOP_APP_DIR):
            return
        desktop_files = [os.path.join(DESKTOP_APP_DIR, f)
                            for f in os.listdir(DESKTOP_APP_DIR)
                            if f.endswith(".desktop") ]
        for f in desktop_files:
            ldebug("Loading .desktop file: '%s'" % f)
            self._addAppMenuItem(f)

        # Disable the Tools menu entry until a user joins the resource.
        self.menuAplicaciones.setEnabled(False)

    ## \fn _addAppMenuItem(self, f)
    # \brief Adds a new .desktop entry to the tools menu.
    # \param f .desktop file to be added.
    def _addAppMenuItem(self, f):
        try:
            app = SAppLauncher(f, self.menuAplicaciones)
        except DesktopFileNotFound, m:
            lerror("No such .desktop file: '%s'" % m)
        else:
            self.menuAplicaciones.addAction(app)
            self.connect(app,
                        SIGNAL("triggered()"),
                        lambda: self._launchApp(app.ExecCommand()))

    ## \fn _launchApp
    # \brief Asks the core to run a command.
    # \param cmd Command to be ran.
    def _launchApp(self, cmd):
        self.handlers["LAUNCH_APP_CB"](cmd)

    ## \fn closeEvent(self, event)
    # \brief Calls the close event handler.
    # \param event The event that generated the close request. Not used.
    def closeEvent(self, event):
        if not self.handlers["CLOSE_EVENT_CB"]():
            event.ignore()
        else:
            qapp = QCoreApplication.instance()
            qapp.quit()

    ## \fn update_gui(self, users)
    # \brief Updates the GUI (users list, banned list)
    # \param users List of users to update the GUI with.
    def update_gui(self, users):
        # users is a dict with at least the following keys: nick, jid, banned
        banned_users = dict( [(u, users[u]) for u in users if users[u]["banned"] ])
        good_users = dict( [(u, users[u]) for u in users if not users[u]["banned"] ])
        self._update_banned_list(banned_users)
        self._update_good_list(good_users)

        # Enable the applications menu if we have at least one valid user
        enabled = bool(len(good_users))
        self.menuAplicaciones.setEnabled(enabled)

    ## \fn _update_banned_list(self, users)
    # \brief Updates the banned users list.
    # \param users Users to populate the banned list with.
    def _update_banned_list(self, users):
        self._update_list(self.banList, users)

    ## \fn _update_good_list(self, users)
    # \brief Updates the "normal" users list.
    # \param users Users to populate the users list with.
    def _update_good_list(self, users):
        self._update_list( self.userList, users)

    ## \fn _update_list(self, listWidget, users)
    # \brief Updates a list widget with the users.
    # \param listWidget QListWidget to update.
    # \param users List of users to update the list with.
    def _update_list(self, listWidget, users):
        nicks = users.keys()
        listWidget.clear()
        listWidget.addItems(nicks)

    ## \fn manage_resource(self)
    # \brief Manages the create/destroy resource button
    def manage_resource(self):
        id_intr = 0
        
        if len(get_user_name()) == 0:
            identify_user()
        else:
            id_intr = 1
            
        if id_intr == 1:    
            status = self.bGrupoAction.isChecked()
            if status == True:
                # Se ha pulsado el botón -> Se pasa al estado de creación de recurso
                res = unicode(self.tGrupo.text())
                if len(res) == 0 or len(res) > 32:
                    self._message(QApplication.translate("SGuiProfe", "Debe escribir un nombre para el grupo (Max. 32 caracteres)."))
                    self.bGrupoAction.setChecked(not status)
                    return
                try:
                    self.handlers["CREATE_RESOURCE_CB"](res)
                except SInvalidGroupName, name:
                    self._message(QString(u"Nombre de grupo inválido: \"<b>%1</b>\"<br>Compruebe que el nombre contiene al menos un caracter alfanumérico.").arg(unicode(name)))
                    # Toggle status so that the UI doesn't change
                    self.bGrupoAction.setChecked(not status)
                    self.tGrupo.setText("")
                    return
                self.bGrupoAction.setText(QApplication.translate("SGuiProfe", "Eliminar grupo"))
                self.lGrupo.setText(res)
            else:
                ldebug("GUI :: Delete resource\n%s\n" % ('-'*80))
                self.handlers["DESTROY_RESOURCE_CB"]()
                ldebug("Interface reset\n%s\n" % ('-'*80))
                self._reset_gui()
    
            # Stablishes various widget states depending on the action.
            self.tGrupo.setEnabled(not status)
            self.tabWidget.setEnabled(status)
            self.bAbrirCerrarGrupo.setEnabled(status)

    ## \fn _reset_gui(self)
    # \brief Resets the GUI to the original state.
    def _reset_gui(self):
        self.tGrupo.setText("")
        self.bGrupoAction.setText(QApplication.translate("SGuiProfe", "Crear grupo"))
        self.lGrupo.setText("")
        self.bAbrirCerrarGrupo.setText(QApplication.translate("SGuiProfe", "Cerrar grupo"))
        self.bAbrirCerrarGrupo.setChecked(False)
        # Desactiva las comparticiones
        self._shared_app(False)
        self.shared_accion.setChecked(False)

    ## \fn manage_open_close(self, status)
    # \brief Opens or closes the MUC
    # \param status The status of the button.
    def manage_open_close(self, status):
        if status == True:
            # We want to close the MUC.
            self.handlers["CLOSE_MUC_CB"]()
            self.bAbrirCerrarGrupo.setText(QApplication.translate("SGuiProfe", "Abrir grupo"))
        else:
            # We want to open the MUC.
            self.handlers["OPEN_MUC_CB"]()
            self.bAbrirCerrarGrupo.setText(QApplication.translate("SGuiProfe", "Cerrar grupo"))

    ## \fn kick_user(self)
    # \brief Requests the core to kick the selected users.
    def kick_user(self):
        # Collect the users selected on the list.
        users = [unicode(i.text()) for i in self.userList.selectedItems()]
        map( self.handlers["KICK_USER_CB"], users)

    ## \fn ban_user(self)
    # \brief Request the core to ban the selected users.
    def ban_user(self):
        # Collect the users selected on the list.
        users = [unicode(i.text()) for i in self.userList.selectedItems()]
        map( self.handlers["BAN_USER_CB"], users)

    ## \fn unban_user(self)
    # \brief Request the core to unban the selected users.
    def unban_user(self):
        # Collect the users selected on the list.
        users = [unicode(i.text()) for i in self.banList.selectedItems()]
        map( self.handlers["UNBAN_USER_CB"], users)

    ## \fn ident_user(self)
    # \brief Request the core to identify the user(s).
    def ident_user(self):
        users = [unicode(i.text()) for i in self.userList.selectedItems()]
        map( self.handlers["IDENTIFY_USER_CB"], users)

    ## \fn _message(self, msg)
    # \brief Shows a message dialog.
    # \param msg Message to show.
    def _message(self, msg):
        QMessageBox.information(self, QApplication.translate("SGuiProfe", u"Información"), msg)

    ## \fn show_about(self)
    # \brief Shows the application's about dialog.
    def show_about(self):
        msg = QString(u"""Sistema Integral de Gestión de Aulas y Localización de Alumnado
\N{COPYRIGHT SIGN} CGA 2010""")
        title="SIGALA"
        QMessageBox.about(self, title, msg)


    ## \fn _setup_shared_app(self)
    # \brief Sets up the shared directory app's menu entry.
    def _setup_shared_app(self):
        separador = QAction(self)
        separador.setSeparator(True)
        self.shared_accion = QAction(QApplication.translate("SGuiProfe", "Compartir", None, QApplication.UnicodeUTF8), self)
        self.shared_accion.setCheckable(True)
        self.connect(self.shared_accion, SIGNAL("triggered()"),
                lambda: self._shared_app(self.shared_accion.isChecked()))
        self.menuAplicaciones.addAction(separador)
        self.menuAplicaciones.addAction(self.shared_accion)

    ## \fn _shared_app(self, estado)
    # \brief Requests the core to start or stop the shared dir app.
    # \param state Whether to start the shared dir app or not.
    def _shared_app(self, estado):
        self.handlers["SHARED_CB"](estado)
        if estado:
            # Shows some information about the shared dir application.
            self.show_shared_info()

    ## \fn show_shared_info(self)
    # \brief Shows an information dialog about the sharing application.
    # The user can choose to not display the dialog again.
    def show_shared_info(self):
        PRIVATE_DIR=os.path.join(SHARED_DIR, SHARED_PRIVATE_DIR)
        info = QApplication.tr(self, unicode(SHARED_INFO_TEXT)).arg(SHARED_DIR).arg(PRIVATE_DIR)
        show_shared_help = self.settings.value("shared/show_help", QVariant(True)).toBool()
        # Does the user want to see the dialog?
        if show_shared_help:
            ret = SShowInfoAgain(info)
            ret.exec_()
            if not ret.ask():
                ldebug("No se mostrará más")
                show_shared_help=False
            linfo("Estableciendo la configuracion a %s" % show_shared_help)
            self.settings.setValue("shared/show_help", QVariant(show_shared_help))

    def show_log(self):
        self.log_win=SLog(logging.getLogger('sigala.server'))
        self.log_win.show()

    def show_resources(self):
        self.handlers["VIEW_RESOURCES"]()


if __name__=="__main__":
    s = SGuiProfe()
    app=QApplication(sys.argv)
    s.show()
    app.exec_()
