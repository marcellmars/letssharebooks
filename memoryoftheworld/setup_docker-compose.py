import shutil
import os
import local_env as G

LSBM = '/letssharebooks/memoryoftheworld/'
FILES = [["docker-compose", ".yml"],
         ["motw-compose", ".yml"],
         ["motw-wordpress", ".yml"],
         ["calibre_docker", ".yml"],
         ["nginx/lsb_domains", ""],
         ["nginx/static_web/candy/index", ".html"],
         ["nginx/static_web/candy/calibre", ".html"]]


#------------------------------------------------------------------------------
#- FILES are templates which should be preprocessed before any deployment -----

for i in FILES:
    with open("{}{}{}_template{}".format(G.MOTW_HOME, LSBM, i[0], i[1])) as f:
        with open("{}{}{}{}".format(G.MOTW_HOME, LSBM, i[0], i[1]), "w") as g:
            g.write(f.read().replace('''${MOTW_HOME}''',
                                     G.MOTW_HOME)
                            .replace('''${MOTW_PERSISTENCE}''',
                                     G.MOTW_PERSISTENCE)
                            .replace('''${MYSQL_PASS}''',
                                     G.MYSQL_PASS)
                            .replace('''${MYSQL_USER}''',
                                     G.MYSQL_USER)
                            .replace('''${MOTW_WORDPRESS_HOME}''',
                                     G.MOTW_WORDPRESS_HOME)
                            .replace('''${MOTW_MEDIAWIKI_HOME}''',
                                     G.MOTW_MEDIAWIKI_HOME)
                            .replace('''${RSYNC_DIRECTORY}''',
                                     G.RSYNC_DIRECTORY)
                            .replace('''${LSB_DOMAIN}''',
                                     G.LSB_DOMAIN))

#------------------------------------------------------------------------------
#- crt and key file names should be the same as LSB_DOMAIN --------------------
#- nginx and prosody needs crt and key for ssl to work ------------------------

for docker in ["nginx", "prosody"]:
    os.remove("{}/lsb_domain.crt".format(docker))
    os.remove("{}/lsb_domain.key".format(docker))
    shutil.copy("secrets/{}.crt".format(G.LSB_DOMAIN),
                "{}/lsb_domain.crt".format(docker))
    shutil.copy("secrets/{}.key".format(G.LSB_DOMAIN),
                "{}/lsb_domain.key".format(docker))


#------------------------------------------------------------------------------
#- it is recommended for nginx to have dhparam.pem for better security --------

shutil.copy("secrets/dhparam.pem",
            "nginx/dhparam.pem")


#------------------------------------------------------------------------------
#- prosody changes dots in the name of directery.. aih ------------------------

with open("prosody/Dockerfile_template", "r") as f:
    with open("prosody/Dockerfile", "w") as g:
        d = "xmpp%2e{}%2e{}".format(".".join(G.LSB_DOMAIN.split(".")[:-1]),
                                    G.LSB_DOMAIN.split(".")[-1])
        g.write(f.read().replace('''${LSB_DOMAIN}''',
                                 d))
