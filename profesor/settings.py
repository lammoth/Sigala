# -*- coding: utf-8 -*-
import os

from PyQt4.QtGui import QApplication

## \namespace profesor

from sigala.common.settings import SHARED_PRIVATE

#\brief Command to start/stop/restart the XMPP server
XMPP_SERVER_COMMAND = "sudo /etc/init.d/ejabberd-cgaconfig"

#\brief RPC methods to be called when a user joins the MUC
## Pay attention to the trailing ','. We don't want a single item's list
## to become a list of characters :)
RPC_ON_USER_CONNECT = ("IP","MAC")


#\brief Directory containing .desktop files to load.
DESKTOP_APP_DIR = "/usr/share/sigala/desktop"

# \brief Icono para los .desktop con icono no-accesible
DEFAULT_APP_ICON = "/usr/share/sigala/default_app.png"

#\ brief Module contaning teacher's DBUS modules
DBUS_MODULES="sigala.profesor.dbus_modules"

# \brief Teacher's RPC modules
# Indica dónde se encuentran los módulos que exportan llamadas RPC 
# del profesor.
RPC_MODULES="sigala.profesor.rpc"

# \brief SIGALA's shared dir
# Directorio para los compartidos de SIGALA
SHARED_DIR=os.path.join(os.getenv("HOME"), "SIGALA")

#\brief Directory where clients will upload their files.
# Directorio al que los alumnos suben sus ficheros.
SHARED_PRIVATE_DIR=os.path.join(SHARED_DIR, SHARED_PRIVATE)

# \brief Info about shares
# Información a mostrar cuando se inicia la compartición de archivos.
SHARED_INFO_TEXT=QApplication.translate("SGuiProfe", "Se compartirán los ficheros del directorio <b>%1</b>.<br>Los clientes subirán sus archivos al directorio <b>%2</b>.<br>Para más información consulte la <a href='file:///usr/share/doc/sigala-doc/html/index.html'>documentación de SIGALA</a>", None, QApplication.UnicodeUTF8)

# \brief File in which to write our PID.
PID_FILE="/tmp/sigala" + str(os.getuid()) + ".pid"

# \brief HTML help file
SIGALA_HTML_HELP_FILE="file:///usr/share/doc/sigala-doc/html/index.html"

