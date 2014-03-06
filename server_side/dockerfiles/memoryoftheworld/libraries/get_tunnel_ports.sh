#!/bin/sh

ss -4el|grep uid:$1|cut -d ":" -f 2|cut -d " " -f 1
