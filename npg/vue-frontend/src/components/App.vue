<template>
    <b-container class="app" fluid>
        <search-bar @atInput="reloadSearch($event)"/>
        <library-covers :reloadSearch="sq"/>
    </b-container>
</template>

<script>
 export default {
     name: 'app',
     data() {
         return {
             sq: {'resource': 'books',
                  'db_query': NaN,
                  'url_params': NaN,
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

<style>
    * {
        border-radius: 0 !important;
    }

    #app {
        font-family: 'Avenir', Helvetica, Arial, sans-serif;
        /* font-family: BitstreamVeraSansMono, Consolas, monospace; */
        font-weight: bold;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        color: #2c3e50;
    }

    .motw_link,
    .motw_link:hover,
    .motw_link:visited {
        color: white;
        font-weight: bold;
        text-decoration: none;
    }

    .motw_link:hover {
        text-decoration: underline;
    }
</style>
