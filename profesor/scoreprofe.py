#!/usr/bin/env python
# -*- coding: utf-8 -*-

## \namespace profesor

import sys
import logging
import logging.config

from subprocess import Popen
from subprocess import call as subcall

import dbus
from dbus.mainloop.qt import DBusQtMainLoop

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from sigala.profesor.sdbus import SDbus
from sigala.profesor.sprofe import SProfe
from sigala.profesor.sxmppserver import SXmppServer
from sigala.profesor.sshareddir import SSharedDir

from sigala.common.smdns import SMdns

from sigala.common.user_info import get_user_name
from sigala.common.user_info import generate_jid
from sigala.common.user_info import get_hostname
from sigala.common.user_info import identify_user

from sigala.common.settings import VALID_CHARS
from sigala.common.settings import LOGGING_CONFIG_FILE
from sigala.common.settings import SIGALA_PID_FILE

from sigala.common.exception import SInvalidGroupName
from sigala.common.exception import NoDefaultDevice

from sigala.gui.profesor.sguiprofe import SGuiProfe
from sigala.gui.profesor.sresourcesviewer import SResourceViewer

logging.config.fileConfig(LOGGING_CONFIG_FILE)
linfo = logging.info
lerror = logging.error
ldebug = logging.debug

## \class SCoreProfe
# \brief SIGALA teacher's core.
class SCoreProfe:
    def __init__(self):
        # Diccionario con los datos de los usuarios. clave=JID
        self.users = dict()

        # Diccionario con los manejadores de las peticiones del GUI
        self.gui_handlers = {
                            "CREATE_RESOURCE_CB": self.request_create_resource,
                            "DESTROY_RESOURCE_CB": self.request_destroy_resource,
                            "KICK_USER_CB": self.request_kick_user,
                            "BAN_USER_CB": self.request_ban_user,
                            "UNBAN_USER_CB": self.request_unban_user,
                            "IDENTIFY_USER_CB": self.request_identify_user,
                            "OPEN_MUC_CB": self.request_open_muc,
                            "CLOSE_MUC_CB": self.request_close_muc,
                            "CLOSE_EVENT_CB": self.closeEvent,
                            "LAUNCH_APP_CB": self.launchApp,
                            "SHARED_CB": self.shared_dir,
                            "VIEW_RESOURCES": self.view_resources,
            }

        # Manejadores que se le pasan al bot.
        self.bot_handlers = {
                            "NEW_USER_CB": self.request_add_user,
                            "DEL_USER_CB": self.request_del_user,
        }

        # Subservices setup.
        self.gui = None
        self.resources_win = None
        self._setup_gui()

        self.log = None
        self._setup_logging()
        self.log.info(QApplication.translate("SCoreProfe.log", "Iniciando servidor."))

        try:
            self.jid = generate_jid()
            self.hostname = get_hostname()
        except NoDefaultDevice, e:
            self.gui._message(QApplication.translate("SCoreProfe.log", u"Es necesaria una conexión de red para usar SIGALA."))
            sys.exit(1)

        if len(get_user_name()) == 0:
            ldebug("El username: '%s'" % get_user_name())
            identify_user()

        self.nick = get_user_name()

        self.sdbus = None
        self._setup_dbus()

        self.mdns = None
        self._setup_mdns()

        self.resources_win=SResourceViewer(self.mdns, self.jid, self.users)

        self.shared=None

        self.xmpp_server = SXmppServer()
        self.xmpp_server.start()

        # No instanciamos el botaún, necesitamos los parámetros de conexión.
        self.bot = None
        self.muc_name = ""

    ## \fn _setup_logging(self)
    # \brief Sets up the logging class attribute.
    def _setup_logging(self):
        logging.config.fileConfig(LOGGING_CONFIG_FILE)
        self.log = logging.getLogger('sigala.server')

    ## \fn _term_client(self)
    # \brief Signals the SIGALA client to terminate.
    def _term_client(self):
        # No se usa de momento. Ya se verá
        if not os.path.isfile(SIGALA_PID_FILE):
            return
        else:
            # Para cuando se use:
            self.log.info(QApplication.translate("SCoreProfe.log", "Cerrando instancia del cliente."))
            with open(SIGALA_PID_FILE, "r") as f:
                client_pid = int(f.readline())
                ldebug("Client PID: '%s'" % client_pid)
                linfo("Asking client to shut down...")
                try:
                    os.kill(client_pid, signal.SIGTERM)
                except OSError, m:
                    lerror("PID file exists, but an error occurred: '%s'" % m)

    ## \fn shared_dir(self, start)
    # \brief Starts or stops the shared dir feature.
    # \param start Whether or not to start the shared dir server.
    def shared_dir(self, start=False):
        if start:
            self.log.info(QApplication.translate("SCoreProfe.log", "Iniciando el compartido."))
            self.shared.start()
        else:
            self.log.info(QApplication.translate("SCoreProfe.log", "Deteniendo el compartido."))
            if self.shared:
                self.shared.stop()

    ## \fn _setup_dbus(self)
    # \brief Sets up dbus modules.
    # \param
    def _setup_dbus(self):
        # Se pasa el bus de sesión al cargador de módulos de DBUS
        DBusQtMainLoop(set_as_default=True)
        self.bus = dbus.SessionBus()
        self.sdbus = SDbus(self.bus, self)

    ## \fn _setup_mdns(sef)
    # \brief Sets up the resource publisher.
    def _setup_mdns(self):
        # Se instancia el publicador de recursos.
        self.mdns = SMdns()

    ## \fn _setup_gui(self)
    # \brief Sets up the GUI
    def _setup_gui(self):
        # Instancia de la interfaz de usuario
        self.qtapp = QApplication(sys.argv)
        self.qtapp.setOrganizationName("cga")
        self.qtapp.setApplicationName("SIGALA")
        # Internacionalización
        self.i10n()
        # Se pasa como parámetro el diccionario con las llamadas para cada
        # tipo de evento.
        self.gui = SGuiProfe(handlers = self.gui_handlers)

    ## \fn i10n(self)
    # \brief Translates the GUI
    def i10n(self):
        locale = QLocale.system().name()
        self.qtTranslator = QTranslator()
        if self.qtTranslator.load("sgui_profesor_" + locale, ":/tr"):
            linfo("Cargando traducciones para: (%s)" % locale)
            self.qtapp.installTranslator(self.qtTranslator)

    ## \fn run(self)
    # \brief Starts the main program
    def run(self):
        self.gui.show()
        self.qtapp.exec_()

    def sanitize_muc_name(self, name):
        # Restricts the MUC name to ASCII only characters.
        return str(filter(lambda k: k in VALID_CHARS, name)).lower()

    ## \fn request_create_resource(self, muc_name)
    # \brief Called then the user click on the Create resource button.
    # \param muc_name Name of the resource to be created.
    def request_create_resource(self, muc_name):
        self.log.info(QApplication.translate("SCoreProfe.log", "Creando el grupo: %1", 
                                                None, QApplication.UnicodeUTF8).arg(muc_name))
        muc_sane_name = self.sanitize_muc_name(muc_name)
        if len(muc_sane_name) == 0:
            self.log.error(QApplication.translate("ScoreProfe.log", "Nombre de grupo inválido: %1", 
                                                    None, QApplication.UnicodeUTF8).arg(muc_name))
            raise SInvalidGroupName(muc_name)

        # Starts the sharing system.
        self.shared=SSharedDir(muc_name)
        self.muc_name = muc_name
        ldebug("Create resource '%s'\n%s\n" % (self.muc_name, '-'*80))
        self.muc_jid = self.generate_muc_jid(muc_sane_name)
        self.nick = get_user_name()
        self.bot = SProfe( jid=self.jid,
                            muc_jid=self.muc_jid,
                            nick=self.nick,
                            parent=self,
                        )
        self.bot.set_core_handlers(self.bot_handlers)
        self.bot.connect(("127.0.0.1", 5222))
        self.bot.process(threaded=True)

        datos = {   'muc_jid': self.muc_jid,
                    'muc_name': self.muc_name,
                    'prof_name': self.nick,
                    'prof_jid': self.bot.fulljid,
                }
        name = u"%s - %s" % (self.muc_name, self.nick)
        # Publishes the resource with mDNS.
        self.mdns.publish(name, datos)
        self.log.info(QApplication.translate("SCoreProfe.log", "Grupo creado: %1 - %2 (%3)", 
                                                None, QApplication.UnicodeUTF8).arg(
                                                            self.muc_name).arg(
                                                            self.nick).arg(
                                                            self.muc_jid)
                      )

    ## \fn generate_muc_jid(self)
    # \brief Generates a new MUC jid based on the resource name.
    def generate_muc_jid(self, name):
        # Genera el jid del MUC en función del nombre del recurso.
        return "%s@conference.%s" % (name, self.hostname)

    ## \fn request_destroy_resource(self)
    # \brief Called when the user requests the destruction of the resource.
    def request_destroy_resource(self):
        self.log.info(QApplication.translate("SCoreProfe.log", "Eliminando grupo: %1", 
                                            None, QApplication.UnicodeUTF8).arg(self.muc_name))
        ldebug("Destroying resource\n%s\n" % ('-'*80))
        if self.resources_win:
            self.resources_win.hide()
        if self.shared:
            self.shared.stop()
            self.shared=None
        if self.bot:
            self.mdns.unpublish()
            self.bot.destroy_muc()
            self.bot.disconnect()
        self.bot = None
        self.users = dict()
        self._update_gui()
        self.log.info(QApplication.translate("SCoreProfe.log", "Grupo eliminado."))

    ## \fnrequest_kick_user(self, nick)
    # \brief Called when the user wants to kick a users frmo the MUC.
    # \param nick Nick of the user to be kicked.
    def request_kick_user(self, nick):
        self.log.info(QApplication.translate("SCoreProfe.log", "Expulsando usuario: %1", 
                                                None, QApplication.UnicodeUTF8).arg(nick))
        ldebug("Expulsando usuario\n%s\n" % ('-'*80))
        # Not a user anymore.
        del self.users[unicode(nick)]
        self.bot.kick_user(nick)
        self._update_gui()

    ## \fn request_ban_user(self, nick)
    # \brief Called when the user wants to ban a user from the MUC.
    # \param nick Nick of the user to be banned.
    def request_ban_user(self, nick):
        self.log.info(QApplication.translate("SCoreProfe.log", "Prohibiendo acceso al usuario: %1", 
                                                None, QApplication.UnicodeUTF8).arg(nick))
        ldebug("Baneando usuario\n%s\n" % ('-'*80))
        # We need the full JID in order to ban a user, search it.
        jid = self.users[nick].get("jid", None)
        self.bot.ban_user(jid)
        # Mark the user as banned, so we can show him in the banned list
        # and maybe unban him later
        self.users[nick]["banned"]=True
        self._update_gui()


    ## \fn request_unban_user(self, nick)
    # \brief Called when the user want to unban a user.
    # \param nick NIck of the user to be unbanned.
    def request_unban_user(self, nick):
        self.log.info(QApplication.translate("SCoreProfe.log", "Revocando prohibicion de acceso al usuario: %1", 
                                                None, QApplication.UnicodeUTF8).arg(nick))
        ldebug("Desbaneando usuario: '%s'\n%s\n" % (nick, ('-'*80)))
        # We need the full JID to unban the user.
        jid = self.users[nick].get("jid", None)
        if jid:
            self.bot.unban_user(jid)
            # We need to delete the user because he is not in the MUC
            # and we don't want him to appear in the connected users list.
            del self.users[nick]
            self._update_gui()

    ## \fn request_identify_user(self, nick)
    # \brief Requests a user to identify itself.
    # \param nick Nick of the user to identify.
    def request_identify_user(self, nick):
        self.log.info(QApplication.translate("SCoreProfe.log", "Identificando usuario: %1", 
                                                None, QApplication.UnicodeUTF8).arg(nick))
        linfo("Identificando usuario '%s'" % nick)
        jid = self.users[nick].get("jid", None)
        self.bot.rpc_call(jid, "IDENTIFY", handler=None)

    ## \fn request_open_muc(self)
    # \brief The user wants to open the MUC
    def request_open_muc(self):
        self.log.info(QApplication.translate("SCoreProfe.log", "Abriendo el grupo."))
        ldebug("Abriendo MUC\n%s\n" % ('-'*80))
        self.bot.open_muc()

    ## \fn request_close_muc(self)
    # \brief The user wants to close the MUC
    def request_close_muc(self):
        self.log.info(QApplication.translate("SCoreProfe.log", "Cerrando el grupo."))
        ldebug("Cerrando MUC\n%s\n" % ('-'*80))
        self.bot.close_muc()

    ## \fn _update_gui(self)
    # \brief Asks the GUI to update itself.
    def _update_gui(self):
        self.gui.update_gui(self.users)

    ## \fn request_del_user(self, nick)
    # \brief Removes a user from the user list when he lefts the MUC.
    # \param nick Nick of the user to be removed.
    def request_del_user(self, nick):
        self.log.info(QApplication.translate("SCoreProfe.log", "Usuario desconectado: %1", 
                                                None, QApplication.UnicodeUTF8).arg(nick))
        ldebug("CORE :: Removing user: '%s'" % nick)
        if nick in self.users.keys():
            # A user that is banned cannot be deleted from the user list,
            # as that'd make him disappear from the banned users list.
            if not self.users[nick]["banned"]:
                del self.users[nick]
            self._update_gui()
        else:
            lerror("Trying to remove non-existant user!: '%s'" % nick)
        if self.resources_win:
            self.resources_win.update_resources(self.resources_win.resource_list, self.jid, self.users)

    ## \fn request_add_user(self, data)
    # \brief Adds a new user to the user list
    # \param data Data of the new user (nick, ip, jid...)
    def request_add_user(self, data):
        self.log.info(QApplication.translate("SCoreProfe.log", "Usuario conectado: %1", 
                                                None, QApplication.UnicodeUTF8).arg(data["nick"]))
        ldebug("CORE :: Adding new user: '%s'" % data["nick"])
        # Directly add the data to the dict using the nick as key.
        self.users[data["nick"]] = data
        # The user is not banned (yet :) )
        self.users[data["nick"]]['banned'] = False
        self._update_gui()
        if self.resources_win:
            self.resources_win.update_resources(self.resources_win.resource_list, self.jid, self.users)

    ## \fn closeEvent(self)
    # \brief Called when the GUI window is closed.
    # If we need to cancel the close, return False.
    def closeEvent(self):
        self.log.info(QApplication.translate("SCoreProfe.log", "Saliendo de la aplicación...", 
                                                None, QApplication.UnicodeUTF8))
        # Este evento se llama cuando se cierra la ventana del programa.
        # Devuelve True si es correcto continuar. False si se cancela el cierre
        self.request_destroy_resource()
        try:
            self.gui.log_win.hide()
        except:
            pass
        self.gui.hide()
        self.xmpp_server.stop()
        self.log.info(QApplication.translate("SCoreProfe.log", "Cerrando la aplicación.", 
                                                None, QApplication.UnicodeUTF8))
        return True

    ## \fn launchApp(self, cmd)
    # \brief Launches an aplication from the "Tools" menu.
    # \param cmd Command to be ran.
    def launchApp(self, cmd):
        self.log.info(QApplication.translate("SCoreProfe.log", "Lanzando aplicación: %1", 
                                                None, QApplication.UnicodeUTF8).arg(cmd))
        ldebug("Launching '%s'" % cmd)
        try:
            pid = Popen([cmd,]).pid
        except OSError, m:
            self.log.info(QApplication.translate("SCoreProfe.log", "Error: Comando desconocido (%1)", 
                                                None, QApplication.UnicodeUTF8).arg(cmd))
            lerror("Unknown command '%s' (%s)" % (cmd, m))
            msg = QString(u"Ha ocurrido un error al ejecutar la aplicación.<br>Por favor contacte con el CGA y provea los siguientes detalles:<br><br><b>Comando</b>: '%s'<br><b>Error</b>: '%s'" % (cmd, m.args[1]))
            self.gui._message(msg)
        else:
            self.log.info(QApplication.translate("SCoreProfe.log", "Aplicación %1 lanzada. PID: %2", 
                                                None, QApplication.UnicodeUTF8).arg(cmd).arg(pid))
            ldebug("Launched '%s' with PID %d" % (cmd, pid))

    def view_resources(self):
        self.resources_win.show()


if __name__=="__main__":
#    import sys
#    reload(sys)
#    sys.setdefaultencoding("utf-8")

    s = SCoreProfe()
    s.run()
