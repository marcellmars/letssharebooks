#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sleekxmpp
import sys
import pickle
import requests
import logging
import os
import subprocess

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger('create_xmpp_room')
LOG.setLevel(logging.INFO)

LSB_DOMAIN = os.getenv("LSB_DOMAIN") or 'memoryoftheworld.org'

#------------------------------------------------------------------------------
#- echo to /etc/hosts in docker doesn't work?!?

hosts = open("/etc/hosts", "r").readlines()

hosts_lines = []
for host in hosts:
    if LSB_DOMAIN not in host:
        hosts_lines.append(host)

hosts_lines.append("127.0.0.1 xmpp.{0} conference.{0} anon.{0}\n"
                   .format(LSB_DOMAIN))

open("/etc/hosts", "w").writelines(hosts_lines)

with open("/etc/dnsmasq.d/local", "w") as f:
    config = "\n".join(["bind-interfaces",
                        "listen-address=127.0.0.1",
                        "server=172.17.42.1",
                        "server=8.8.8.8",
                        "address=/xmpp.{}/127.0.0.1".format(LSB_DOMAIN),
                        "srv-host=_xmpp-client._tcp.xmpp.{0}, xmpp.{0},5222\n"
                        .format(LSB_DOMAIN)])
    f.write(config)

d = subprocess.Popen(['supervisorctl', 'restart', 'dnsmasq'])
d.communicate()

#------------------------------------------------------------------------------


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

        welcome = "Dear {}, welcome to the 'Ask a librarian' chat room.\n"\
            .format(nick.title())
        welcome += "Browse and share your public library collection at:\n"
        welcome += "https://library.{}/#librarian={}".format(LSB_DOMAIN,
                                                             nick.title().replace(" ", "+"))

        try:
            nicks = requests.get("http://library:4321/get_active_librarians")
            if nicks.ok:
                nicks = nicks.json()['librarians']
            else:
                print("No active librarians?")

        except requests.exceptions.RequestException as e:
            nicks = {'librarians': []}
            LOG.info("Web app doesn't work?\nRequestException: {}"
                     .format(e))
            self.disconnect()

        if nick in nicks and presence['from'].bare == self.room:
            self.send_message(mto=presence['from'].bare,
                              mbody=welcome,
                              mtype='groupchat')
        LOG.info("{} joined 'Ask a librarian' chat room."
                 .format(nick.title()))

    def start(self, event):
        self.send_presence()
        self.plugin['xep_0045'].joinMUC(self.room,
                                        self.nick,
                                        wait=True)
        LOG.info("{} started 'Ask a librarian' chat room."
                 .format(self.nick))

xmpp = MUCBot("biblibothekar@xmpp.{}".format(LSB_DOMAIN),
              pickle.load(open("/usr/local/bin/.password", "r")),
              "ask_a_librarian@conference.{}".format(LSB_DOMAIN),
              "Bibli Bot Hekar")

xmpp.register_plugin('xep_0045')

if xmpp.connect():
    xmpp.process(block=True)
else:
    sys.exit(-2)
