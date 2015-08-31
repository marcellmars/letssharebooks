FROM librarian/motw

MAINTAINER Marcell Mars "https://github.com/marcellmars"

RUN  echo 'Acquire::http::Proxy "http://172.17.42.1:3142";' >> /etc/apt/apt.conf.d/01proxy

RUN apt-get update \
    && apt-get -y install php5-curl \
                          php5-gd \
                          php5-intl \
                          php-pear \
                          php5-imagick \
                          php5-imap \
                          php5-mcrypt \
                          php5-memcache \
                          php5-ming \
                          php5-ps \
                          php5-pspell \
                          php5-recode \
                          php5-snmp \
                          php5-sqlite \
                          php5-tidy \
                          php5-xmlrpc \
                          php5-xsl \
                          php5-fpm \
                          php5-mysql

# php-fpm config from https://github.com/eugeneware/docker-wordpress-nginx/blob/master/Dockerfile
RUN sed -i -e "s/upload_max_filesize\s*=\s*2M/upload_max_filesize = 100M/g" /etc/php5/fpm/php.ini \
    && sed -i -e "s/post_max_size\s*=\s*8M/post_max_size = 100M/g" /etc/php5/fpm/php.ini \
    && sed -i -e "s/;daemonize\s*=\s*yes/daemonize = no/g" /etc/php5/fpm/php-fpm.conf \
    && sed -i -e "s/^listen .*/listen = 0.0.0.0:9000/g" /etc/php5/fpm/pool.d/www.conf \
    && find /etc/php5/cli/conf.d/ -name "*.ini" -exec sed -i -re 's/^(\s*)#(.*)/\1;\2/g' {} \; \
    && rm /etc/php5/mods-available/snmp.ini

ADD php5.conf /etc/supervisor/conf.d/
