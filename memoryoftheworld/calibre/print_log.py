#!/usr/bin/python

import tailer
import sys
import time
import os

while True:
    if os.path.isfile('/tmp/letssharebooks_debug.log'):
        break
    time.sleep(0.1)

for line in tailer.follow(open('/tmp/letssharebooks_debug.log')):
    sys.stderr.write(line+"\n")
    sys.stderr.flush()
