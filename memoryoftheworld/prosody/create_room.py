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
    def start(self, event):
        self.send_presence()
        self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        wait=True)

xmpp = MUCBot("marcell@xmpp.memoryoftheworld.org", pickle.load(open("/usr/local/bin/.password","r")), "letssharebooks@conference.memoryoftheworld.org", " . ")
xmpp.register_plugin('xep_0045')

if xmpp.connect():
    xmpp.process(block=True)
else:
    sys.exit(-2)
