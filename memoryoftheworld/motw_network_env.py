#!/usr/bin/env python
# -*- coding: utf-8 -*-

import subprocess
import sys
import local_env as G


LSB_DOMAIN = G.LSB_DOMAIN
MOTW_PUBLIC_IP = G.MOTW_PUBLIC_IP

DOCKERS = ["01 library",
           "02 mongodb",
           "03 nginx",
           "04 prosody",
           "05 sshd"]
           # "05 sshd",
           # "06 php5",
           # "07 db",
           # "08 rsync"]

ALIGN = max(map(len, DOCKERS)) - 3


def get_docker_ips():
    docker_ips = {}
    for dckr in DOCKERS:
        docker_ips[dckr] = subprocess.check_output(
            ["docker",
             "inspect",
             "-f",
             "'{{ .NetworkSettings.IPAddress }}'",
             "{}".format(dckr[3:])])[1:-2]

    return docker_ips


def get_docker_ids():
    docker_ids = {}
    for dckr in DOCKERS:
        docker_ids[dckr] = subprocess.check_output(
            ["docker",
             "inspect",
             "-f",
             "'{{ .Id }}'",
             "{}".format(dckr[3:])])[1:-2]

    return docker_ids


def status():
    docker_ips = get_docker_ips()
    # docker_ids = get_docker_ids()

    dmsq = [l for l in open("/etc/dnsmasq.d/local", "r").readlines()
            if "address=/{}/".format(LSB_DOMAIN) in l]

    hosts = [l for l in open("/etc/hosts", "r").readlines()
             if LSB_DOMAIN in l]

    resolv_conf = [l for l in open("/etc/resolv.conf", "r").readlines()
                   if not "nameserver 127.0.0.1" in l]

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    if dmsq and hosts and not resolv_conf:
        print("https://www.{} is set to LOCAL environment."
              .format(LSB_DOMAIN))
    elif not dmsq and not hosts and "nameserver 8.8.8.8" in resolv_conf[0]:
        print("https://www.{} is set to REMOTE environment."
              .format(LSB_DOMAIN))
    else:
        print("https://www.{} is neither set to "
              .format(LSB_DOMAIN)),
        print("LOCAL nor REMOTE environment. Good luck!")

    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")
    print("                                    {1:>{0}} {2} (ip)"
          .format(ALIGN,
                  "host",
                  "172.17.42.1"))
    print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")

    docker_ips = sorted([(key, value) for (key, value) in docker_ips.items()])
    for ip in docker_ips:
        if ip[1] == "":
            print("!!! {1:>{0}}  is not running !!!"
                  .format(ALIGN + 4,
                          ip[0][3:]))
            continue
        print("                                    {1:>{0}} {2} (ip)\n./motw_supervisorctl {1} status\ndocker exec -it {1} /bin/bash"
              .format(ALIGN,
                      ip[0][3:],
                      ip[1]))
                      # docker_ids[ip[0]][:8]))
        print("- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -")


def set_local_env(local=True):
    unset_local_env()
    docker_ips = get_docker_ips()

    #--------------------------------------------------------------------------
    #- add motw nginx ip address to  dnsmasq  ---------------------------------

    dmsq = open("/etc/dnsmasq.d/local", "r").readlines()

    init_address = True
    init_docker = True

    for n, d in enumerate(dmsq):
        if d.startswith("address=/{}/".format(LSB_DOMAIN)):
            dmsq[n] = "address=/{}/{}\n".format(
                LSB_DOMAIN,
                docker_ips['03 nginx'])
            init_address = False
        if d.startswith("interface=docker0"):
            init_docker = False

    if init_address:
        dmsq.append("address=/{}/{}\n".format(
            LSB_DOMAIN,
            docker_ips['03 nginx']))

    if init_docker:
        dmsq.append("interface=docker0\n")

    open("/etc/dnsmasq.d/local", "w").writelines(dmsq)

    #--------------------------------------------------------------------------
    #- add motw docker lines to /etc/hosts  -----------------------------------

    hosts = open("/etc/hosts", "r").readlines()
    for n, d in enumerate(hosts):
        if LSB_DOMAIN in d:
            hosts.pop(n)

    for i in ["xmpp", "anon", "conference"]:
        hosts.append("{} {}.{}\n".format(docker_ips['04 prosody'],
                                         i,
                                         LSB_DOMAIN))

    hosts.append("{} {}\n".format(docker_ips['05 sshd'],
                                  LSB_DOMAIN))
    # hosts.append("{} rsync.{}\n".format(docker_ips['08 rsync'],
    #                                     LSB_DOMAIN))

    open("/etc/hosts", "w").writelines(hosts)

    #--------------------------------------------------------------------------
    #- set/etc/resolv.conf to be handled by dnsmasq ---------------------------

    open("/etc/resolv.conf", "w").write("nameserver 127.0.0.1\n")

    if local:
        block_remote_production()


def block_remote_production():
    #--------------------------------------------------------------------------
    #- add iptables rule so remote/production motw server is blocked  ---------

    subprocess.call('iptables -A INPUT -s {} -m comment --comment motw -j DROP'
                    .format(MOTW_PUBLIC_IP),
                    shell=True)
    subprocess.call(['service', 'dnsmasq', 'restart'])


def unset_local_env():
    #--------------------------------------------------------------------------
    #- remove all motw iptables rules  ----------------------------------------

    rules = subprocess.check_output(['iptables', '-S'])
    for rule in rules.split("\n"):
        if "motw" in rule:
            subprocess.call('iptables {}'.format(rule.replace("-A", "-D")),
                            shell=True)

    #--------------------------------------------------------------------------
    #- remove all motw lines from /etc/hosts  ---------------------------------

    hosts = open("/etc/hosts", "r").readlines()

    hosts_lines = []
    for host in hosts:
        if LSB_DOMAIN not in host:
            hosts_lines.append(host)

    open("/etc/hosts", "w").writelines(hosts_lines)

    #--------------------------------------------------------------------------
    #- set /etc/resolv.conf back to external dns  -----------------------------
    #---* some systems will bring back (127.0.0.1) when dnsmasq restarts ------

    open("/etc/resolv.conf", "w").write("nameserver 8.8.8.8\n")

    #--------------------------------------------------------------------------
    #- remove motw docker line from /etc/dnsmasq.d/local  ---------------------

    dmsq = open("/etc/dnsmasq.d/local", "r").readlines()
    dms_lines = []
    for dms in dmsq:
        if not dms.startswith("address=/{}/".format(LSB_DOMAIN)) \
           and not dms.startswith("interface=docker0"):
            dms_lines.append(dms)

    open("/etc/dnsmasq.d/local", "w").writelines(dms_lines)
    subprocess.call(['service', 'dnsmasq', 'restart'])


if __name__ == '__main__':
    if len(sys.argv) > 1:
        if sys.argv[1] == "local":
            set_local_env(True)
            status()
        elif sys.argv[1] == "remote":
            unset_local_env()
            status()
        elif sys.argv[1] == "host":
            set_local_env(False)
            status()
        elif sys.argv[1] == "status":
            status()
    else:
        print("Usage: {} host | local | remote | status"
              .format(sys.argv[0]))
