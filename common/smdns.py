#!/usr/bin/python
# -*- coding: utf-8 -*-
## \namespace  common

import logging
import logging.config
import dbus
import gobject
import avahi
import json

from dbus import DBusException
from dbus.mainloop.glib import DBusGMainLoop

from sigala.common.settings import AVAHI_SERVICE_TYPE
from sigala.common.settings import AVAHI_SERVICE_PORT
from sigala.common.settings import LOGGING_CONFIG_FILE

from sigala.common.netdev import NetDev

logging.config.fileConfig(LOGGING_CONFIG_FILE)

## \class SMdns
## \brief Manages mDNS's publications
#  Manages the publication / unpublicartion of services (resources) for mDNS for the teacher, and discovery for the student
class SMdns:
    """ 
    Gestiona la publicación/despublicación de servicios (recursos) por mDNS para el profesor, y 
    el descubrimiento para el alumno.
    """
    
    ## \fn __init__(self, error_handler=None)
    #  \brief Setup Dbus stuff
    def __init__(self, error_handler=None):
        self.error_handler = (self._local_error_handler, error_handler)[error_handler is not None]
        self.group=None
        
        nd = NetDev()
        self.hostname = nd.hostname()
        self.ip = nd.default_ip()
        self.domain = ""

        self.sysbus = dbus.SystemBus()    #System bus for access to avahi methods
        
        self.server = dbus.Interface(self.sysbus.get_object(avahi.DBUS_NAME, avahi.DBUS_PATH_SERVER),
                                    avahi.DBUS_INTERFACE_SERVER)

         
    ## \fn _local_error_handler(self, *args)
    #  \brief Error handler
    def _local_error_handler(self, *args):
        logging.info("SMDns: %s" % args[1])
        pass

    ## \fn _local_found_handler(self, name, domain, address, port, info_dict)
    #  \brief Found resource  handler
    def _local_found_handler(self, name, domain, address, port, info_dict):
        logging.info('\n\tService found:\n\t\tname: %s\n\t\tdomain: %s\n\t\taddress: %s\n\t\tport: %s\n\t\tinfo_dict: %s', 
                    name, domain, address, port, info_dict)

    ## \fn _local_lost_handler(self, *args)
    def _local_lost_handler(self, *args):
        logging.debug("(SMdns._local_lost_handler) - %s:%s" % (args[0], args[1]))
    
    ## \fn _handle_service_resolved(self, *args)
    #  \brief Obtains txt field and other data from  resource: dictionary is  json encoded 
    def _handle_service_resolved(self, *args):
        # Obtenemos el campo txt del recurso: diccionario codificado con json
        avahi_txt_list = avahi.txt_array_to_string_array(args[9])
        elem = ''.join(avahi_txt_list)[::-1]
        try:
            info_dict = json.loads(elem)
        except:
            info_dict = {}
        
        # Resto de datos del servicio..
        s_name = args[2]
        s_type = args[3]
        s_domain = args[4]
        s_address = args[7]
        s_port = args[8]

        self.found_handler(s_name, s_domain, s_address, s_port, info_dict)
	    
    ## \fn _handle_new_item(self, interface, protocol, name, stype, domain, flags
    #  \brief ItemNew Handler 
    #  Event handler "ItemNew" of self.sbrowser. Responsible for resolving and connecting service handler 
    #  found "dynamic" self.found_handler for collecting the data of the resolution.
    #  \param 
    def _handle_new_item(self, interface, protocol, name, stype, domain, flags):
        # Manejador del evento "ItemNew" de self.sbrowser. Se encarga de resolver el servicio encontrado
        # y conectar el manejador "dinámico" self.found_handler para que recoja los datos de la resolución.
        logging.info('Discovered mDNS resource\n%s\n', ('-'*80))
        logging.debug("(SMdns.handle_found) + %s" % name)
        self.server.ResolveService(interface, protocol, name, stype, domain, avahi.PROTO_UNSPEC, 
                            dbus.UInt32(0), reply_handler=self._handle_service_resolved, error_handler=self.error_handler)
	    
    ## \fn _handle_remove_item(self, interface, protocol, name, stype, domain, flags)
    #  \brief Remove Item  handler 
    #  Method Server.ResolverService is not available in this context,
    #  spend only the name and the domain, which should uniquely identify the resource
    def _handle_remove_item(self, interface, protocol, name, stype, domain, flags):
        logging.info('Lost mDNS resource\n%s\n', ('-'*80))
        logging.debug("(SMdns.handle_lost) - %s" % name)
        # El método server.ResolverService no está disponible en este contexto, 
        # se pasan sólo el nombre y el dominio, con lo que se debería identificar unívocamente el recurso:
        self.lost_handler(name, domain)
        		
    ## \fn _entry_group_state_changed(self, state, error)
    #  \brief Notify group state changes
    def _entry_group_state_changed(self, state, error):
        logging.debug(error)
        if state not in (1, 2):
            self.error_handler(state, error)

    ## \fn publish(self, s_name, s_data={})
    #  \brief Publish data in mDNS
    def publish(self, s_name, s_data={}):
        s_data['hostname'] = self.hostname
        s_data['ip'] = self.ip
        s_txt = json.dumps(s_data)
                                            
        self.group = dbus.Interface(self.sysbus.get_object(avahi.DBUS_NAME, self.server.EntryGroupNew()),
                                    avahi.DBUS_INTERFACE_ENTRY_GROUP)
                                    
        self.group.connect_to_signal('StateChanged', self._entry_group_state_changed)
        
        self.group.AddService(
            avahi.IF_UNSPEC,		#interface
            avahi.PROTO_UNSPEC,		#protocol
            dbus.UInt32(0),			#flags
            s_name, AVAHI_SERVICE_TYPE,
            self.domain, "",
            dbus.UInt16(AVAHI_SERVICE_PORT),
            avahi.string_array_to_txt_array(s_txt))
        self.group.Commit()
            
    ## \fn unpublish(self)
    #  \brief Unpublish mDNS data
    def unpublish(self):
        if not self.group is None:
            self.group.Reset()
    
    ## \fn browse(self, found_handler=None, lost_handler=None
    #  \brief Browse mDNS data 
    def browse(self, found_handler=None, lost_handler=None):
        # Si se reciben manejadores como parámetros, sobreescribimos los locales.
        self.found_handler = (self._local_found_handler, found_handler)[found_handler is not None]
        self.lost_handler = (self._local_lost_handler, lost_handler)[lost_handler is not None]

        self.sbrowser = dbus.Interface( self.sysbus.get_object(avahi.DBUS_NAME,
                                                            self.server.ServiceBrowserNew( avahi.IF_UNSPEC,
                                                                                           avahi.PROTO_UNSPEC,
                                                                                           AVAHI_SERVICE_TYPE, self.domain,
                                                                                           dbus.UInt32(0) 
                                                                                          )),
                                        avahi.DBUS_INTERFACE_SERVICE_BROWSER)
                                        
        # Los datos proporcionados por los eventos "ItemNew" y "ItemRemove" requieren algunas transformaciones
        # antes de pasárselos a las funciones recibidas en el constructor (found_handler y lost_handler). Por eso
        # conectamos dichos eventos a métodos que harán estas transformaciones, y pasarán el resultado a dichas funciones..
        self.sbrowser.connect_to_signal("ItemNew", self._handle_new_item)
        self.sbrowser.connect_to_signal("ItemRemove", self._handle_remove_item)
        

if __name__=='__main__':
    DBusGMainLoop( set_as_default=True )
    main_loop = gobject.MainLoop()
    
    ATest = SMdns()
    ATest.publish("TestService", {'muc_jid':"salita@conference.test.domain.es", 'muc_name':"TestMucName", 
                                    'prof_name': 'John Doe'})
    ATest.browse()
    main_loop.run()
    
