#!/usr/bin/env python
# -*- coding: utf-8 -*-
##\namespace alumno
import sys
import os
import logging
import logging.config

from threading import Lock

from PyQt4.QtCore import *
from PyQt4.QtGui import *
from dbus.mainloop.glib import DBusGMainLoop

from sigala.common.settings import LOGGING_CONFIG_FILE
from sigala.alumno.settings import EXIT_CODE_MESSAGES

from sigala.common.user_info import get_user_name
from sigala.common.user_info import generate_jid
from sigala.common.user_info import identify_user
from sigala.common.smdns import SMdns
from sigala.common.exception import NoDefaultDevice

from sigala.alumno.salumno import SAlumno

from sigala.gui.alumno.sguialumno import SGuiAlumno
import sigala.gui.alumno.resources_rc


##\class SCoreAlumno
# \brief SIGALA Student's core.
class SCoreAlumno():
	## \fn __init__(self)
	# \brief Core constructor. Sets up handlers, gui, debus, etc..
	def __init__(self):
		self.resource_list = {}
		self.resource_name = None
		self.shared_info = None
		self.bot = None

		self.bot_handlers = {
			"STATUS_CONNECTED": self.handle_connected,
			"STATUS_DISCONNECTED": self.handle_disconnected,
			"STATUS_MESSAGE":   self.handle_bot_status_message,
		}
		self.gui_handlers = {
			"REQUEST_JOIN_MUC": self.request_join_muc,
			"REQUEST_EXIT_MUC": self.request_exit_muc,
			"GET_SHARED_INFO": self.get_shared_info,
			"EXIT_APPLICATION": self.exit_application,
			"RECONNECT": self.reconnect,
		}

		self.qapp = QApplication(sys.argv)
		self.i10n()

		self.gui = None
		self._setup_gui()

		self.log = None
		self._setup_logging()
		self.log.info(QApplication.translate("SCoreAlumno.log", "Iniciando cliente."))

		self.mdns = None

		try:
			self._setup_dbus()
		except NoDefaultDevice, e:
			#os.system('zenity --error --title="SIGALA" --text="SIGALA necesita una conexión de red para su correcto funcionamiento."')
			pass
		
		self.resource_list_lock = Lock()

	## \fn i10n(self)
	# \brief Translates the GUI
	def i10n(self):
		locale = QLocale.system().name()
		self.qtTranslator = QTranslator()
		if self.qtTranslator.load("sgui_alumno_" + locale, ":/tr"):
			logging.info("Cargando traducciones para: (%s)" % locale)
			self.qapp.installTranslator(self.qtTranslator)

	## \fn _setup_logging(self)
	# \brief Sets up the logging class attribute.
	def _setup_logging(self):
		logging.config.fileConfig(LOGGING_CONFIG_FILE)
		self.log = logging.getLogger('sigala.client')

	def reconnect(self):
		if not self.resource_list:
			try:
				self._setup_dbus()
			except NoDefaultDevice, e:
				os.system('zenity --error --title="SIGALA" --text="SIGALA necesita una conexión de red para su correcto funcionamiento."')

	## \fn _setup_dbus(self)
	# \brief Sets up the dbus class attribute.
	def _setup_dbus(self):
		DBusGMainLoop( set_as_default=True )
		self.mdns = SMdns()
		self.mdns.browse(self.handle_resource_found, self.handle_resource_lost)

	## \fn _setup_gui(self)
	# \brief Sets up the gui class attribute.
	def _setup_gui(self):
		self.qapp.setOrganizationName("cga")
		self.qapp.setApplicationName("SIGALA")
		self.qapp.setQuitOnLastWindowClosed(False)
		# Internacionalización
		self.gui = SGuiAlumno()
		self.gui.set_core_handlers(self.gui_handlers)

	## \fn run(self)
	# \brief Run application.
	def run(self):
		sys.exit(self.qapp.exec_())

	## \fn request_join_muc(self, muc_jid)
	# \brief Join into Multi User Chat.
	# \param muc_jid MUC identifier.
	def request_join_muc(self, muc_jid):
		id_intr = 0
		resource = self.resource_list[muc_jid]
		ip = resource['ip']
		if len(get_user_name()) == 0:
			logging.debug("El username: '%s'" % get_user_name())
			identify_user()
		else:
			id_intr = 1
			
		if id_intr == 1:
			#TODO: Quitar o cambiar el apaño (sufijo del jid y nick) para tener servidor y cliente
			#funcionando en la misma máquina:
			jid = 'a'+generate_jid(resource['hostname'])
			nick = ' ' + get_user_name()
			self.bot = SAlumno(jid=jid, muc_jid=muc_jid, nick=nick, parent=self)
			self.bot.set_core_handlers(self.bot_handlers)
			self.bot.connect((ip, 5222))
			self.bot.process(threaded=True)
			self.log.info(QApplication.translate("SCoreAlumno.log", "Conectando al grupo: %1 - %2 (%3)",
													None, QApplication.UnicodeUTF8).arg(
														resource['muc_name']).arg(
														resource['prof_name']).arg(
														resource['hostname'])
						)

	## \fn handle_connected(self, muc_jid)
	# \brief Handle connected to a MUC event.
	# \param muc_jid MUC identifier.
	def handle_connected(self, muc_jid):
		if muc_jid in self.resource_list.keys():
			self.resource_name = muc_jid
			# Update Gui from others threads
			self.gui.emit(SIGNAL("connectionStablished"), self.resource_list, self.resource_name)
			self.request_shared_info()
			self.log.info(QApplication.translate("SCoreAlumno.log", "Conexión establecida.",
													None, QApplication.UnicodeUTF8))
		else:
			self.log.info(QApplication.translate("SCoreAlumno.log", "No se puede conectar al recurso %1, no \
																	esta en la lista.", None,
																	QApplication.UnicodeUTF8).arg(muc_jid))
			self.request_exit_muc()

	## \fn handle_disconnected(self)
	# \brief Handle disconnected.
	def handle_disconnected(self):
		self.bot = None
		self.resource_name = None
		self.log.info(QApplication.translate("SCoreAlumno.log", "Desconectado."))
		self.gui.emit(SIGNAL("connectionLost"), self.resource_list, self.resource_name)

	## \fn handle_bot_status_message(self, code, msg)
	# \brief Handle xmpp bot errors, and emits signals to notify the GUI.
	# \param code Error code.
	# \param msg Error message.
	def handle_bot_status_message(self, code, msg):
		# Show messages from others threads in the Gui
		self.log.warn(QApplication.translate("SCoreAlumno.log", "Estado %1: %2", None,
											QApplication.UnicodeUTF8).arg(code).arg(msg))
		self.gui.emit(SIGNAL("msgReceived"), msg)
		if int(code) in EXIT_CODE_MESSAGES:
			self.request_exit_muc()

	## \fn request_shared_info(self)
	# \brief Make a RPC call for request teacher's shared information.
	def request_shared_info(self):
		self.log.info(QApplication.translate("SCoreAlumno.log", "Solicitando información de compartido.",
												None, QApplication.UnicodeUTF8))
		prof_jid = self.resource_list[self.resource_name]["prof_jid"]
		self.bot.rpc_call(prof_jid, "SHARED_INFO", handler=self._set_shared_info)

	## \fn _set_shared_info(self)
	# \brief Receive and process the teacher's shared information.
	# \param *args RPC result params.
	def _set_shared_info(self, id, info):
		self.log.info(QApplication.translate("SCoreAlumno.log", "Recibida información de compartido.",
												None, QApplication.UnicodeUTF8))
		self.shared_info = dict(info)
		self.shared_info["nick"] = self.bot.nick
		self.shared_info["group"] = self.resource_list[self.resource_name]["muc_name"]

	def get_shared_info(self):
		return self.shared_info

	## \fn request_exit_muc(self)
	# \brief Manage the disconnection from resource. Emits signal to notify the GUI.
	def request_exit_muc(self):
		try:
			resource = self.resource_list[self.resource_name]
			self.log.info(QApplication.translate("SCoreAlumno.log", "Desconectando del grupo: %1 - %2",
													None, QApplication.UnicodeUTF8).arg(
															   resource['muc_name']).arg(
															   resource['prof_name'])
						)
		except KeyError:
			pass
		self.resource_name = None
		self.shared_info=None
		if self.bot is not None:
			logging.info('Disconnecting ...\n%s\n', ('-'*80))
			self.bot.disconnect()
		self.gui.emit(SIGNAL("connectionLost"), self.resource_list, self.resource_name)
		self.gui.emit(SIGNAL("hideSharedClient"))

	## \fn handle_resource_found(self, name, domain, address, port, info_dict)
	# \brief Handle the Resource Found event.
	# \param name Resource Name.
	# \param domain Resource Domain.
	# \param address Resource Address.
	# \param port Resource Port.
	# \param info_dict Aditional information necessary for configure resource.
	def handle_resource_found(self, name, domain, address, port, info_dict):
		logging.info('Resource Found: %s Domain: %s / host: %s' % (name, domain, info_dict['hostname']))
		info_keys = info_dict.keys()
		if 'muc_jid' in info_keys and 'muc_name' in info_keys and 'prof_name' in info_keys and 'prof_jid' in info_keys:
			self.log.info(QApplication.translate("SCoreAlumno.log", "Grupo encontrado: %1 - %2",
																None, QApplication.UnicodeUTF8).arg(
																info_dict['muc_name']).arg(
																info_dict['prof_name'])
						)
			info_dict['service_name'] = name
			with self.resource_list_lock:
				self.resource_list[info_dict['muc_jid']] = info_dict
			self._update_gui()

	## \fn handle_resource_lost(self, *args)
	# \brief Handle the Resource Lost event.
	# \param *args Array with information about resource lost.
	def handle_resource_lost(self, *args):
		resource_index = None
		logging.info('Resource Lost: %s' % args[0])
		for resource in self.resource_list.values():
			if resource['service_name'] == args[0]:
				resource_index = resource['muc_jid']
				continue
		if resource_index is not None:
			resource = self.resource_list[resource_index]
			self.log.info(QApplication.translate("SCoreAlumno.log", "Grupo perdido: %1 - %2",
													None, QApplication.UnicodeUTF8).arg(
															   resource['muc_name']).arg(
															   resource['prof_name'])
						)
			with self.resource_list_lock:
				del self.resource_list[resource_index]
			self._update_gui()

	## \fn update_gui(self)
	# \brief Sets up the GUI from the variables resource_list and resource_name
	def _update_gui(self):
		logging.info('Resource List: \n\t%s' % self.resource_list)
		self.gui.update_gui(self.resource_list, self.resource_name)

	## \fn exit_application(self)
	# \brief Make things when client closed..
	def exit_application(self):
		self.request_exit_muc()
		self.log.info(QApplication.translate("SCoreAlumno.log", "Cerrando cliente."))
		self.qapp.quit()

if __name__=='__main__':
#    import sys
#    reload(sys)
#    sys.setdefaultencoding("utf-8")
    sc = SCoreAlumno()
    sc.run()
