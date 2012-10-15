#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys,os
import time
import logging
import getpass
from optparse import OptionParser
import subprocess
import inspect
import signal

import sleekxmpp
from sleekxmpp.exceptions import IqError, IqTimeout

# add current path from running script. by http://stackoverflow.com/users/99834/sorin 
cmd_folder = os.path.abspath(os.path.split(inspect.getfile( inspect.currentframe() ))[0])
if cmd_folder not in sys.path:
    sys.path.insert(0, cmd_folder)

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
else:
    raw_input = input

logging.basicConfig(filename = 'letssharebooks.log', level = logging.DEBUG, format ='%(asctime)s: %(filename)s >> %(levelname)s - %(message)s')

class MUCBot(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, room, nick, lsbbot, calibre_path, calibre_port):
        sleekxmpp.ClientXMPP.__init__(self, jid, password)

        
        killing_pid = subprocess.Popen(['rm', '%s/calibre.pid' % cmd_folder], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        logging.debug("cmd_folder: %s" % cmd_folder)
        logging.debug("Deleting calibre.pid: %s" % str(killing_pid.communicate()))

        self.lsbbot = lsbbot
        self.room = room
        self.nick = nick
        self.ssh_proc = None
        self.running_tunnel = False

        self.calibre_path = calibre_path
        self.calibre_port = calibre_port

        self.url = ""
        self.local_url = "http://localhost:%s" % self.calibre_port
        self.chat_url = "https://jabber.snipdom.net/chat/example"
        self.status = ""

        self.add_event_handler("session_start", self.join_server)
        self.add_event_handler("failed_auth", self.check_credentials)
        self.add_event_handler("session_end", self.lost_connection)
        self.add_event_handler("message", self.message)
    
    def get_status_message(self):
        self.status_message = "[1] Your temporary public URL: https://%s\033[0K\n[2] Your local URL: %s\033[0K\n[3] Let's chat while we share: %s\033[0K\n[4] Shutdown session\033[0K\nSTATUS: %s\033[0K\n" % (self.url, self.local_url, self.chat_url, self.status)
        return self.status_message

    def send_status_message(self, message):
        self.status = message
        os.kill(int(open(cmd_folder + "/../lsbcli.pid").read()), signal.SIGUSR1)
        # preparation for pyinstaller
        #os.kill(int(open("lsbcli.pid").read()), signal.SIGUSR1)

    def check_credentials(self, event):
        logging.debug("Authorization failed. Check your credentials!")
        self.send_status_message("Authorization failed. Check your username and password.")
        self.disconnect()

    def lost_connection(self, event):
        logging.debug("session_end event triggered!")
        self.send_status_message("Lost the connection.")
 
    def join_server(self, event):
        logging.debug("session_start event triggered!")
        self.send_presence()
        try:
            self.get_roster()
        except IqError:
            logging.error("There was an error getting the roster: %s" % IqError.iq['error']['condition'])
            self.disconnect()
        except IqTimeout:
            logging.error("Timeout. Server is taking too long too respond")
            self.send_status_message("Authorization failed. Check your username and password.")
            os.kill(int(open(cmd_folder + "/../lsbcli.pid").read()), signal.SIGUSR1)
            self.disconnect()

    def message(self, msg):
        if msg['type'] in ('chat', 'normal') and msg['body'].startswith("__free_slot__"):
            logging.debug("Received __free_slot__: %s" % msg)
            prefix, self.ssh_user, self.url, self.ssh_port = msg['body'].split(",")
            self.start_the_tunnel()

        if msg['type'] in ('chat', 'normal') and msg['body'].startswith("__no_free_slot__"):
            logging.debug("Received __no_free_slot__: %s" % msg['body'].split(",")[1])

    def generate_key(self):
        keygen_check = subprocess.check_call('''rm -f letssharebooks.key*; ssh-keygen -q -t rsa -b 2048 -N "" -f letssharebooks.key''', shell = True)
        if keygen_check != 0: logging.debug("Generating SSH key failed. :(")
        self.public_key = open("letssharebooks.key.pub", "r").read()
        return self.public_key

    def ask_for_slot(self):
        self.generate_key()
        self.send_message(mto = self.lsbbot, mbody = "__ask_for_slot__,%s" % self.public_key, mtype = 'chat')
        self.send_status_message("Asking for free slot on server.")

    def start_the_tunnel(self):
        if not self.ssh_proc:
            self.ssh_proc = subprocess.Popen(['ssh', '-g', '-o', 'StrictHostKeyChecking=no', '-o', 'UserKnownHostsFile=.userknownhostsfile', '-o', 'TCPKeepAlive=yes', '-o', 'ServerAliveInterval=60', '-i', 'letssharebooks.key', '-NR', ':%s:localhost:%s' % (self.ssh_port, self.calibre_port), '%s@jabber.snipdom.net' % self.ssh_user], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        #time.sleep(2)
        self.running_tunnel = True
        lsbappid = open("lsbapp.pid", "w")
        lsbappid.write(str(self.ssh_proc.pid))
        lsbappid.close()
        #stdout, stderr = self.ssh_proc.communicate()
        #logging.debug("Establishing SSH erros: %s, %s" % (str(stdout), str(stderr)))
        self.send_message(mto = self.lsbbot, mbody = "__got_the_slot__,%s" % self.ssh_user, mtype = 'chat')
        self.send_status_message("Tunnel established.")
    
    def kill_the_tunnel(self):
        self.ssh_proc.kill()
        self.ssh_proc = None
        self.running_tunnel = False
        subprocess.Popen(['rm', '-f', 'lsbapp.pid'])
        self.send_message(mto = self.lsbbot, mbody = "__killed_the_slot__,%s" % self.public_key, mtype = 'chat')

    def start_calibre_server(self):
        self.calibre_proc = subprocess.Popen([self.calibre_path, '-p', self.calibre_port, '--max-cover=300x400', '--pidfile=%s/calibre.pid' % cmd_folder, '--daemonize'], stdin = subprocess.PIPE, stdout = subprocess.PIPE, stderr = subprocess.STDOUT)
        stdout = self.calibre_proc.communicate()
        logging.debug("Calibre server process: stdout/stderr: %s" % str(stdout))
        logging.debug("Calibre server running on port %s" % str(self.calibre_port))
        self.send_status_message("Calibre server running on port %s" % str(self.calibre_port))
    
    def kill_calibre_server(self):
        killing_calibre = subprocess.Popen(['kill', open("%s/calibre.pid" % cmd_folder).read()], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        logging.debug("Killing calibre after shutting down: %s" % str(killing_calibre.communicate()))
        deleting_calibre = subprocess.Popen(['rm', '%s/calibre.pid' % cmd_folder], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
        logging.debug("Deleting calibre.pid: %s" % str(deleting_calibre.communicate()))

class LSBooks:

    def setup_mucbot(self, jid, password, room, nick, lsbbot, calibre_path, calibre_port):
        self.xmpp = MUCBot(jid, password, room, nick, lsbbot, calibre_path, calibre_port)

        self.xmpp.register_plugin('xep_0030') # Service Discovery
        self.xmpp.register_plugin('xep_0199') # XMPP Ping

    def jabber_connect(self):
        if self.xmpp.connect():
            self.xmpp.process(block=False)
            logging.info("Connected to %s as %s" % (self.xmpp.room, self.xmpp.nick))
            return True
        else:
            logging.debug("Unable to connect to %s as %s" % (self.xmpp.room, self.xmpp.nick))
            return False
