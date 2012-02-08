# -*- coding: utf-8 -*-
## \namespace common
#  \brief Interface for load RPC modules

from exception import *

## \class IRPCModule
#  \brief Emulates an interface for RPC modules
class IRPCModule:
    """ Emulates an interface for RPC modules """
    ## \fn  __init__(self)
    #  \brief RPC method name
    def __init__(self, core=None):
        # RPC method name
        self.name = None

    ## \fn main(self, *args)
    #  \brief 'main' method not in requested object
    def main(self, *args):
        raise NotImplementedException("No 'main' method in '%s'" % (__file__))
