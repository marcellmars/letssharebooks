#!/usr/bin/python

MOTW_HOME="/home/m/devel"
MOTW_PERSISTENCE="/home/mnt/docker-persistence"

for i in ["fig", "calibre"]:
    with open("{}/letssharebooks/memoryoftheworld/{}_template.yml".format(MOTW_HOME, i)) as f:
        with open("{}/letssharebooks/memoryoftheworld/{}.yml".format(MOTW_HOME, i), "w") as g:
            g.write(f.read().replace('''${MOTW_HOME}''', MOTW_HOME)
                            .replace('''${MOTW_PERSISTENCE}''', MOTW_PERSISTENCE))
