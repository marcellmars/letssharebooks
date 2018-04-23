<template>
    <div class="col col-xl-2 col-lg-3 col-md-4 col-sm-6 col-12">
        <b-card overlay
                class="h-100"
                :img-src="getCover(book)"
                :img-alt="book.title"
                text-variant="white">
            <div class="book-header">
            <b-card-body class="card-title">
                <a href="#"
                   @click="titleClick(book)"
                   class="motw_link">
                    {{ book.title }}
                </a>
            </b-card-body>
            <b-card-body class="card-subtitle">
                <a href="#"
                   class="motw_link"
                   v-for="author in book.authors"
                   @click="search('authors', author)"
                   v-text="getEndComma(author)">
                </a>
            </b-card-body>
            </div>
            <div class="card-text"
                 v-html="getFormats(book)">
            </div>
        </b-card>
    </div>
</template>

<script>
 import {
     eventBus
 } from '../main';

 export default {
     props: ['book'],
     methods: {
         titleClick(book) {
             this.$emit('titleClick', book)
         },
         getEndComma(author) {
             if (author === this.book.authors[this.book.authors.length - 1]) {
                 return author
             } else {
                 return `${author}, `
             }
         },
         getModalHeader(book) {
             let authors = ""
             for (let author of book.authors) {
                 authors += this.getEndComma(author)
             }
             return `"${book.title}" by ${authors}`
         },
         search(field, query) {
             this.$store.state.searchQuery = {
                 'endpoint': `/search/${field}/${query}`,
                 'status': `${field}: ${query}`
             }
             eventBus.$emit('reloadSearch')
         },
         getFormats(book) {
             let f = '';
             for (let frm of book['formats']) {
                 let book_url = book.library_url + frm.dir_path + frm.file_name
                 let download_stripe = `<a class="motw_link" href="${book_url}"><img src="static/download.svg" class="download-disk" /><i>${frm.format.toUpperCase()}</i></a>, `;
                 f += download_stripe;
             }
             return f.slice(0, -3)
         },
         getCover(book) {
             return book.library_url + book.cover_url
         }
     },
 }
</script>

<style scoped>
    .col {
        padding-left: 2px;
        padding-right: 2px;
        padding-bottom: 2px;
        padding-top: 2px;
    }

    .card-body {
        padding: 0px;
    }

    .card-text,
    .card-title,
    .card-subtitle {
        font-weight: bold;
        font-size: 1.0em;
        background: black;
        margin: 0px;
        padding-top: 6px;
        padding-right: 3px;
        padding-left: 6px;
    }

    .card-title {
        font-size: 1.2em;
    }

    .card-subtitle {
        font-style: italic;
    }

    .book-header {
        margin: 0.5em 0 0 0
    }

    .card-text {
        width: 100%;
        position: absolute;
        bottom: 0;
    }

    .key_par {
        font-weight: bold;
    }

    .val_par {
        font-weight: normal;
    }

    .darrow {
        text-decoration: underline;
        font-weight: bold;
        font-size: 3em;
    }
</style>
