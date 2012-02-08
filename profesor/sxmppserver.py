# -*- coding: utf-8 -*-
#\namespace profesor

import commands

from settings import XMPP_SERVER_COMMAND

class SXmppServerException(Exception): 
    """ Excepción a usar en la clase SXmppServer """
    pass

#\class SXmppServer
#\brief Class controlling the XMPP server.
class SXmppServer:
    """ 
    Se encarga de iniciar, deterner y reiniciar el servidor XMPP.
    Eleva una excepción en caso de error en alguna de las operaciones
    """

    ## \fn start()
    # \brief Starts the XMPP server.
    def start(self):
        # Para curarnos en salud, antes de inicar el servidor vamos a detenerlo.
        self._do_action("restart")

    ## \fn stop()
    # \brief Stops the XMPP server
    def stop(self):
        self._do_action("stop")

    ## \fn restart()
    # \brief Restarts the XMPP server
    def restart(self):
        self._do_action("restart")

    ## \fn _do_action(action)
    # \brief Executes the XMPP command with the provided parameter
    # \param action Action to pass to the XMPP command.
    def _do_action(self, action):
        # De momento solo tienen sentido estas operaciones
        if not action in ("start", "stop", "restart"):
            raise SXmppServerException("Invalid action: '%s'" % action)
        else:
            # Normalmente el comando será del tipo 'sudo comando', pues arrancar el servidor
            # XMPP requiere privilegios para cambiar de usuario.
            cmd = "%s %s" % (XMPP_SERVER_COMMAND, action)
            ret, output=commands.getstatusoutput(cmd)
            if ret != 0:
                # Si el comando devuelve un código de error, excepción al canto.
                raise SXmppServerException("Could not %s the XMPP server: '%s'" % (action, output))

if __name__=="__main__":

# Pruebas simples de la clase SXmppServer
    
    s = SXmppServer()

    try:
        s.start()
    except SXmppServerException, m:
        print "Error al iniciar el servidor XMPP: %s" % m

    try:
        s.stop()
    except SXmppServerException, m:
        print "Error al para el servidor XMPP: %s" % m
