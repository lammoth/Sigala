# -*- coding: utf-8 -*-
## \namespace profesor
#  \brief Interface for DBus modules

from sigala.common.exception import *

## \class IDbusModule
#  \brief Interface for DBus modules
class IDbusModule:
    """ Interfaz que debe implementar los módulos DBus. """

    ## \fn __init__(self, core)
    #  \brief Initialize DBus modules
    #  \param core SCore instance
    def __init__(self, core):
        raise NotImplementedException("No '__init__' method implemented")

if __name__=="__main__":
    core = SCore
    test = IDbusModule(core)
