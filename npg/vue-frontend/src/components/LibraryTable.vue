<template>
    <div>
        <nav-bar :links="links"
                 :meta="meta"
                 @fetchBooks="fetchBooks($event)">
        </nav-bar>
        <book-modal :show_modal="show_modal"
                    :book="book"
                    @reloadSearch="fetchBooks($event)" />
        <b-table :items="books"
                 :fields="fields"
                 @row-clicked="rowClicked"
                 striped
                 hover
                 small>         
        </b-table>
        <nav-bar :links="links" :meta="meta" @fetchBooks="fetchBooks($event)">
        </nav-bar>
    </div>
</template>

<script>
    import NavBar from './NavBar.vue'
    import BookModal from './BookModal.vue'

    export default {
        data: function() {
            return {
                // books: LIBRARY.books.add
                books: [],
                fields: {
                    'authors': {
                        label: 'Authors',
                        formatter: 'authorsCommaSpace',
                        tdClass: 'btitle'
                    },
                    'title': {
                        label: 'Title',
                    },
                    'pubdate': {
                        label: 'Published',
                        formatter: 'publishedYear'
                    },
                    'formats': {
                        label: 'Download',
                        formatter: 'getFormats'
                    }

                },
                links: {
                    'next': false,
                    'prev': false
                },
                meta: {},
                show_modal: false,
                book: {}
            }
        },
        methods: {
            fetchBooks(a) {
                this.show_modal = false;
                let endpoint = a['endpoint']
                let status = a['status']
                // this.$http.get('static/data.js')
                this.$http.get(endpoint)
                    .then(response => {
                        return response.json()
                    })
                    .then(data => {
                        this.books = data._items;
                        this.meta = data._meta;
                        this.links = data._links;
                        this.meta['status'] = status
                    });
            },
            authorsCommaSpace(t) {
                return t.join(',<br/>')
            },
            publishedYear(d) {
                return `${d}`.slice(0, 4)
            },
            getFormats(key, value, book) {
                let f = '';
                for (let frm of book['formats']) {
                    let book_url = book.library_url + frm.dir_path + frm.file_name
                    let download_stripe = `<a class="motw_table_link" href="${book_url}"><i class="fa fa-download"></i><i>${frm.format.toUpperCase()}</i></a><br/>`;
                    f += download_stripe;
                }
                return f.slice(0, -3)
            },
            rowClicked(item, row, event) {
                this.book = item;
                if (event['path'][1].querySelectorAll('a').length == 0) {
                    this.show_modal = false;
                } else {
                    this.show_modal = true;
                }
            }
        },
        mounted: function() {
            this.fetchBooks({
                'endpoint': 'books',
                'status': 'all books'
            })
        },
        watch: {
            reloadSearch: function(val, oldVal) {
                this.fetchBooks(val)
            }
        },
        components: {
            NavBar,
            BookModal
        }
    }
</script>

<style scoped>
</style>