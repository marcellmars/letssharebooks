<template>
    <div class="col col-xl-2 col-lg-3 col-md-4 col-sm-6 cols-12">
        <b-modal v-model="$store.state.showModal"
                 ref="bookModal"
                 size="lg"
                 no-fade
                 lazy
                 centered
                 @hidden="$emit('modalHidden')"
                 :title="getModalHeader(book)"
                 header-bg-variant="motwred"
                 footer-bg-variant="motwred"
                 header-text-variant="white"
                 footer-text-variant="white">
            <img :src="getCover(book)"
                 class="float-right pr-0 ml-2 mb-2 col-6"></img>

            <div class="key_par">Title:
                <span class="val_par">{{ book.title }}</span>
            </div>

            <div class="key_par">Authors:
                <span v-for="author in book.authors">
                <a href="#"
                   class="motw_table_link"
                   @click="searchByAuthor(author)">{{ author }}</a><span v-text="getEndComma(author)"></span>
                </span>
            </div>

            <div class="key_par" v-if="book.publisher">Publisher:
                <a href="#"
                   class="motw_table_link"
                   @click="searchByPublisher(book.publisher)">{{ book.publisher }}</a>
            </div>

            <div class="key_par" v-if="book.pubdate">Year:
                <span class="val_par">{{ book.pubdate.slice(0,4) }}</span>
            </div>

            <div class="key_par" v-if="book.formats">Download:
                <span class="val_par" v-html="getFormats(book)"></span>
            </div>
          
            <div class="key_par" v-if="book.comments">Description:
                <span class="val_par text-justify" v-html="cleanHtml(book.comments)"></span>
            </div>

            <div slot="modal-footer"
                 class="w-100">
                <a href="#"
                   class="float-left motw_table_link librarian_link"
                   @click="searchByLibrarian(book.librarian)" >
                    catalogued by {{ book.librarian }}
                </a>
            </div>
        </b-modal>
    </div>
</template>

<script>
    import 'font-awesome/css/font-awesome.css';
    import sanitizeHtml from "sanitize-html";
    import {
        eventBus
    } from '../main';

    export default {
        props: ['book'],
        methods: {
            cleanHtml(html_text) {
                return sanitizeHtml(html_text, {
                    allowedTags: ['a', 'abbr', 'acronym', 'b', 'blockquote', 'code', 'em', 'i', 'li', 'ol', 'ul', 'strong', 'br', 'div', 'p']
                }).replace('**', '');
            },
            getEndComma(author) {
                if (author === this.book.authors[this.book.authors.length - 1]) {
                    return
                } else {
                    return ", "
                }
            },
            getModalHeader(book) {
                if (book.hasOwnProperty('authors') === false) {
                    return
                }
                let authors = book.authors
                if (authors.length > 3) {
                    authors = book.authors.slice(0, 3)
                    authors.push("et al.")
                }

                return `"${book.title}" by ${authors.join(', ')}`
            },
            searchByAuthor(author) {
                this.$store.state.searchQuery = {
                    'endpoint': `/search/authors/${author}`,
                    'status': `author: ${author}`
                }
                this.$refs.bookModal.hide()
            },
            searchByLibrarian(librarian) {
                this.$store.state.searchQuery = {
                    'endpoint': `/search/librarian/${librarian}`,
                    'status': `librarian: ${librarian}`
                }
                this.$refs.bookModal.hide()
            },
            searchByPublisher(publisher) {
                this.$store.state.searchQuery = {
                    'endpoint': `/search/publisher/${publisher}`,
                    'status': `publisher: ${publisher}`
                }
                this.$refs.bookModal.hide()
            },

            getFormats(book) {
                let f = '';
                for (let frm of book['formats']) {
                    let book_url = book.library_url + frm.dir_path + frm.file_name
                    let download_stripe = `<a class="motw_table_link" href="${book_url}">.${frm.format}</a>, `;
                    f += download_stripe;
                }
                return f.slice(0, -3)
            },
            getCover(book) {
                return book.library_url + book.cover_url
            }
        }
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

    .card-text {
        width: 100%;
        position: absolute;
        bottom: 0;
    }

    .key_par {
        font-weight: bold;
        padding-bottom: 0.5em;
    }

    .val_par {
        font-weight: normal;
    }

    .librarian_link {
        color: white;
    }
</style>