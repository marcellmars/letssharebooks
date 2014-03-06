import subprocess
import requests
import time
import pickle

def get_tunnel_ports(login="tunnel"):
    uid = subprocess.check_output(["grep", "{0}".format(login), "/etc/passwd"]).split()[0].split(":")[2]
    return subprocess.check_output(["/usr/local/bin/get_tunnel_ports.sh", uid]).split()

def main():
    tp = []
    for port in get_tunnel_ports():
        try:
            r = requests.get("{prefix}www{port}.{host}".format(prefix=PREFIX, port=str(port), host=HOST))
            if r.ok:
                tp.append(int(port))
        except:
            pass
    pickle.dump(tp, open("/tmp/active_tunnel_ports","wb"))

PREFIX = "http://"
#PREFIX = "https://"
HOST = "web.dokr"
#HOST = "memoryoftheworld.org"
#HOST = "memories.the-nsa.org"

while True:
    time.sleep(10)
    main()
