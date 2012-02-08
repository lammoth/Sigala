#!/usr/bin/python
# -*- coding: utf-8 -*-
## \namespace rpc

import sys
import commands

import netifaces

from sigala.common.irpcmodule import IRPCModule
from sigala.common.netdev import NetDev

## \class RPC_getIP(IRPCModule)
#  \brief 
class RPC_getIP(IRPCModule):
    ## \fn  
    #  \brief 
    #  \param
    def __init__(self, core=None):
        self.name="IP"

    ## \fn  main(self)
    #  \brief   Returns the IP of the default route or None if no IP assigned
    def main(self):
        # Returns the IP of the default route or None if no IP assigned
        nd = NetDev()
        return nd.default_ip()

    ## \fn  
    #  \brief 
    #  \return
    def __repr__(self):
        return "%s: %s" % (self.name, self.main())

if __name__=="__main__":
    r = RPC_getIP()
    ip = r.main()
    print "IP: %s" % ip
