<template>
    <b-container class="app" fluid>
        <motw-header @allBooks="allBooks()"
                     @switchView="table=!table;"
                     :show="show"></motw-header>
        <search-bar />
        <library-covers v-show="!table" />
        <library-table v-show="table"  />
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
                table: true,
                show: "covers",
            }
        },
        methods: {
            allBooks() {
                this.$store.state.searchQuery = {
                    'endpoint': 'books',
                    'status': 'all books'
                }
                eventBus.$emit('reloadSearch')
            }
        },
        watch: {
            table: function(val, oldVal) {
                if (val) {
                    this.show = 'covers'
                } else {
                    this.show = 'list';
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
                _this.$store.state.searchQuery = {
                    'endpoint': 'books',
                    'status': 'all books'
                }
                eventBus.$emit('reloadSearch')
            }
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
</style>