#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess

open("/etc/resolv.conf", "w").write("nameserver 8.8.8.8\n")
subprocess.call(['iptables', '-D', 'INPUT', '-s', '82.221.106.120', '-j', 'DROP'])
subprocess.call(['service', 'dnsmasq', 'restart'])

