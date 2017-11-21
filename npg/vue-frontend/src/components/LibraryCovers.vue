<template>
    <div>
        <nav-bar :links="links"
                 :bookresults="bookresults"
                 :meta="meta"
                 @flipPage="librariesLive($event)">
        </nav-bar>

        <b-card-group>
            <book-card @reloadSearch="librariesLive($event)"
                       v-for="book in books"
                       :book="book">
            </book-card>
        </b-card-group>

        <nav-bar :links="links"
                 :bookresults="bookresults"
                 :meta="meta"
                 @flipPage="librariesLive($event)">
        </nav-bar>
    </div>
</template>

<script>
    import BookCard from './BookCard.vue'
    import NavBar from './NavBar.vue'

    export default {
        props: ['reloadSearch'],
        data: function() {
            return {
                // books: LIBRARY.books.add
                books: [],
                libraries: [],
                links: {
                    'next': false,
                    'prev': false
                },
                meta: {},
                bookresults: 12
            }
        },
        methods: {
            getBooks(resource, prms, status) {
                console.log(prms)
                this.$http.get(resource, {
                        params: prms
                    })
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
            librariesLive(a) {
                let resource = a['resource']
                let query = a['query']
                let status = a['status']
                let params = a['params']
                // this.$http.get('static/data.js')
                this.$http.get('libraries/on')
                    .then(response => {
                        return response.json()
                    })
                    .then(data => {
                        for (let item of data._items) {
                            this.libraries.push(item._id)
                        }
                        return JSON.stringify(this.libraries)
                    })
                    .then(data => {
                        let prms = {}
                        if (query) {
                            prms['where'] = `{"library_uuid":{"$in": ${data}}, ${query}}`
                        } else {
                            prms['where'] = `{"library_uuid":{"$in": ${data}}}`
                        }
                        prms['embedded'] = `{"library_uuid": 1}`

                        if (params) {
                            params.forEach(
                                function(v, k){
                                    prms[k] = v
                            })
                        }

                        this.getBooks(resource, prms, status)
                    })
            }
        },
        mounted: function() {
            this.librariesLive({
                'resource': 'books',
                'query': NaN,
                'params': NaN,
                /* 'query': `"authors": "Karl Marx"`,*/
                'status': 'all books'
            })
        },
        watch: {
            reloadSearch: function(val, oldVal) {
                this.librariesLive(val)
            }
        },
        components: {
            BookCard,
            NavBar
        }
    }
</script>

<style scoped>
</style>
