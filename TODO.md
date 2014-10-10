**TODO**
- - -
[TOC]

get rid of this file and add all bullets to issues at github

# [let's share books] Calibre plugin

- add md5 checksums for every book in library
- check if there is already someone on server with the same librarian name
- check if editing a book gets noticed and propagated to server
- check on OSX if handling sslErros works on both calibre 1.x and 2.x
    - >> `netaccman.sslErrors.connect(self.sslErrorHandler)` (main.py:702)
 

# library.memoryoftheworld.org

- provide offline view with librarian nicknames
- make a webpage per nickname-library_uuid for messages from other librarians
- find metadata from open library
- find links for books with md5 on libgen.org
- finish search with librarian name filter
- get librarian name together with related link below the cover

# portable library
- get rid of "All librarians" and put librarian name without drop down manu
- get rid of visit librarian (maybe just adding portable.css with directive `display:none`)
- sync libraries.js and other files with the version in libraries/ so we don't have to maintain more than one
