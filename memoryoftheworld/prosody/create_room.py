import sys
import logging
import sleekxmpp

if sys.version_info < (3,0):
    reload(sys)
    sys.setdefaultencoding('utf8')

class MucSetup(sleekxmpp.ClientXMPP):
    def __init__(self, jid, password, mucname):
        super(MucSetup,self).__init__(jid, password)
        self.room = mucname
        self.nick = 'muc_creator'

        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('muc::%s::got_online' % self.room, self.muc_online)

    def session_start(self, event):
        self.send_presence()
        self.get_roster()
        self.muc = self.plugin['xep_0045']
        self.muc.joinMUC(self.room,
                         self.nick)

    def muc_online(self, presence):

        print presence
        if presence['muc']['nick'] == self.nick:
            form = reparse_form(self.muc.getRoomConfig(self.room))
            print "=== FORM ===\n%s\n=== END FORM ===" % (form['fields'])
            for f in form.field:
                print "%40s\t%15s\t%s\n" % (f, form.field[f]['type'],form.field[f]['value'])
            form.field['muc#roomconfig_roomdesc']['value'] = "Script configured room"
            form.field['muc#roomconfig_persistentroom']['value'] = True
            form.field['muc#roomconfig_publicroom']['value'] = True
            form.field['muc#roomconfig_moderatedroom']['value'] = False
            form.set_type('submit')
            print "=== Return FORM ===\n%s\n=== END Return FORM ===" % str(form)
            self.muc.setRoomConfig(self.room, form)

            print "Receive presence for self.  Exiting."
            self.send_presence('offline')
            self.disconnect(wait=True)

##  Some XMPP forms are sent with xmlns="" in each field which causes the form
##  parsing to break (this is an XML serializer bug on the server).
##  Serializing the form again cleans out the xmlns="" attributes and allows
##  the normal xmlns inheritance rules to take over.  This function reparses
##  the form and allows it to work as expected according to XEP-0004.
def reparse_form(form):
    from sleekxmpp.xmlstream import ET
    #from sleekxmpp.plugins.xep_0004 import *
    x = ET.fromstring(str(form))
    return Form(xml=x)

if __name__ == '__main__':
    optp = OptionParser()

    optp.add_option('-d','--debug', help="Enable debugging",
                    action='store_const', dest='loglevel',
                    const=logging.DEBUG, default=logging.INFO)

    optp.add_option('-j','--jid', dest='jid', help='JID to login as')
    optp.add_option('-p','--password', dest='passwd', help='Login password')
    optp.add_option('-m','--muc', dest='muc', help='MUC to create')
    opts, args = optp.parse_args()

    if opts.jid is None:
        opts.jid = raw_input("JID: ")
    if opts.passwd is None:
        opts.passwd = raw_input("Password: ")
    if opts.muc is None:
        opts.muc = raw_input("MUC: ")

    logging.basicConfig(level=opts.loglevel, format='%(levelname)-9s %(message)s')

    xmpp = MucSetup(opts.jid, opts.passwd, opts.muc)
    xmpp.register_plugin('xep_0030')
    xmpp.register_plugin('xep_0045')
    xmpp.register_plugin('xep_0004')

    if xmpp.connect():
        xmpp.process(block=True)
    else:
        print "Unable to connect as %s" % opts.jid
