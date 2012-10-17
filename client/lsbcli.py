#!/usr/bin/env python
# -*- coding: utf-8 -*-

#!/usr/bin/env python2 ## fucking arch

from __future__ import print_function
import os, getpass, time, signal, logging, sys
import subprocess, time
import webbrowser
from lsboo import tunnelmanager as tunnelmanager

if sys.version_info < (3, 0):
    reload(sys)
    sys.setdefaultencoding('utf8')
    import ConfigParser
else:
    import configparser as ConfigParser
    raw_input = input


#imports so pyinstaller can pick dependency

#import dns
#from dns.rdtypes.IN import *
#from dns.rdtypes.ANY import *

logging.basicConfig(filename = 'lsbcli.log', level = logging.DEBUG, format ='%(asctime)s: %(filename)s >> %(levelname)s - %(message)s')

lsb_version = open("lsb_version", "r").read()

lsb_ascii = """
.        .             .                   .              .
|       _|_ |          |                   |              |
|    .-. |   .--.  .--.|--. .-.  .--..-.   |.-.  .-.  .-. |.-. .--.
|   (.-' |   `--.  `--.|  |(   | |  (.-'   |   )(   )(   )|-.' `--.
'---'`--'`-' `--'  `--''  `-`-'`-'   `--'  '`-'  `-'  `-' '  `-`--'
"""

def capture_control_c(signal, frame):
    logging.debug("Got Control+C signal!")
    
    try:
        lsb.xmpp.kill_the_tunnel()
        lsb.xmpp.disconnect()
    except:
        logging.debug("Didn't kill the tunnel.")
    
    try:
        lsb.xmpp.kill_calibre_server()
    except:
        logging.debug("Didn't kill calibre.")

    sys.exit(0)

def update_status(signal, frame):
    global lsb_version
    logging.debug("Got signal: %s" % signal)

    if sys.platform.startswith("win"):
        subprocess.call(['cls'], shell=True)
    else:
        subprocess.call(['clear'])
    
    print(lsb_ascii)
    print("version: %s\n" % lsb_version)
    print(lsb.xmpp.get_status_message())
    print("To open URL in browser type 1, 2 or 3 and then [Enter] or 4 to exit:", end = " ")

if __name__=='__main__':
    lsbcli_pid = open("lsboo/lsbcli.pid","w")
    lsbcli_pid.write(str(os.getpid()))
    lsbcli_pid.close()

    signal.signal(signal.SIGINT, capture_control_c)
    if not sys.platform.startswith("win"):
        signal.signal(signal.SIGUSR1, update_status)

    lsb_config = ConfigParser.SafeConfigParser()

    if os.path.exists("lsbcli.conf"):
        lsb_config.read("lsbcli.conf")
    else:
        lsb_config.add_section('xmppconfig')
        lsb_config.set('xmppconfig', 'jid', raw_input("Username: "))
        lsb_config.set('xmppconfig', 'password', getpass.getpass("Password: "))
        lsb_config.set('xmppconfig', 'nick', raw_input("Nick: "))
        lsb_config.set('xmppconfig', 'room', "letssharebooks@conference.jabber.snipdom.net")
        lsb_config.set('xmppconfig', 'lsbbot', "lsbbot@jabber.snipdom.net")
       
        if sys.platform.startswith("lin"):
            lsb_config.add_section('calibreconfig')
            calibre_path = subprocess.Popen(['which', 'calibre-server'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
            calibre_path = calibre_path.communicate()[0][:-1]
            if calibre_path == "":
                calibre_path = "unknown"
            lsb_config.set('calibreconfig', 'calibre-server', calibre_path)

        elif sys.platform.startswith("win"):
            lsb_config.add_section('calibreconfig')
            try:
                calibre_path = "C:\Program Files\calibre2\calibre-server.exe"
                check_calibre = subprocess.Popen([calibre_path, '--version'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                if not check_calibre.communicate()[0].startswith("calibre"):
                    calibre_path = "unknown"
            except:
                calibre_path = "unknown"

            lsb_config.set('calibreconfig', 'calibre-server', calibre_path)

        elif sys.platform.startswith("dar"):
            lsb_config.add_section('calibreconfig')
            try:
                calibre_path = "/Applications/calibre.app/Contents/MacOS/calibre-server"
                check_calibre = subprocess.Popen([calibre_path, '--version'], stdout = subprocess.PIPE, stderr = subprocess.PIPE)
                if not check_calibre.communicate()[0].startswith("calibre"):
                    calibre_path = "unknown"
            except:
                calibre_path = "unknown"

            lsb_config.set('calibreconfig', 'calibre-server', calibre_path)

        lsb_config.set('calibreconfig', 'calibre-port', '3000')
        with open("lsbcli.conf", 'w') as fp:
            lsb_config.write(fp)

    lsb = tunnelmanager.LSBooks()
    lsb.setup_mucbot(lsb_config.get("xmppconfig", "jid"), lsb_config.get("xmppconfig", "password"), lsb_config.get("xmppconfig", "room"), lsb_config.get("xmppconfig","nick"), lsb_config.get("xmppconfig", "lsbbot"), lsb_config.get("calibreconfig", "calibre-server"), lsb_config.get("calibreconfig", "calibre-port"))

    if lsb.jabber_connect():
        if not sys.platform.startswith("win"):
            lsb.xmpp.start_calibre_server()
            time.sleep(2)
        lsb.xmpp.ask_for_slot()
    else:
        print("Didn't connect...")
        sys.exit(0)

    while True:
        def check_your_browser():
            print('\033[2A')
            print("Check your browser!\033[0K")
            time.sleep(2)
            print('\033[2A')
            if not sys.platform.startswith("win"):
                os.kill(int(open("lsboo/lsbcli.pid").read()), signal.SIGUSR1)
            else:
                update_status("windows", True)

        def open_in_browser(url):
            try:
                webbrowser.open(url)
            except:
                logging.debug("Strange webbrowser GConf Error")

        try:
            user_input = raw_input()
            #user_input = raw_input("To open URL in browser type 1, 2, 3 or 4 and then [Enter] or 5 to exit: ")
        except EOFError as err:
            logging.debug("Strange raw_input bug saying: %s" % err)
            user_input = "ut98awr"
        if user_input == "1":
            open_in_browser("https://%s" % lsb.xmpp.url)
            check_your_browser()
        elif user_input == "2":
            open_in_browser(lsb.xmpp.local_url)
            check_your_browser()
        elif user_input == "3":
            open_in_browser(lsb.xmpp.chat_url)
            check_your_browser()
        elif user_input == "4":
            os.kill(int(open("lsboo/lsbcli.pid").read()), signal.SIGINT)
        elif user_input == "ut98awr":
            pass
        else:
            print('\033[2A')
            print("Type only 1, 2, 3 or 4 and then [Enter]\033[0K")
            print('\033[2A')
            time.sleep(2)
        if sys.platform.startswith("win"):
            time.sleep(.4)
            update_status("windows", True)
        time.sleep(.1)
