import socket
import json
import requests
import grequests
import pickle
import time
import os

pports = []

LSB_DOMAIN = os.getenv("LSB_DOMAIN") or 'memoryoftheworld.org'


def check_tunnel_ports(ports):
    tp = []
    reqs = [grequests.get("http://www{}.{}/favicon.ico".format(port,
                                                               LSB_DOMAIN),
                          timeout=4) for port in ports]
    rs = grequests.map(reqs, exception_handler=None)
    for n, i in enumerate(rs):
        if i:
            if i.ok:
                tp.append(ports[n])
    print("GET TUNNEL ()PORTS CHECKED): {}".format(ports))
    return tp


def get_tunnel_ports():
    global pports
    data = {'get': 'active_tunnel_ports'}
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('sshd', 3773))
    s.send(json.dumps(data))
    ports = []
    data = ""
    while True:
        rdata = s.recv(8192)
        if rdata:
            data += rdata
        else:
            try:
                data = json.loads(data)
                ports = check_tunnel_ports(list(data))
            except Exception as e:
                print("Exception: {}\n data, rdata: {}, {}".format(e,
                                                                   data,
                                                                   rdata))
            break
    s.close()

    if pports != ports:
        pports = ports
        try:
            requests.get("http://localhost:4321/ping_autocomplete")
        except Exception as e:
            print("ping_autocomplete failed! {}".format(e))
    return ports

while True:
    ports = get_tunnel_ports()
    pickle.dump(ports, open("/tmp/active_tunnel_ports", "wb"))
    time.sleep(7)
