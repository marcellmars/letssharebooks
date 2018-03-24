<template>
    <div>
        <nav-bar :links="links"
                 :meta="meta"
                 @fetchBooks="fetchBooks()">
        </nav-bar>
        <book-modal :show_modal="show_modal"
                    :book="book"
                    @searchQuery="fetchBooks()">
        </book-modal>
        <b-card-group d-block>
            <book-card @searchQuery="fetchBooks()"
                       @titleClick="titleClick"
                       v-for="b in books"
                       :book="b"
                       :key="b._id">
            </book-card>
        </b-card-group>
        <nav-bar :links="links"
                 :meta="meta"
                 @fetchBooks="fetchBooks()">
        </nav-bar>
    </div>
</template>

<script>
    import BookCard from './BookCard.vue'
    import BookModal from './BookModal.vue'
    import NavBar from './NavBar.vue'
    import {
    eventBus
    } from '../main';

    export default {
        props: ['searchQuery'],
        data: function() {
            return {
                show_modal: false,
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
        },
        beforeMount() {
            eventBus.$on('reloadSearch', () => this.fetchBooks());
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