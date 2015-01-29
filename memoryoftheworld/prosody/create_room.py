#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sleekxmpp
import sys
import pickle
import time

time.sleep(4)

class MUCBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, room, nick):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.room = room
        self.nick = nick
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("muc::{}::got_online".format(self.room),
                               self.greetings)

    def greetings(self, presence):
        nick = presence['from'].resource
        if nick != self.nick and presence['from'].bare == self.room:
            self.send_message(mto=presence['from'].bare,
                              mbody="""Dear {}, welcome to the 'Ask a librarian' chat room.\nBrowse and share your public library collection at:\nhttps://library.memoryoftheworld.org/#author=&title=&metadata=&librarian={}&page=1""".format(nick.title(),nick.title().replace(" ", "+")),
                              mtype='groupchat')
        
    def start(self, event):
        self.send_presence()
        self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        wait=True)

xmpp = MUCBot("biblibothekar@xmpp.memoryoftheworld.org",
              pickle.load(open("/usr/local/bin/.password","r")),
              "askalibrarian@conference.memoryoftheworld.org",
              "Bibli Bot Hekar")

xmpp.register_plugin('xep_0045')

if xmpp.connect():
    xmpp.process(block=True)
else:
    sys.exit(-2)
