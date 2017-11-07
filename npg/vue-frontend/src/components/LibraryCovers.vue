<template>
    <div>
        <nav-bar :links="links"
                 :bookresults="bookresults"
                 :meta="meta"
                 @fetchBooks="fetchBooks($event)">
        </nav-bar>

        <b-card-group>
          <book-card @reloadSearch="fetchBooks($event)"
                     v-for="book in books"
                     :book="book"
                     :key="title"></book-card>
        </b-card-group>

        <nav-bar :links="links"
                 :bookresults="bookresults"
                 :meta="meta"
                 @fetchBooks="fetchBooks($event)">
        </nav-bar>
    </div>
</template>

<script>
    import BookCard from './BookCard.vue'
    import NavBar from './NavBar.vue'

    export default {
        data: function() {
            return {
                // books: LIBRARY.books.add
                books: [],
                links: {
                    'next': false,
                    'prev': false
                },
                meta: {},
                bookresults: 12
            }
        },
        methods: {
            fetchBooks(endpoint) {
                // this.$http.get('static/data.js')
                this.$http.get(endpoint)
                    .then(response => {
                        return response.json()
                    })
                    .then(data => {
                        this.books = data._items;
                        this.meta = data._meta;
                        this.links = data._links;
                    });
            },
        },
        mounted: function() {
            this.fetchBooks('books/on/')
        },
        components: {
            BookCard,
            NavBar
        }
    }
</script>

<style scoped>
</style>
