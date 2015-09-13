#!/usr/bin/python

import tailer
import sys
import time
import os

LOG_FILE = sys.argv[1]

while True:
    if os.path.isfile(LOG_FILE):
        break
    time.sleep(0.5)

for line in tailer.follow(open(LOG_FILE)):
    sys.stderr.write(line+"\n")
    sys.stderr.flush()
