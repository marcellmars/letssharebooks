<template>
    <b-container class="app" fluid>
        <search-bar/>
        <library-covers/>
    </b-container>
</template>

<script>
    export default {
        name: 'app'
    }
</script>

<style>
    * {
        border-radius: 0 !important;
    }

    #app {
        /* font-family: 'Avenir', Helvetica, Arial, sans-serif; */
        font-family: BitstreamVeraSansMono, Consolas, monospace;
        font-weight: bold;
        -webkit-font-smoothing: antialiased;
        -moz-osx-font-smoothing: grayscale;
        color: #2c3e50;
    }
 a {
     color:white !important;
     font-weight: bold;
     text-decoration: none;
 }
</style>
