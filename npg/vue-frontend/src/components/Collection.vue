<template>
  <b-container fluid>
    <b-button pill @click="fetchBooks">{{ name }}.vue</b-button>
    <b-card-group>
      <item :message="collectionMessage" @fromItem="processMessage($event)" v-for="book in books" :book="book"></item>
    </b-card-group>
  </b-container>
</template>

<script>
import Item from './Item.vue'

export default {
    data: function() {
        return {
            name: 'Collection',
            counter: 0,
            collectionMessage: 'edit me',
            itemMessage: 'still nothing...',
            // books: LIBRARY.books.add
            books: [],
            links: {},
            meta: {}
        }
    },
    methods: {
        processMessage(e) {
            this.itemMessage = e;
            this.counter++;
        },
        fetchBooks() {
            // this.$http.get('static/data.js')
            this.$http.get('http://localhost:5000/books')
                .then(response => {
                    return response.json()})
                .then(data => {
                    this.books = data["_items"];
                    this.meta = data["_meta"];
                    this.links = data["_links"];
                    });
        }
    },
    components: {
        'item': Item
    }
}
</script>

<style scoped>
</style>
