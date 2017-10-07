<template>
  <b-container fluid>
    <b-button pill v-if="links.prev" @click="fetchBooks(links.prev.href)">prev page</b-button>
    <b-button pill @click="fetchBooks()">fetch books</b-button>
    <b-button pill v-if="links.next" @click="fetchBooks(links.next.href)">next page</b-button>
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
            links: {'next': false,
                    'prev': false
                   },
            meta: {}
        }
    },
    methods: {
        processMessage(e) {
            this.itemMessage = e;
            this.counter++;
        },
        fetchBooks(nl = 'books') {
            // this.$http.get('static/data.js')
            this.$http.get('http://localhost:5000/' + nl)
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
