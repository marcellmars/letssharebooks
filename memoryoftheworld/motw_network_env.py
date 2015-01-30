#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys

def get_docker_ips():
    #------------------------------------------------------------------------------
    #- getting ip addresses from dockers  -----------------------------------------

    docker_ips = {}
    for dckr in ["library", "mongodb", "nginx", "prosody", "sshd"]:
        docker_ips[dckr] = subprocess.check_output(["docker",
                                                    "inspect",
                                                    "-f",
                                                    "'{{ .NetworkSettings.IPAddress }}'",
                                                    "memoryoftheworld_{}_1".format(dckr)])[1:-2]

    return docker_ips

def status():
    docker_ips = get_docker_ips()

    dmsq = [l for l in open("/etc/dnsmasq.d/local", "r").readlines()
            if "address=/memoryoftheworld.org/" in l]
    
    hosts = [l for l in open("/etc/hosts", "r").readlines()
             if "memoryoftheworld.org" in l]

    resolv_conf = [l for l in open("/etc/resolv.conf", "r").readlines()
                   if not "nameserver 127.0.0.1" in l]

    if dmsq and hosts and not resolv_conf:
        print("https://www.memoryoftheworld.org is set to LOCAL environment.")
    elif not dmsq and not hosts and "nameserver 8.8.8.8" in resolv_conf[0]:
        print("https://www.memoryoftheworld.org is set to REMOTE environment.")
    else:
        print("https://www.memoryoftheworld.org is neither set to \
        LOCAL nor REMOTE environment. Good luck!")

    for docker_ip in docker_ips.items():
        print("{}: {}".format(docker_ip[0], docker_ip[1]))

def set_local_env():
    docker_ips = get_docker_ips()
    
    #------------------------------------------------------------------------------
    #- add motw nginx ip address to  dnsmasq  -------------------------------------

    dmsq = open("/etc/dnsmasq.d/local", "r").readlines()

    init_address = True
    init_docker = True

    for n,d in enumerate(dmsq):
        if d.startswith("address=/memoryoftheworld.org/"):
            dmsq[n]="address=/memoryoftheworld.org/{}\n".format(docker_ips['nginx'])
            init_address = False
        if d.startswith("interface=docker0"):
            init_docker = False

    if init_address:
        dmsq.append("address=/memoryoftheworld.org/{}\n".format(docker_ips['nginx']))

    if init_docker:
        dmsq.append("interface=docker0\n")

    open("/etc/dnsmasq.d/local", "w").writelines(dmsq)

    #------------------------------------------------------------------------------
    #- add motw docker lines to /etc/hosts  ---------------------------------------

    hosts = open("/etc/hosts", "r").readlines()
    for n,d in enumerate(hosts):
        if "memoryoftheworld.org" in d:
            hosts.pop(n)

    for i in ["xmpp", "anon", "conference"]:
        hosts.append("{} {}.memoryoftheworld.org\n".format(docker_ips['prosody'], i))

    hosts.append("{} memoryoftheworld.org\n".format(docker_ips['sshd']))

    open("/etc/hosts", "w").writelines(hosts)

    #------------------------------------------------------------------------------
    #- set/etc/resolv.conf to be handled by dnsmasq -------------------------------

    open("/etc/resolv.conf", "w").write("nameserver 127.0.0.1\n")

    #------------------------------------------------------------------------------
    #- add iptables rule so remote/production motw server is blocked  -------------

    subprocess.call('iptables -A INPUT -s 82.221.106.120/32 -m comment --comment motw -j DROP', shell=True)
    subprocess.call(['service', 'dnsmasq', 'restart'])

def unset_local_env():
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
        if not dms.startswith("address=/memoryoftheworld.org/") \
           and not dms.startswith("interface=docker0"):
            dms_lines.append(dms)

    open("/etc/dnsmasq.d/local", "w").writelines(dms_lines)
    subprocess.call(['service', 'dnsmasq', 'restart'])


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "on":
            set_local_env()
            status()
        elif sys.argv[1] == "off":
            unset_local_env()
            status()
        elif sys.argv[1] == "status":
            status()
    else:
        print("Usage: {} on|off|status".format(sys.argv[0]))

