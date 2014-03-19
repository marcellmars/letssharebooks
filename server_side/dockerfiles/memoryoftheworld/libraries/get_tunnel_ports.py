import subprocess
import requests
import time
import pickle
import argparse


def get_tunnel_ports(login="tunnel"):
    uid = subprocess.check_output(["grep", "{0}".format(login), "/etc/passwd"]).split()[0].split(":")[2]
    return subprocess.check_output(["sh", "/usr/local/bin/get_tunnel_ports.sh", uid]).split()

def main(prefix, host):
    tp = []
    for port in get_tunnel_ports():
        try:
            r = requests.get("{prefix}www{port}.{host}".format(prefix=prefix, port=str(port), host=host))
            if r.ok:
                tp.append(int(port))
        except:
            pass
    pickle.dump(tp, open("/tmp/active_tunnel_ports","wb"))

LSB_ENV = {
    'live' : {
        'prefix': 'https://',
        'host': 'memoryoftheworld.org'
    },
    'docker' : {
        'prefix': 'http://',
        'host': 'web.dokr'
    }
}

parser = argparse.ArgumentParser(description='get active lsb tunnels')
parser.add_argument('--env', help="server environment (live|docker)", default='docker')
args = parser.parse_args()

while True:
    time.sleep(10)
    main(LSB_ENV[args.env]['prefix'], LSB_ENV[args.env]['host'])
