## \namespace common
# \brief Customized exceptions. 
# Normally just a more meaningful name.
# ej. 
# class BotDisconnected(Exception)

## \class NotImplementedException
#  \brief For using when a method has not been implemented
class NotImplementedException(Exception): pass

## \class NoDefaultDevice
#  \brief There's no default route, so no default network device.
class NoDefaultDevice(Exception): pass

## \class DesktopFileNotFound
# \brief Tried to load a non existent .desktop file
class DesktopFileNotFound(Exception): pass

## \class InvalidGroupName
# \brief User entered an invalid group name
class SInvalidGroupName(Exception): pass
