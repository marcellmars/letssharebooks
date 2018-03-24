<template>
    <div>
        <nav-bar :links="shelf.links"
                 :meta="shelf.meta">
        </nav-bar>
        <book-modal :book="book" />
        <b-card-group d-block>
            <book-card @titleClick="titleClick"
                       v-for="b in shelf.books"
                       :book="b"
                       :key="b._id">
            </book-card>
        </b-card-group>
        <nav-bar :links="shelf.links"
                 :meta="shelf.meta">
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
        props: ['searchQuery',
                'shelf'],
        data: function() {
            return {
                book: {}
            }
        },
        methods: {
            titleClick(book) {
                this.book = book;
                this.$store.state.showModal = true;
            },
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