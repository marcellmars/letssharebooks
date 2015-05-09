import local_env as G

LSBM = '/letssharebooks/memoryoftheworld/'
for i in ["docker-compose", "calibre"]:
    with open("{}{}{}_template.yml".format(G.MOTW_HOME, LSBM, i)) as f:
        with open("{}{}{}.yml".format(G.MOTW_HOME, LSBM, i), "w") as g:
            g.write(f.read().replace('''${MOTW_HOME}''',
                                     G.MOTW_HOME)
                            .replace('''${MOTW_PERSISTENCE}''',
                                     G.MOTW_PERSISTENCE)
                            .replace('''${MOTW_WORDPRESS_HOME}''',
                                     G.MOTW_WORDPRESS_HOME)
                            .replace('''${RSYNC_DIRECTORY}''',
                                     G.RSYNC_DIRECTORY))
