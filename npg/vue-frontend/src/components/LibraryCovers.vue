<template>
    <div>
        <nav-bar :links="links"
                 :bookresults="bookresults"
                 :meta="meta"
                 @flipPage="getLibraries($event)">
        </nav-bar>

        <b-card-group>
            <book-card @reloadSearch="getLibraries($event)"
                       v-for="book in books"
                       :book="book">
            </book-card>
        </b-card-group>

        <nav-bar :links="links"
                 :bookresults="bookresults"
                 :meta="meta"
                 @flipPage="getLibraries($event)">
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
            getLibraries(a) {
                let resource = a['resource']
                let db_query = a['db_query']
                let status = a['status']
                let url_params = a['url_params']
                // this.$http.get('static/data.js')
                this.$http.get('libraries/on')
                    .then(response => {
                        return response.json()
                    })
                    .then(data => {
                        let libraries = []
                        for (let item of data._items) {
                            libraries.push(item._id)
                        }
                        return JSON.stringify(libraries)
                    })
                    .then(data => {
                        let prms = {}
                        if (db_query) {
                            prms['where'] = `{"library_uuid":{"$in": ${data}}, ${db_query}}`
                        } else {
                            prms['where'] = `{"library_uuid":{"$in": ${data}}}`
                        }
                        prms['embedded'] = `{"library_uuid": 1}`

                        if (url_params) {
                            url_params.forEach(
                                function(v, k) {
                                    prms[k] = v
                                })
                        }

                        this.getBooks(resource, prms, status)
                    })
            }
        },
        mounted: function() {
            this.getLibraries({
                'resource': 'books',
                'db_query': NaN,
                'url_params': NaN,
                /* 'db_query': `"authors": "Karl Marx"`,*/
                'status': 'all books'
            })
        },
        watch: {
            reloadSearch: function(val, oldVal) {
                this.getLibraries(val)
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
