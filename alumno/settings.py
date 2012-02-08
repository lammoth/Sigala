# -*- coding: utf-8 -*-
## \namespace alumno
#  \brief  Configuration options for students

import os

from PyQt4.QtGui import QApplication


## \brief Where to find RPCs module
RPC_MODULES = "sigala.alumno.rpc"

## \brief Error Code Messages 
CODE_MESSAGES = {   301: QApplication.translate("SGuiAlumno", "Se te ha prohibido la entrada al grupo."),
                    307: "Has sido expulsado del grupo.",
                    403: QApplication.translate("SGuiAlumno", "Tienes prohibida la entrada a este grupo."),
                    407: QApplication.translate("SGuiAlumno", "El grupo está cerrado.", None, QApplication.UnicodeUTF8),
                    409: QApplication.translate("SGuiAlumno", "Ya hay un usuario con ese nombre."),
                    7337: QApplication.translate("SGuiAlumno", "El grupo ha sido eliminado."),
                }

## \brief The client should disconnect when receiving these codes.
EXIT_CODE_MESSAGES = ( 301, 307, 403, 407, 409, 7337 )

# \brief File in which to write our PID.
PID_FILE="/tmp/sigala-client" + str(os.getuid()) + ".pid"



