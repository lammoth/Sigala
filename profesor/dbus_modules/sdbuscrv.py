# -*- coding: utf-8 -*-

import dbus
import dbus.service

from sigala.profesor.idbusmodule import IDbusModule

class SCRVModule(dbus.service.Object, IDbusModule):
	def __init__(self, bus, core):
		self.core = core
		name = dbus.service.BusName('org.cga.sigala', bus)
		self.path = '/org/cga/sigala/CRV'
		dbus.service.Object.__init__(self, name, self.path)

	@dbus.service.method('org.cga.sigala.CRV')
	def get_user_data(self):
		users_aula = {}
		users = self.core.users
		for user in users:
			name = users[user]['nick']
			ip = users[user]['IP']
			mac = users[user]['MAC']
			users_aula[user] = {'nick':name, 'IP':ip, 'MAC':mac}
		return users_aula
