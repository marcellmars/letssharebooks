<template>
  <div class="col col-xl-2 col-lg-3 col-md-4 col-sm-6 cols-12">
    <b-card overlay
      class="h-100"
      :img-src="getCover(book)"
      :img-alt="book.title"
      text-variant="white">
        <b-card-body class="card-title">
            <span @click="show_modal = !show_modal">{{ book.title }}</span>
        </b-card-body>
        <b-card-body class="card-subtitle">
            <span v-for="author in book.authors"
                  @click="searchQuery(author)"
                  v-text="getEndComma(author)">
            </span>
        </b-card-body>
        <div class="card-text"
             v-html="getFormats(book)">
        </div>
    </b-card>
    <b-modal v-model="show_modal"
             size="lg"
             no-fade
             :title="book.title"
             header-bg-variant="danger"
             footer-bg-variant="danger"
             header-text-variant="white"
             footer-text-variant="white">
        <img :src="getCover(book)" class="float-right" width="33%"></img>
        <div v-html="book.comments"></div>
        <div slot="modal-footer"
             class="w-100">
            <p class="float-left">catalogued by {{ book.library_uuid }}</p>
        </div>
    </b-modal>
  </div>
</template>

<script>
    import 'font-awesome/css/font-awesome.css'
    export default {
        props: ['book'],
        data() {
            return {
                show_modal: false,
            }
        },
        methods: {
            getEndComma(author) {
                if (author === this.book.authors[this.book.authors.length - 1]) {
                    return author
                } else {
                    return author + ", "
                }
            },
            searchQuery(author) {
                var sq = 'books/on?where=authors=="' + author + '"'
                this.$emit('reloadSearch', sq)
            },
            getFormats(book) {
                let f = '';
                for (var frm of book['formats']) {
                    var book_url = book.library_url + frm.dir_path + frm.file_name
                    var download_stripe = '<a class="motw_download" href="' + book_url + '"><i class="fa fa-download"></i><i>' + frm.format.toUpperCase() + '</i></a>, ';
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

    .card-text {
        width: 100%;
        position: absolute;
        bottom: 0;
    }
</style>
