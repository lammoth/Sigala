# -*- coding: utf-8 -*-
## \namespace common 
import os
import logging
import string

# \brief Config file for logging.
LOGGING_CONFIG_FILE="/etc/sigala/logging.conf"

AVAHI_SERVICE_TYPE = "_profe._tcp"
AVAHI_SERVICE_PORT = "8888"

# Caracteres válidos para los nombres de usuario y mucs
VALID_CHARS = string.ascii_letters + string.digits

#File to write the PID in.
SIGALA_PID_FILE = "/tmp/sigala.pid"

SHARED_PRIVATE="SUBIDAS"

# \brief Command to execute by the identification method
IDENTIFY_COMMAND="/usr/bin/cga-sigala-identify-user"

def setup_sigala_config_dir():
    # Comprueba y crea el directorio $HOME/.sigala
    home=os.getenv("HOME")
    ruta=os.path.join(home, ".sigala")
    try:
        os.stat(ruta)
    except OSError:
        # El directorio no existe, se crea.
        os.mkdir(ruta)
