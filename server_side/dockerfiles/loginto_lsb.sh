#!/bin/sh

lxc-attach -n `docker ps -notrunc|grep librarian/library|cut -d " " -f 1`
