view this document here: https://stackedit.io/viewer#!provider=gist&gistId=7547779&filename=PublicLibraryLocalSetup_no-docker.md

[TOC]


## Overview
### SSH tunneling
Calibre plugin **[let's share books]** establishes [SSH tunnel](#SSH) as a user **tunnel** with [SSH server](#SSH) through port 722 without authorization.

That allows local [Calibre content server][1] to get proxied through SSH tunnel and [Nginx](#Nginx) so Calibre content server can get its own public URL (i.e. https://www3493.memoryoftheworld.org). Local Calibre library is then accessible from the world to which Nginx is exposed. In production setup that's **memoryoftheworld.org**, in development setup that's usually only developer's laptop.

### Webapp unifying all proxied libraries
Calibre plugin **[let's share books]** collects all metadata about the books (in current Calibre library) and send it to webapp which then unifies all libraries into unique interface. 

Webapp shows all the books from libraries and enables search through all of them.
## Setup
### Adding user 'tunnel'

    sudo useradd -m -g users -s /bin/bash tunnel

then remove character **!** in **/etc/shadow** in line which looks like this:

    tunnel:!:16028:0:99999:7:::

it should then look like this:

    tunnel::16028:0:99999:7:::

### <a id="SSH"></a>SSH
make new configuration file **sshd_config_tunnel** in directory **/etc/ssh/**:

    UsePAM no
     AllowUsers tunnel
     Port 722

    Match User tunnel
     ForceCommand /bin/echo do-not-send-commands
     AllowTcpForwarding yes
     PasswordAuthentication yes
     PermitEmptyPasswords yes`

run ssh daemon with that configuration:

    sudo /usr/bin/sshd -D -f /etc/ssh/sshd_config_tunnel
### <a id="DNSMasq"></a>DNSMasq
*local domain name **dokr** is used because of original development setup with docker.io. it could be any name one prefers. this document covers setup without docker. everything is running in the same operating system session. if you use some other name check out the code and replace **dokr** instances accordingly*

if you use **dnsmasq** add line to **/etc/dnsmasq.conf**:

    address=/dokr/127.0.0.1
if you use **NetworkManager** add line to **/etc/NetworkManager/dnsmasq.d/local**:

    address=/dokr/127.0.0.1
restart dnsmasq daemon or NetworkManager.

### <a id="Nginx"></a>Nginx
make new configutation **lsb** file in **/etc/nginx/sites-available**:

    server {
                server_name   "~^www(?<port>\d{4,5}).web.dokr"
                listen 80;
                
                location / {
                    proxy_pass        http://127.0.0.1:$port;
                proxy_set_header  X-Real-IP  $remote_addr;
                    proxy_set_header  Host $host;
                }
    }

if you use **/etc/nginx/sites-available** for you configuration files you should add symlink to **/etc/nginx/sites-enabled**:

    cd /etc/nginx/sites-enabled
    sudo ln ../sites-available/lsb lsb
    
also check if you have this line in **/etc/nginx.conf**:

    http {
    ..
    include /etc/sites-enabled/*;
    ..
    }

run nginx as you run it on your linux distribution. i.e.:

    sudo systemctl start nginx
or
    
    sudo service nginx start

### <a id="get_tunnel_ports.sh"></a>get_tunnel_ports.sh
add **get_tunnel_ports.sh** shell script to **/usr/local/bin/**:

    #!/bin/sh
    
    ss -4el|grep uid:$1|cut -d ":" -f 2|cut -d " " -f 1

make it executable:

    sudo chmod +x /usr/local/bin/get_tunnel_port.sh

### Dependencies
1. http://calibre-ebook.com/download_linux
2. git clone https://github.com/marcellmars/letssharebooks
2. pip install cherrypy

[1]: http://www.thedustyblog.com/2012/05/calibrerunning-a-content-server/