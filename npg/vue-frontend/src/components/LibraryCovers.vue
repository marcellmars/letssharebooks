<template>
    <div>
        <b-button-toolbar justify>
                <b-button class="col" variant="info" pill v-if="links.prev" @click="fetchBooks(links.prev.href)">prev page</b-button>
                <b-button disabled class="col" variant="warning" pill> {{ bookresults * (meta.page - 1) }}-{{ Math.min(meta.page * bookresults, meta.total) }} of {{ meta.total }} (page:{{ meta.page }})</b-button>
                <b-button class="col" variant="info" pill v-if="links.next" @click="fetchBooks(links.next.href)">next page</b-button>
        </b-button-toolbar>
        <b-card-group>
            <book-card v-for="book in books" :book="book"></book-card>
        </b-card-group>
        <b-button-toolbar justify>
                <b-button class="col" variant="info" pill v-if="links.prev" @click="fetchBooks(links.prev.href)">prev page</b-button>
                <b-button disabled class="col" variant="warning" pill> {{ bookresults * (meta.page - 1) }}-{{ Math.min(meta.page * bookresults, meta.total) }} of {{ meta.total }} (page:{{ meta.page }})</b-button>
                <b-button class="col" variant="info" pill v-if="links.next" @click="fetchBooks(links.next.href)">next page</b-button>
        </b-button-toolbar>
    </div>
</template>

<script>
    import BookCard from './BookCard.vue'

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
            fetchBooks(endpoint = 'books/on') {
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
            this.fetchBooks()
        },
        components: {
            BookCard,
        }
    }
</script>

<style scoped>

</style>
