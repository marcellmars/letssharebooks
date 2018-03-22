<template>
    <b-container class="app" fluid>
        <search-bar @atInput="reloadSearch($event)" />
        <!-- <library-covers :reloadSearch="sq" /> -->
        <library-table :reloadSearch="sq" />
    </b-container>
</template>

<script>
 export default {
     name: 'app',
     data() {
         return {
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

<style>
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
     /* font-weight: bold; */
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

 /*  */
 /* .btitle { */
 /* font-size: 1.1em; */
 /* } */
 /*  */
 /* .formats-download { */
     /* text-align: right; */
 /* font-size: 1.1em; */
 /* } */
</style>