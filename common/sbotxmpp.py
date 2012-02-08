# -*- coding: utf-8 -*-
## \namespace common

import os
import logging
import logging.config

from xml.etree import cElementTree as ET

import sleekxmpp

from sigala.common.settings import LOGGING_CONFIG_FILE

logging.config.fileConfig(LOGGING_CONFIG_FILE)
linfo = logging.info
lerror = logging.error
ldebug = logging.debug

## \class SBotXMPP(sleekxmpp.ClientXMPP)
#  \brief XMPP client bot that connects to the server and joins a MUC 
class SBotXMPP(sleekxmpp.ClientXMPP):
    """ XMPP bot that connects to the server and joins a MUC """
    ## \fn __init__(self, jid, muc_jid, nick, passwd="anonymous", parent=None)
    #  \brief Initialize client Bot
    #  jid: Bot's JID
    #  passwd: User password (but we're using anonymous login)
    #  muc_jid: MUC's JID to join
    #  muc_name: User friendly name of the MUC
    #  parent: Parent object (i.e. the core).
    def __init__(self, jid, muc_jid, nick, passwd="anonymous", parent=None):
        linfo('XMPP bot initialization\n%s\n', ('-'*80))
        sleekxmpp.ClientXMPP.__init__(self, jid, passwd)
        self.core=parent
        self.muc_jid = muc_jid
        self.muc_name=muc_jid.split("@")[0]
        self.nick = nick

        ldebug("Bot JID: %s" % self.jid)
        ldebug("Bot nick: %s" % self.nick)
        ldebug("MUC JID: %s" % self.muc_jid)
        ldebug("MUC Name: %s" % self.muc_name)

        # Load the needed XEP's
        self._load_plugins()

        # Sets common event handlers
        self._load_event_handlers()

        # RPC call attribs.
        self.rpc_call_handlers = {}

        # Fills the dict of available RPC modules
        if hasattr(self, "RPC_MODULES"):
            ldebug("Loading rpc modules")
            self.load_rpc_modules()
            linfo("Finished reading modules RPC")
        else:
            ldebug("Not loading RPC modules")
        ldebug('Sleekxmpp trace\n%s\n', ('-'*80))

    ## \fn _load_plugins(self)
    #  \brief Load sleekxmpp's plugins needed 
    def _load_plugins(self):
        for p in ("xep_0009", "xep_0045"):
            ldebug("Loading plugin %s" % p)
            self.registerPlugin(p)
        self.rpc = self["xep_0009"]
        self.muc = self["xep_0045"]

    ## \fn _load_event_handlers(self)
    #  \brief Load event handlers for session start and rpc calls
    def _load_event_handlers(self):
        self.add_event_handler("session_start", self._session_start)
        self.add_event_handler("rpc_call_result", self._handle_rpc_response)
        self.add_event_handler("disconnected", self._handle_disconnected)

    ## \fn _session_start(self, event)
    #  \brief Inizialitation stuff: Request roster, send presence, join MUC
    #  \params[in] event: 
    def _session_start(self, event):
        linfo('Session start\n%s\n', ('-'*80))
        ldebug("Requesting roster\n%s\n", ('-'*80))
        self.getRoster()
        #ldebug("Sending presence")
        #self.sendPresence(pstatus="%s - %s".decode("UTF-8") % (self.muc_name, self.nick))
        ldebug("Joining MUC\n%s\n", ('-'*80))
        self.join_muc()
        ldebug("MUC joined\n%s\n", ('-'*80))

    ## \fn join_muc(self)
    #  \brief Joins the MUC
    def join_muc(self):
        self.muc.joinMUC(room=self.muc_jid, nick=self.nick)

    ## \fn rpc_call(self, jid, method, handler=None, *args)
    #  \brief Executes a RPC call
    #  \param jid: JID of the user we are making the RPC call to.
    #  \param method: RPC name
    #  \param handler: Method that will handle the RPC response.
    #  \param *args: Variable argument list for the RPC
    #  \return  RPC call ID.
    def rpc_call(self, jid, method, handler=None, *args):
        # Ejecuta una llamada RPC
        ldebug("********************** Calling '%s' method on JID '%s'" % (method, jid))
        ret=self.rpc.call_remote(jid, method, *args)
        if handler is not None:
            self.rpc_call_handlers[ret] = handler
            ldebug("Adding handler for RPC")
            ldebug("Added '%s' handler for ID '%s'" % (handler, ret))
            ldebug("'%s' method on JID '%s' called\n%s\n" % (method, jid, ('-'*80)))
        return ret

    ## \fn _handle_rpc_response(self, response)
    #  \brief Handles RPC calls made to a bot.
    #  \param response: XMPP Stanza response.
    def _handle_rpc_response(self, response):
        # Handles RPC calls made to the bot. It uses 
        # the handlers dict to call the corresponding 
        # response handler.
        id=response["pid"]
        result=response["params"]
        if id in self.rpc_call_handlers.keys():
            self.rpc_call_handlers[id](id, result)
        else:
            linfo("Unhandled response id=%s: '%s'" % (id, result))

    ## \fn load_rpc_modules(self)
    #  \brief Loads and register RPC modules
    def load_rpc_modules(self):
        # Loads and register RPC modules.
        modlist=[]
        modulos = __import__(self.RPC_MODULES, fromlist=["*",])
        for m in dir(modulos):
            if m.startswith("rpc_"):
                # Only load those modules in self.RPC_MODULES which 
                # name starts with rpc_.
                linfo("Importing module: '%s'" % m )
                modulo=modulos.__dict__[m]
                try:
                    self._register_module(modulo)
                except Exception, m:
                    lerror("Error loading RPC module: '%s'" % m)

    ## \fn _register_module(self, module)
    #  \brief Registers a RPC module 
    #  \param module: module reference.
    def _register_module(self, module):
        # Registers a RPC module 'module'
        for k in module.__dict__.keys():
            if k.upper().startswith("RPC_"):
                ldebug("Instantiating class '%s'" % k)
                o = module.__dict__[k](self.core)
                self.rpc.register_call(o.main, name=o.name)
                self.rpc.acl_allow(o.name, None)
                ldebug("New RPC module: %s" % (o.name))
                
    ## \fn _handle_disconnected(self, event)
    #  \brief Disconnected event handler
    #  \param event: event
    def _handle_disconnected(self, event):
        linfo('Disconnecting ...\n%s\n', ('-'*80))
        # We are not handling the disconnection event in the bot.
        pass
        
    ## \fn reconnect(self)
    #  \brief Overriding sleekxmpp reconnect method.
    def reconnect(self):
        sleekxmpp.XMLStream.disconnect(self)
        
        
if __name__=="__main__":
    host = "bowman"
    domain = "cga.andared.cec.junta-andalucia.es"
    jid = "profesor@%s.%s/RPC" % (host, domain)
    password = "profesor"
    muc_jid = "salita@conference.%s.%s" % (host, domain)
    nick = "Un bot cualquiera"
    bot = SBotXMPP(jid, muc_jid, nick, passwd=password)
    bot.connect()
    bot.process(threaded=False)

