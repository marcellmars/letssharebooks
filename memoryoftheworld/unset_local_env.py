#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

#------------------------------------------------------------------------------
#- remove all motw iptables rules  --------------------------------------------

rules = subprocess.check_output(['iptables', '-S'])
for rule in rules.split("\n"):
    if "motw" in rule:
        subprocess.call('iptables {}'.format(rule.replace("-A", "-D")), shell=True)

#------------------------------------------------------------------------------
#- remove all motw lines from /etc/hosts  -------------------------------------

hosts = open("/etc/hosts", "r").readlines()

hosts_lines = []
for host in hosts:
    if "memoryoftheworld.org" not in host:
        hosts_lines.append(host)

open("/etc/hosts", "w").writelines(hosts_lines)

#------------------------------------------------------------------------------
#- set /etc/resolv.conf back to external dns  ---------------------------------
#---* some systems will bring back (127.0.0.1) when dnsmasq restarts ----------

open("/etc/resolv.conf", "w").write("nameserver 8.8.8.8\n")

#------------------------------------------------------------------------------
#- remove motw docker line from /etc/dnsmasq.d/local  -------------------------

dmsq = open("/etc/dnsmasq.d/local", "r").readlines()
dms_lines = []
for dms in dmsq:
    if not dms.startswith("address=/memoryoftheworld.org/"):
        dms_lines.append(dms)

open("/etc/dnsmasq.d/local", "w").writelines(dms_lines)
subprocess.call(['service', 'dnsmasq', 'restart'])
