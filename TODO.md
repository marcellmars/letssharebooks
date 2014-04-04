**TODO**
- - -
[TOC]

# [let's share books] Calibre plugin

- add md5 checksums for every book in library
- finish all the dance with librarian name (if name changed update librarian on library.memoryoftheworld.org etc.)
- check if editing a book gets noticed and propagated to server

# library.memoryoftheworld.org

- provide offline view with librarian nicknames
- make a webpage per nickname-library_uuid for messages from other librarians
- find metadata from open library
- find links for books with md5 on libgen.org
- finish search with librarian name filter
- get librarian name together with related link below the cover

# portable library
- replace all hardcoded paths in templates with variables so portable could ignore them by setting them to empty strings:
  - in index.html: 
    - DONE_book_ parts_tmpl:
      - /get/ + book.application_id
    - DONE_book_content_tmpl:
      - /get/cover + book.application_id
      - /get/opf + book.application_id + " " + book_title_stripped
    - DONE_book_modal_tmpl
      - /get/cover + book.application_id
      - /get/opf + book.application_id + " " + book_title_stripped
- get rid of visit librarian (maybe just adding portable.css with directive `display:none`)
- sync libraries.js and other files with the version in libraries/ so we don't have to maintain more than one
