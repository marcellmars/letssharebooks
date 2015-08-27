#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sleekxmpp
import sys
import pickle
import time
import requests

time.sleep(4)


class MUCBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, room, nick):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)
        self.base_url = "https://library.memoryoftheworld.org"
        self.room = room
        self.nick = nick
        self.add_event_handler("session_start", self.start)
        self.add_event_handler("muc::{}::got_online".format(self.room),
                               self.greetings)

    def greetings(self, presence):
        nick = presence['from'].resource

        welcome = "Dear {}, welcome to the 'Ask a librarian' chat room.\n"\
            .format(nick.title())
        welcome += "Browse and share your public library collection at:\n"
        welcome += "{}/#librarian={}".format(self.base_url,
                                             nick.title().replace(" ", "+"))

        try:
            nicks = requests.get("{}/get_active_librarians"
                                 .format(self.base_url),
                                 verify=False)
            if nicks.ok:
                nicks = nicks.json()['librarians']
            else:
                sys.stderr.write("No active librarians?")

        except requests.exceptions.RequestException as e:
            nicks = {'librarians': []}
            sys.stder.write("Web app doesn't work?\nRequestException: {}"
                            .format(e))
            self.disconnect()

        if nick in nicks and presence['from'].bare == self.room:
            self.send_message(mto=presence['from'].bare,
                              mbody=welcome,
                              mtype='groupchat')
        sys.stderr.write("{} joined Ask a librarian chat room."
                         .format(nick.title()))

    def start(self, event):
        self.send_presence()
        self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        wait=True)
        sys.stderr.write("{} joined Ask a librarian chat room."
                         .format(self.nick))

xmpp = MUCBot("biblibothekar@xmpp.memoryoftheworld.org",
              pickle.load(open("/usr/local/bin/.password", "r")),
              "ask_a_librarian@conference.memoryoftheworld.org",
              "Bibli Bot Hekar")

xmpp.register_plugin('xep_0045')

if xmpp.connect():
    xmpp.process(block=True)
else:
    sys.exit(-2)
