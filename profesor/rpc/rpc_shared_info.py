#!/usr/bin/python
# -*- coding: utf-8 -*-
## \namespace rpc

from sigala.common.irpcmodule import IRPCModule

## \class RPC_sharedInfo(IRPCModule)
#  \brief 
class RPC_sharedInfo(IRPCModule):
    ## \fn  
    #  \brief 
    #  \param
    def __init__(self, core):
	self.core = core
        self.name="SHARED_INFO"
        print "Loading module '%s'" % self.name

    ## \fn  main(self)
    #  \brief   Returns the information needed to connect to the shared Webdav 
    def main(self):
        info = {    "IP": self.core.shared.IP, 
                    "port": self.core.shared.port, 
                    "user": self.core.shared.user, 
                    "password": self.core.shared.password
                }
        return info

    def __repr__(self):
        return "%s" % (self.name)

if __name__=="__main__":
    r = RPC_sharedInfo()
    info = r.main()
