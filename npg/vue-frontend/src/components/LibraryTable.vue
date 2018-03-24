<template>
    <div>
        <nav-bar :links="links"
                 :meta="meta"
                 @fetchBooks="fetchBooks()">
        </nav-bar>
        <book-modal :show_modal="show_modal"
                    :book="book"
                    @reloadSearch="fetchBooks()" />
        <b-table :items="books"
                 :fields="fields"
                 @row-clicked="rowClicked"
                 striped
                 hover
                 small>         
        </b-table>
        <nav-bar :links="links" :meta="meta" @fetchBooks="fetchBooks()">
        </nav-bar>
    </div>
</template>

<script>
    import NavBar from './NavBar.vue'
    import BookModal from './BookModal.vue'
    import {
        eventBus
    } from '../main';

    export default {
        props: ['searchQuery'],
        data: function() {
            return {
                books: [],
                fields: {
                    'authors': {
                        label: 'Authors',
                        formatter: 'authorsCommaSpace',
                        tdClass: 'btitle w-25'
                    },
                    'title': {
                        label: 'Title',
                    },
                    'pubdate': {
                        label: 'Year',
                        formatter: 'publishedYear',
                    },
                    'formats': {
                        label: 'File',
                        formatter: 'getFormats',
                        tdClass: 'formats-download'
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
            fetchBooks() {
                this.show_modal = false;
                let endpoint = this.$store.state.searchQuery['endpoint']
                let status = this.$store.state.searchQuery['status']
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
                if (t.length > 3) {
                    t = t.slice(0, 3)
                    t.push("et al.")
                }
                return t.join(',<br/>')
            },
            publishedYear(d) {
                return `${d}`.slice(0, 4) + '&nbsp;'
            },
            getFormats(key, value, book) {
                let f = '';
                for (let frm of book['formats']) {
                    let book_url = book.library_url + frm.dir_path + frm.file_name
                    let download_stripe = `<a class="motw_table_link" href="${book_url}">.${frm.format }</a>, `;
                    f += download_stripe;
                }
                return f.slice(0, -3)
            },
            rowClicked(item, row, event) {
                this.book = item;
                this.show_modal = true;
            }
        },
        beforeMount() {
            eventBus.$on('reloadSearch', () => this.fetchBooks())
        },
        components: {
            NavBar,
            BookModal
        }
    }
</script>

<style scoped>
    .table:hover {
        cursor: pointer;
    }
</style>