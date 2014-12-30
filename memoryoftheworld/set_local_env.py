#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
hosts = open("/etc/hosts", "r").readlines()
dmsq = open("/etc/dnsmasq.d/local", "r").readlines()
docker_ips = {}
for dckr in ["library", "mongodb", "nginx", "prosody", "sshd"]:
    docker_ips[dckr] = subprocess.check_output(["docker",
                                                "inspect",
                                                "-f",
                                                "'{{ .NetworkSettings.IPAddress }}'",
                                                "memoryoftheworld_{}_1".format(dckr)])[1:-2]

for n,d in enumerate(dmsq):
    if d.startswith("address="):
        dmsq[n]="address=/memoryoftheworld.org/{}\n".format(docker_ips['nginx'])

for n,d in enumerate(hosts):
    for i in ["xmpp", "anon", "conference"]:
        if "{}.memoryoftheworld.org".format(i) in d:
            hosts[n] = "{} {}.memoryoftheworld.org\n".format(docker_ips['prosody'], i)

open("/etc/hosts", "w").writelines(hosts)
open("/etc/dnsmasq.d/local", "w").writelines(dmsq)
open("/etc/resolv.conf", "w").write("nameserver 127.0.0.1\n")
subprocess.call(['service', 'dnsmasq', 'restart'])

