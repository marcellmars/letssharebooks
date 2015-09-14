import local_env as G

LSBM = '/letssharebooks/memoryoftheworld/'
FILES = [["docker-compose", ".yml"],
         ["motw-compose", ".yml"],
         ["calibre", ".yml"],
         ["nginx/lsb_domains", ""]]

for i in FILES:
    with open("{}{}{}_template{}".format(G.MOTW_HOME, LSBM, i[0], i[1])) as f:
        with open("{}{}{}{}".format(G.MOTW_HOME, LSBM, i[0], i[1]), "w") as g:
            g.write(f.read().replace('''${MOTW_HOME}''',
                                     G.MOTW_HOME)
                            .replace('''${MOTW_PERSISTENCE}''',
                                     G.MOTW_PERSISTENCE)
                            .replace('''${MOTW_WORDPRESS_HOME}''',
                                     G.MOTW_WORDPRESS_HOME)
                            .replace('''${RSYNC_DIRECTORY}''',
                                     G.RSYNC_DIRECTORY)
                            .replace('''${LSB_DOMAIN}''',
                                     G.LSB_DOMAIN))
