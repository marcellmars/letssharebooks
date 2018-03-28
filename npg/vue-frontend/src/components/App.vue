<template>
    <b-container class="app" fluid>
        <loading-spinner-modal v-if="loading" />
        <motw-header @allBooks="allBooks()"
                     @switchView="table=!table;"
                     :show="show"></motw-header>
        <search-bar />
        <library-covers v-if="!table" :shelf="shelf" />
        <library-table v-if="table"  :shelf="shelf" />
        <router-view></router-view>
    </b-container>
</template>

<script>
    import {
        eventBus
    } from '../main';

    export default {
        name: 'app',
        data() {
            return {
                loading: true,
                table: true,
                show: "show covers",
                shelf: {
                    books: [],
                    links: {
                        'next': false,
                        'prev': false
                    },
                    meta: {
                        'status': 'single book view',
                        'page': 2,
                        'max_results': 1,
                        'total': 1
                    }
                }
            }
        },
        methods: {
            fetchBooks() {
                if (!this.$store.state.searchQuery.hasOwnProperty('endpoint')) {
                    return
                }
                this.$store.state.showModal = false
                let endpoint = this.$store.state.searchQuery['endpoint'].substring(1)
                let status = this.$store.state.searchQuery['status']
                this.loading = true;
                let show_p = this.show
                this.show = "loading..."
                this.$http.get(endpoint)
                    .then(response => {
                        return response.json()
                    })
                    .then(data => {
                        this.shelf.books = data._items;
                        this.shelf.meta = data._meta;
                        this.shelf.links = data._links;
                        this.shelf.meta['status'] = status
                        this.$router.push({
                            'path': "/" + endpoint
                        })
                    })
                    .then(() => {
                        this.show = show_p
                        this.loading = false;
                    });
            },
            allBooks() {
                this.$store.state.searchQuery = {
                    'endpoint': '/books',
                    'status': 'all books'
                }
                eventBus.$emit('reloadSearch')
            }
        },
        watch: {
            table: function(val, oldVal) {
                if (val) {
                    this.show = 'show covers'
                } else {
                    this.show = 'show list';
                }
                eventBus.$emit('reloadSearch');
            }
        },
        mounted: function() {
            let loadPortable = document.createElement('script')
            loadPortable.setAttribute('rel', 'prefetch')
            loadPortable.setAttribute('src', 'static/data.js')
            loadPortable.async = false;
            var _this = this
            document.head.appendChild(loadPortable)
            loadPortable.onload = function() {
                eventBus.$emit('reloadSearch')
            }
        },
        created() {
            eventBus.$on('reloadSearch', this.fetchBooks)
            eventBus.$on('resetBooks', this.allBooks)
        }
    }
</script>

<style lang="scss">
    $theme-colors: ( "motwred": #f00);
    @import "node_modules/bootstrap/scss/bootstrap";

    * {
        border-radius: 0 !important;
    }

    .app {
        font-family: 'IBM Plex Mono', monospace;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        color: #2c3e50;
    }

    .motw_link,
    .motw_link:hover,
    .motw_link:visited {
        color: white;
        text-decoration: none;
    }

    .motw_link:hover {
        text-decoration: underline;
        font-weight: bold;
    }

    .motw_table_link,
    .motw_table_link:hover,
    .motw_table_link:visited {
        color: #2c3e50;
        font-weight: normal;
        text-decoration: underline;
    }

    .motw_table_link:hover {
        text-decoration: underline;
        font-weight: bold;
    }

    .download-disk {
        width: 6%;
        padding-bottom: 0.3em;
    }
</style>