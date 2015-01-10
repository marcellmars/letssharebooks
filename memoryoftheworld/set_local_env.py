#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

#------------------------------------------------------------------------------
#- getting ip addresses from dockers  -----------------------------------------

docker_ips = {}
for dckr in ["library", "mongodb", "nginx", "prosody", "sshd"]:
    docker_ips[dckr] = subprocess.check_output(["docker",
                                                "inspect",
                                                "-f",
                                                "'{{ .NetworkSettings.IPAddress }}'",
                                                "memoryoftheworld_{}_1".format(dckr)])[1:-2]

#------------------------------------------------------------------------------
#- add motw nginx ip address to  dnsmasq  -------------------------------------

dmsq = open("/etc/dnsmasq.d/local", "r").readlines()
init_pass = True
for n,d in enumerate(dmsq):
    if d.startswith("address=/memoryoftheworld.org/"):
        dmsq[n]="address=/memoryoftheworld.org/{}\n".format(docker_ips['nginx'])
        init_pass = False

if init_pass:
        dmsq.append("address=/memoryoftheworld.org/{}\n".format(docker_ips['nginx']))

open("/etc/dnsmasq.d/local", "w").writelines(dmsq)

#------------------------------------------------------------------------------
#- add motw docker lines to /etc/hosts  ---------------------------------------

hosts = open("/etc/hosts", "r").readlines()
for n,d in enumerate(hosts):
    if "memoryoftheworld.org" in d:
        hosts.pop(n)

for i in ["xmpp", "anon", "conference"]:
    hosts.append("{} {}.memoryoftheworld.org\n".format(docker_ips['prosody'], i))

hosts.append("127.0.0.1 memoryoftheworld.org\n")

open("/etc/hosts", "w").writelines(hosts)

#------------------------------------------------------------------------------
#- set/etc/resolv.conf to be handled by dnsmasq -------------------------------

open("/etc/resolv.conf", "w").write("nameserver 127.0.0.1\n")

#------------------------------------------------------------------------------
#- add iptables rule so remote/production motw server is blocked  -------------

subprocess.call('iptables -A INPUT -s 82.221.106.120/32 -m comment --comment motw -j DROP', shell=True)
subprocess.call(['service', 'dnsmasq', 'restart'])

