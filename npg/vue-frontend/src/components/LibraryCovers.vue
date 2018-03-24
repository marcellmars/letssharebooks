<template>
    <div>
        <nav-bar :links="links"
                 :meta="meta"
                 @fetchBooks="fetchBooks($event)">
        </nav-bar>
        <book-modal :show_modal="show_modal"
                    :book="book"
                    @searchQuery="fetchBooks($event)">
        </book-modal>
        <b-card-group d-block>
            <book-card @searchQuery="fetchBooks($event)"
                       @titleClick="titleClick"
                       v-for="b in books"
                       :book="b"
                       :key="b._id">
            </book-card>
        </b-card-group>
        <nav-bar :links="links"
                 :meta="meta"
                 @fetchBooks="fetchBooks($event)">
        </nav-bar>
    </div>
</template>

<script>
    import BookCard from './BookCard.vue'
    import BookModal from './BookModal.vue'
    import NavBar from './NavBar.vue'

    export default {
        props: ['searchQuery'],
        data: function() {
            return {
                show_modal: false,
                // books: LIBRARY.books.add
                books: [],
                links: {
                    'next': false,
                    'prev': false
                },
                meta: {},
                book: {}
            }
        },
        methods: {
            titleClick(book) {
                this.book = book;
                this.show_modal = true;
            },
            fetchBooks(a) {
                this.show_modal = false;
                let endpoint = a['endpoint']
                let status = a['status']
                this.$http.get(endpoint)
                    .then(response => {
                        console.log(response);
                        return response.json()
                    })
                    .then(data => {
                        this.books = data._items;
                        this.meta = data._meta;
                        this.links = data._links;
                        this.meta['status'] = status
                    });
            },
        },
        mounted: function() {
            this.fetchBooks(this.searchQuery)
        },
        watch: {
            searchQuery: function(val, oldVal) {
                this.fetchBooks(val)
            }
        },
        components: {
            BookCard,
            BookModal,
            NavBar
        }
    }
</script>

<style scoped>
</style>