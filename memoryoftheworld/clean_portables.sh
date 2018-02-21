#!/bin/bash

# it rmoves all portables and then brings it back

PORTABLES=(
    biopolitics.memoryoftheworld.org
    economics.memoryoftheworld.org
    feminism.memoryoftheworld.org
    herman.memoryoftheworld.org
    kok.memoryoftheworld.org
    otpisane.memoryoftheworld.org
    midnightnotes.memoryoftheworld.org
    hortense.memoryoftheworld.org
    tamoneki.memoryoftheworld.org
    marcell.memoryoftheworld.org
    praxis.memoryoftheworld.org
    lib.discombobulated.systems
    badco.memoryoftheworld.org
    dubravka.memoryoftheworld.org
    anybody.memoryoftheworld.org
    quintus.memoryoftheworld.org
    slowrotation.memoryoftheworld.org
)

for i in ${PORTABLES[@]};
do
    curl -k https://library.memoryoftheworld.org/remove_portable\?url\=http://$i;
    #curl -k https://library.memoryoftheworld.org/remove_portable\?url\=https://$i;
    #curl -k https://library.memoryoftheworld.org/add_portable\?url\=https://$i;
    curl -k https://library.memoryoftheworld.org/add_portable\?url\=http://$i;
done
