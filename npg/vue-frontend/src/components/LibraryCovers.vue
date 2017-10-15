<template>
  <b-container fluid>
    <search-bar></search-bar>
    <b-button pill v-if="links.prev" @click="fetchBooks(links.prev.href)">prev page</b-button>
    <b-button pill @click="fetchBooks()">fetch books</b-button>
    <b-button pill v-if="links.next" @click="fetchBooks(links.next.href)">next page</b-button>
    <b-card-group>
      <book-card v-for="book in books" :book="book"></book-card>
    </b-card-group>
  </b-container>
</template>

<script>
import BookCard from './BookCard.vue'
import SearchBar from './SearchBar.vue'

export default {
    data: function() {
        return {
            // books: LIBRARY.books.add
            books: [],
            links: {'next': false,
                    'prev': false
                   },
            meta: {}
        }
    },
    methods: {
        fetchBooks(endpoint = 'books') {
            // this.$http.get('static/data.js')
            this.$http.get(endpoint)
                .then(response => {
                    return response.json()})
                .then(data => {
                    this.books = data._items;
                    this.meta = data._meta;
                    this.links = data._links;
                    });
        }
    },
    components: {
        BookCard,
        SearchBar
    }
}
</script>

<style scoped>
</style>
