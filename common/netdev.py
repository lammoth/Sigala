#!/usr/bin/python
# -*- coding: utf-8 -*-
## \namespace common
#  \brief Obtains info about network devices

import sys
import commands
import socket

import netifaces

from exception import *

## \class NetDev
#  \brief Obtains info about network devices
class NetDev:
    """
    Obtención de información sobre los dispositivos de red.
    """
    ## \fn default_info(self, ielement)
    #  \brief Returns MAC or IP address of the default network device
    #  \return MAC or IP address
    #  \params[in] ielement: MAC or IP
    def default_info(self, ielement):
        """ Devuelve la ip o la mac del dispositivo de red por defecto. """
        element = None
        # Get iface addresses.
        addresses = self._get_addresses()
        if addresses == None:
            raise NoDefaultDevice("Interface not connected")
        else:
            if ielement in addresses.keys():
                # Get the IP or MAC
                element = addresses[ielement][0]['addr']

            # If no default route, return None
            return element

    ## \fn default_ip(self)
    #  \brief Returns default's network device IP address
    #  \return IP address
    def default_ip(self):
        """ Devuelve la ip del dispositivo de red por defecto. """

        element_type = netifaces.AF_INET
        self.element_result = self.default_info(element_type)
        return self.element_result

    ## \fn default_mac(self)
    #  \brief Returns default's network device MAC address
    #  \return MAC address
    def default_mac(self):
        """ Devuelve la mac del dispositivo de red por defecto. """

        element_type = netifaces.AF_LINK
        self.element_result = self.default_info(element_type)
        return self.element_result

    ## \fn hostname(self)
    #  \brief Returns the machine name associated with the default ip
    #  \return hostname
    def hostname(self):
        """ Devuelve el nombre del equipo asociado a la ip por defecto. """

        self.hostname = socket.gethostbyaddr(self.default_ip())[0]
        return self.hostname

    ## \fn _get_addresses(self)
    #  \brief  Command to get the routing table
    #  \return Returns the default gateway device (or None if no such device, too bad!)
    def _get_addresses(self):
        # Command to get the routing table
        cmd = "ip route"
        ret=None
        iproute = commands.getoutput(cmd).splitlines()
        for l in iproute:
            # Check the default route
            if l.startswith("default"):
                s = l.split(" ")
                # Future output format proof, should the 'dev' index changes...
                idx = s.index("dev") + 1
                ret=netifaces.ifaddresses(s[idx])
    # Si no hay ruta por defecto, buscar la interfaz de local-link
    # En este caso, la salida de ip route es como esta:
    # 169.254.0.0/16 dev eth0 proto kernel scope link src 169.254.11.245 metric 2
        if ret == None:
            for l in iproute:
                if l.startswith("169.254.0.0/"):
                    s = l.split(" ")
                    idx = s.index("dev") + 1
                    ret = netifaces.ifaddresses(s[idx])

        # Returns the default gateway device (or None if no such device, too bad!)
        return ret


if __name__ == '__main__':

    #Pruebas de ejemplo para la clase NetDev

    ndv = NetDev()
    a = ndv.hostname()
    print a
