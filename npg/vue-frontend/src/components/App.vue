<template>
    <b-container class="app" fluid>
        <motw-header @switchView="table=!table;" :show="show"></motw-header>
        <search-bar @atInput="reloadSearch($event)" />
        <library-covers v-if="!table"  :searchQuery="sq" />
        <library-table v-if="table" :searchQuery="sq" />
    </b-container>
</template>

<script>
export default {
    name: 'app',
    data() {
        return {
            counter: 0,
            table: true,
            show: "covers",
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
    },
    watch: {
        table: function(val, oldVal) {
            if (val) {
                this.show = 'covers'
            } else {
                this.show = 'list';
            }
        }
    },
    mounted: function() {
        this.counter ++;
        console.log(this.counter)
        let loadPortable = document.createElement('script')
        loadPortable.setAttribute('rel', 'prefetch')
        loadPortable.setAttribute('src', 'static/data.js')
        loadPortable.async = false;
        var _this = this
        document.head.appendChild(loadPortable)
        loadPortable.onload = function() {
            console.log(bkz)
            _this.sq = {
                'endpoint': 'books',
                'status': 'all books'
            }
            _this.reloadSearch(_this.sq)
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
