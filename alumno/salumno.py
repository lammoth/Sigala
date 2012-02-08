# -*- coding: utf-8 -*-
## \namespace alumno
import logging

from sigala.alumno.settings import RPC_MODULES
from sigala.alumno.settings import CODE_MESSAGES

from sigala.common.settings import LOGGING_CONFIG_FILE

from sigala.common.sbotxmpp import SBotXMPP

logging.config.fileConfig(LOGGING_CONFIG_FILE)
linfo = logging.info
lerror = logging.error
ldebug = logging.debug


## \class SAlumno(SBotXMPP)
#  \brief A bot for the SIGALA client. 
class SAlumno(SBotXMPP):
    ## \fn __init__(self, jid, muc_jid, nick, passwd="anonymous") 
    #  \brief New bot for the client.
    # \param jid JID for the bot.
    # \param muc_jid JID of the MUC to join in.
    # \param nick The nick the client will use in the MUC.
    # \param passwd Password for the xmpp server client. Not used.
    def __init__(self, jid, muc_jid, nick, passwd="anonymous", parent=None):
        self.RPC_MODULES = RPC_MODULES
        super(SAlumno, self).__init__(jid, muc_jid, nick, passwd, parent)

    ## \fn set_core_handlers(self, handlers) 
    #  \brief Set handlers to invoque core actions
    # \param handlers Dictionary in the form EVENT:method
    def set_core_handlers(self, handlers):
        self.core_handlers = handlers

    ## \fn  _load_event_handlers(self)
    #  \brief  Load event handlers: groupchat_presence
    def _load_event_handlers(self):
        # As we are adding a new event handlers, we let the parent 
        # load its own handlers.
        super(SAlumno, self)._load_event_handlers()
        self.add_event_handler("groupchat_presence", self.handle_muc_presence)

    ## \fn  handle_muc_presence(self, entry)
    # \brief  Manages MUC presence.
    # \param entry XMPP presence stanza
    def handle_muc_presence(self, entry):
        user = entry.find('{%(ns)s}x/{%(ns)s}item' %
            {'ns': 'http://jabber.org/protocol/muc#user'})
        user_muc_jid = entry.getFrom()
        muc_jid = user_muc_jid.bare
        nick = user_muc_jid.resource
        if nick == self.nick:
            tipo = entry.getType()
            code = None
            if tipo == "unavailable":
                # We've been kicked or banned from the MUC
                status = entry.find('{%(ns)s}x/{%(ns)s}status' %
                            {'ns': 'http://jabber.org/protocol/muc#user'})
                if status is not None:
                    code = status.get("code")
                else:
                    code = 7337 #The muc has been destroyed
            elif tipo == "error":
                error = entry.find('{jabber:client}error')
                code = error.get("code")
            elif tipo == "available":
                linfo("Inform the core about our own presence.")
                self.core_handlers["STATUS_CONNECTED"](muc_jid)
            else:
                lerror("Unhandled presence type: '%s'" % tipo)
            # If we have a code, something weird has happened. Handle it.
            if code:
                self.handle_user_status(code)

    ## \fn handle_user_status(self, code)
    #  \brief  Handle the different error or presence codes.
    #  \param[in] Message code number
    def handle_user_status(self, code):
        linfo('Information about user status\n%s\n', ('-'*80))
        # Informs the core about the kick, ban, etc.
        try:
            # Get the descriptive string for the code
            msg = CODE_MESSAGES[int(code)]
        except KeyError, m:
            lerror("Unknown error code: %s" % code)
        else:
            linfo(msg)
            self.core_handlers["STATUS_MESSAGE"](code, msg)
            
    ## \fn _handle_disconnected(self, event)
    # \brief Handles the disconnection event.
    # \param event XMPP stanza.
    def _handle_disconnected(self, event):
        # Just let the core handle the disconnection event.
        self.core_handlers["STATUS_DISCONNECTED"]()
        
        
if __name__=="__main__":
    import sys
    import getopt
    import base64
    
    opts = dict(getopt.getopt(sys.argv[1:], "u:n:")[0])
    user = opts.get("-u", "")
    nick = opts.get("-n", "Nick del alumno")
    muc = opts.get("-m", "salita")

    host = "bowman.cga.andared.cec.junta-andalucia.es"
    jid = "%s@%s" % (user, host)
    password = "alumno"
    muc_jid = "%s@conference.%s" % (muc, host)
    print "Conectado:"
    print "JID: %s" % jid
    print "Nick: %s" % nick
    bot = SAlumno(jid, muc_jid, nick, passwd=password)
    bot.connect()
    bot.process(threaded=False)
