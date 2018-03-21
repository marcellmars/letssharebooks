<template>
    <div class="col col-xl-2 col-lg-3 col-md-4 col-sm-6 cols-12">
        <b-modal v-model="show_modal"
                 size="lg"
                 no-fade
                 :title="getModalHeader(book)"
                 header-bg-variant="danger"
                 footer-bg-variant="danger"
                 header-text-variant="white"
                 footer-text-variant="white">
            <img :src="getCover(book)"
                 class="float-right"
                 width="33%"></img>
            <div class="key_par">Title:
                <span class="val_par">{{ book.title }}</span>
            </div>

            <div class="key_par">Authors:
                <a href="#"
                   v-for="author in book.authors"
                   @click="searchByAuthor(author)"
                   v-text="getEndComma(author)">
                </a>
            </div>
            <div class="key_par">Publisher:
                <span class="val_par">{{ book.publisher }}</span>
            </div>
            <div class="key_par">Description:</div>
            <div v-html="book.comments"></div>
            <div slot="modal-footer"
                 class="w-100">
                <a href="#" class="float-left motw_link"
                   @click="searchByLibrarian(book.librarian)" >
                    catalogued by {{ book.librarian }}
                </a>
            </div>
        </b-modal>
    </div>
</template>

<script>
    import 'font-awesome/css/font-awesome.css'
    export default {
        props: ['book', 'show_modal'],
        methods: {
            getEndComma(author) {
                if (author === this.book.authors[this.book.authors.length - 1]) {
                    return author
                } else {
                    return `${author}, `
                }
            },
            getModalHeader(book) {
                let authors = ""
                if (book.hasOwnProperty('authors') === false) {
                    return
                }

                for (let author of book.authors) {
                    authors += this.getEndComma(author)
                }
                return `"${book.title}" by ${authors}`
            },
            searchByAuthor(author) {
                this.$emit('reloadSearch', {
                    'endpoint': `search/authors/${author}`,
                    'status': `author: ${author}`
                })
            },
            searchByLibrarian(librarian) {
                this.$emit('reloadSearch', {
                    'endpoint': `search/librarian/${librarian}`,
                    'status': `librarian: ${librarian}`
                })
            },
            getFormats(book) {
                let f = '';
                for (let frm of book['formats']) {
                    let book_url = book.library_url + frm.dir_path + frm.file_name
                    let download_stripe = `<a class="motw_link" href="${book_url}"><i class="fa fa-download"></i><i>${frm.format.toUpperCase()}</i></a>, `;
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
    }

    .val_par {
        font-weight: normal;
    }
</style>