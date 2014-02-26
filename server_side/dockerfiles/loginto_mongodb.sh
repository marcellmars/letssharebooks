#!/bin/sh

lxc-attach -n `docker ps -notrunc|grep librarian/mongodb|cut -d " " -f 1`
