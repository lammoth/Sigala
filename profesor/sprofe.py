# -*- coding: utf-8 -*-
## \namespace profesor
#  \brief Teacher's Bot

import logging
import logging.config
from threading import Lock

from sigala.common.sbotxmpp import SBotXMPP

from sigala.common.settings import LOGGING_CONFIG_FILE

from sigala.common.exception import NotImplementedException

from sigala.profesor.settings import RPC_ON_USER_CONNECT
from sigala.profesor.settings import RPC_MODULES

logging.config.fileConfig(LOGGING_CONFIG_FILE)
linfo = logging.info
lerror = logging.error
ldebug = logging.debug

## \class SProfe(SBotXMPP)
#  \brief Teacher's Class
class SProfe(SBotXMPP):
    ## \fn __init__(self, jid, muc_jid, nick, passwd="anonymous")
    #  \brief Inizialitation routines
    # \param jid The bot's JID.
    # \param muc_jid JID of the MUC  we are joining in.
    # \param nick Out bot's nick in the MUC.
    # \param passwd Password for the server. Not used.
    # \param parent Bot's parent object, normally the core.
    def __init__(self, jid, muc_jid, nick, passwd="anonymous", parent=None):
        self.RPC_MODULES = RPC_MODULES
        super(SProfe, self).__init__(jid, muc_jid, nick, passwd, parent)
        # User list. JID as key, various as values :P
        self.users = {}
        # As events are async,. we don't want to mess with insertions an deletions
        # in users dict without protection :)
        self.users_lock = Lock()
        
    ## \fn  _load_event_handlers(self)
    #  \brief  Load event handlers 
    def _load_event_handlers(self):
        # As we are adding aditional event handlers, 
        # we need to let the parent add his own handlers
        super(SProfe, self)._load_event_handlers()
        self.add_event_handler("groupchat_presence", self.handle_muc_presence)

    ## \fn handle_muc_presence(self, entry)
    #  \brief Manages MUC presence events.
    # \param entry XMPP presence stanza
    def handle_muc_presence(self, entry):
        ldebug('Presence events\n%s\n', ('-'*80))
        user = entry.find('{%(ns)s}x/{%(ns)s}item' % 
            {'ns': 'http://jabber.org/protocol/muc#user'})
        user_muc_jid = entry.getFrom()
        nick = user_muc_jid.resource
        real_jid = user.get("jid")
        tipo = entry.getType()
        if real_jid == self.fulljid or real_jid is  None:
            # Our own presence or we have no permission to see the 
            # real JID of the user (shouldn't happen, this is bad).
            ldebug("Ignoring user: %s" % entry)
            return
        if tipo == "unavailable":
            # The user left the MUC.
            ldebug(u"Report to the core about user disappearing '%s'" % real_jid)
            self.core_handlers["DEL_USER_CB"](nick)
            return
        elif tipo == "available":
            # A user joins the MUC...
            if user.get("affiliation") != "member":
                # ... but we have to make him a member 
                # of the MUC before admitting him.
                self.muc.setAffiliation(room=self.muc_jid, 
                                        jid=real_jid, 
                                        affiliation="member")
                return

        # Finally, a full featured user :)
        linfo("User entered the MUC!: %s (%s)" % (nick, user_muc_jid))
        user_data = {'jid': real_jid, 'nick': nick, 'pending_rpc':{}}

        with self.users_lock:
            self.users[real_jid] = user_data
        # Run the default RPC calls on the user.
        self.process_default_rpc(real_jid)


    ## \fn process_default_rpc(self, jid)
    #  \brief Process default RPC on user connection
    #  \param jid User's JID
    def process_default_rpc(self, jid):
        linfo('Initialize RPC modules when user connect\n%s\n', ('-'*80))
        for rpc in RPC_ON_USER_CONNECT:
            id=self.rpc_call(jid, rpc, handler=self._default_rpc_handler)
            with self.users_lock:
                # We keep track of the pending RPC responses for the user.
                self.users[jid]["pending_rpc"][id] = rpc
        linfo('Sleekxmpp trace\n%s\n', ('-'*80))

    ## \fn  _default_rpc_handler(self, id, result)
    #  \brief  Handle RPC responses
    # \param id ID of the XMPP response stanza.
    # \param result Result of the RPC call.
    def _default_rpc_handler(self, id, result):
        linfo("Received RPC response\n%s\n" % ('-'*80))
        ldebug("RPC Response: id:'%s', result:'%s'" % (id, result))
        response_handled=False
        # List to know which users to delete once completed.
        # We need to track this because we can't modify the user list 
        # while iterating it.
        to_clean=[]
        with self.users_lock:
            for user in self.users:
                try:
                    call_name = self.users[user]["pending_rpc"].pop(id)
                    # Add the call name as key and result as value 
                    # to the user info dict.
                    self.users[user][call_name] = result
                    response_handled=True
                except KeyError, m:
                    ldebug("User '%s' not waiting for that response (%s): '%s'" % (user, id, result))
                if len(self.users[user]["pending_rpc"].keys()) == 0:
                    # No more pending RPCs for the user, report new user to Core...
                    self._report_new_user(self.users[user])
                    to_clean.append(user)

            for u in to_clean:
                # Delete all the users that got reported to the core.
                del self.users[u]

        if not response_handled:
            lerror("Unexpected RPC response (%s): '%s'" % (id, result))

    ## \fn _report_new_user(self, user)
    # \brief Reports the new user to the core.
    # \param user Dictionary with the info os the user to be added.
    def _report_new_user(self, user):
        del user["pending_rpc"]
        ldebug("New user ready: %s" % user)
        self.core_handlers["NEW_USER_CB"](user)
                
    ## \fn _ser_muc_config(self, **config)
    # \brief Stablishes the MUC config according to the named parameters.
    # Example: _set_muc_config(inviteonly=False, membersonly=True)
    # \param config Named parameters.
    def _set_muc_config(self, **config):
        linfo("Settings MUC config: '%s'" % config)
        # Dictionary comprehension to form the configuration update dictionary.
        room_config = dict( ("muc#roomconfig_%s" % c, config[c]) for c in config)
        config_form = self.muc.getRoomConfig(self.muc_jid)
        values = config_form.getValues()
        # Update the configuration with our new configuration dictionary.
        values.update(room_config)
        config_form.setValues(values)
        self.muc.setRoomConfig(self.muc_jid, config_form)

    # \fn open_muc(self)
    # \brief Opens the MUC (everyone can join in).
    def open_muc(self):
        # Sets the MUC config to "public" (membersonly=False)
        self._set_muc_config(membersonly=False)

    # \fn close_muc(self)
    # \brief Closes the MUC (only members can join in).
    def close_muc(self):
        # Sets the MUC config to "private" (membersonly=True)
        self._set_muc_config(membersonly=True)

    def destroy_muc(self):
        """
        Destroy the muc when the teacher closes the group.
        """
        self.muc.destroy(self.muc_jid)

    # \fn kick_user(self, nick)
    # \brief Temporarily kicks a user from the MUC
    # \param nick Nick of the user to kick from the MUC.
    def kick_user(self, nick):
        # Kicks the user from the MUC (role="none")
        self.muc.setRole(self.muc_jid, nick=nick, role="none")

    # \fn ban_user(self, jid)
    # \brief Ban a user from the MUC.
    # Unlike kicks, a ban has to be done to the JID of the user, not the Nick.
    # \param jid The JID of the user to kick.
    def ban_user(self, jid):
        # Sets an user affiliation to "outcast"
        self.muc.setAffiliation(self.muc_jid, jid=jid, affiliation="outcast")

    # \fn unban_user(self, jid)
    # \brief Unbans a user from the MUC.
    # \param jid JID of the user to readmit.
    def unban_user(self, jid):
        # Sets the user affiliation to "member"
        self.muc.setAffiliation(self.muc_jid, jid=jid, affiliation="member")

    # \fn set_core_handlers(self, handlers)
    # \brief Set the handlers for the different events the bot can receive.
    # \param handlers Dictionary in the form EVENT:handler
    def set_core_handlers(self, handlers):
        self.core_handlers = handlers

if __name__=="__main__":
    host = "monkey.cga.andared.cec.junta-andalucia.es"
    jid = "@%s" % (host)
    password = "profesor"
    muc_jid = "salita@conference.%s" % (host)
    nick = "Un bot de profesor cualquiera"
    bot = SProfe(jid, muc_jid, nick, passwd=password)
    bot.connect()
    bot.process(threaded=False)
