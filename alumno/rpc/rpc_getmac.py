#!/usr/bin/python
# -*- coding: utf-8 -*-
## \namespace rpc

import sys
import commands

import netifaces

from sigala.common.irpcmodule import IRPCModule
from sigala.common.netdev import NetDev

## \class RPC_getMAC
#  \brief
class RPC_getMAC(IRPCModule):
    ## \fn __init__(self)
    #  \brief 
    #  \param
    def __init__(self, core=None):
        self.name="MAC"

    ## \fn  main(self)
    #  \brief Returns the MAC of the default route or None if no MAC assigned
    #  \param
    #  \return MAC of the default route 
    def main(self):
        # Returns the MAC of the default route or None if no MAC assigned
        nd = NetDev()
        return nd.default_mac()

    ## \fn  
    #  \brief 
    #  \param
    #  \return 
    def __repr__(self):
        return "%s: %s" % (self.name, self.main())

if __name__=="__main__":
    r = RPC_getMAC()
    mac = r.main()
    print "MAC: %s" % mac
