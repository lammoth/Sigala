#!/usr/bin/python
# -*- coding: utf-8 -*-
## \namespace rpc

import sys


import netifaces

from sigala.common.irpcmodule import IRPCModule
from sigala.common.netdev import NetDev
from sigala.common.user_info import identify_user



## \class RPC_identify(IRPCModule)
#  \brief 
class RPC_identify(IRPCModule):
    ## \fn  
    #  \brief 
    #  \param
    def __init__(self, core):
        self.name="IDENTIFY"
        self.core=core

    ## \fn  main(self)
    #  \brief   Ejecuta el cambio de identidad del alumno.
    def main(self):
        self.core.request_exit_muc()
        identify_user()
