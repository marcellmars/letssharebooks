#!/usr/bin/env python

import subprocess
import json
import SocketServer


def get_tunnel_ports(login="tunnel"):
    tunnel_uid = subprocess.check_output(["grep", "^{0}:"
                                          .format(login),
                                          "/etc/passwd"]).split()[0].split(":")[2]
    active_tunnel_ports = [n.split(":")[1].split(" ")[0]
                           for n in subprocess.check_output(['ss', '-4el']).split('\n')
                           if n.find('uid:{} '.format(tunnel_uid)) != -1]

    print("active tunnel ports: {}".format(active_tunnel_ports))
    return active_tunnel_ports


class MyTCPServer(SocketServer.ThreadingTCPServer):
    allow_reuse_address = True


class MyTCPServerHandler(SocketServer.BaseRequestHandler):
    def handle(self):
        try:
            data = json.loads(self.request.recv(1024).strip())
            self.request.sendall(json.dumps(get_tunnel_ports()))
            #self.request.sendall(json.dumps([123,345,456]))
        except Exception, e:
            print("Upss:", e)

server = MyTCPServer(('0.0.0.0', 3773), MyTCPServerHandler)
server.serve_forever()
