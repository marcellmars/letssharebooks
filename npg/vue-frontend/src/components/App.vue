<template>
    <b-container class="app" fluid>
        <motw-header></motw-header>
        <search-bar @atInput="reloadSearch($event)" />
        <library-covers v-if="!table" :reloadSearch="sq" />
        <library-table v-if="table" :reloadSearch="sq" />
    </b-container>
</template>

<script>
    export default {
        name: 'app',
        data() {
            return {
                table: true,
                sq: {
                    'endpoint': 'books',
                    'status': 'all books'
                }
            }
        },
        methods: {
            reloadSearch(e) {
                this.sq = e
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