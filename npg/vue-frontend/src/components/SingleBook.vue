<template>
    <div>
       <book-modal @modalHidden="resetBooks" :book="book" />
    </div>
</template>
<script>
    import BookModal from './BookModal.vue'
    import {
        eventBus
    } from '../main';

    export default {
        props: [
            'id'
        ],
        data() {
            return {
                book: {}
            }
        },
        methods: {
            resetBooks() {
                if (this.$store.state.singleBook) {
                    this.$store.state.singleBook = false;
                    eventBus.$emit('resetBooks')
                } else {
                    eventBus.$emit('reloadSearch')
                }
            }
        },
        mounted: function() {
            this.$http.get('book/' + this.id)
                .then(response => {
                    return response.json()
                })
                .then(data => {
                    this.book = data
                    this.$store.state.showModal = true
                    this.$router.push('/book/' + data['_id'])
                })
        },
        components: {
            BookModal
        }
    }
</script>
<style>
</style>