#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

hosts = open("/etc/hosts", "r").readlines()

hosts_lines = []
for host in hosts:
    if "memoryoftheworld.org" not in host:
        hosts_lines.append(host)

open("/etc/hosts", "w").writelines(hosts_lines)
open("/etc/resolv.conf", "w").write("nameserver 8.8.8.8\n")

rules = subprocess.check_output(['iptables', '-S'])
for rule in rules.split("\n"):
    if "motw" in rule:
        subprocess.call('iptables {}'.format(rule.replace("-A", "-D")), shell=True)

subprocess.call(['service', 'dnsmasq', 'restart'])

