<template>
    <b-button-toolbar justify class="motwheader">
        <b-button variant="motwred" class="motw-home font-weight-bold">LIBRARY</b-button>
        <b-button pill variant="link" @click="$emit('switchView')">show {{ show }}</b-button>
        <a class="motw-bookmark  align-text-middle float-right" href="https://wwww.memoryoftheworld.org">MEMORY OF THE WORLD</a>
    </b-button-toolbar>
</template>

<script>
 export default {
         props: ['show']
 }
</script>

<style>

    .motwheader {
        margin-bottom: 0.4em;
        margin-top: 0.3em;
    }

    .motw-home {
        color: white;
        height: 0;
        padding: 0 0 0 0;
        border: 0.9em solid red;
        line-height: 0.2em;
        font-size: 1.1em;
        font-weight: bold;
    }

    .motw-home:hover {
        text-decoration: underline;
        background-color: red;
    }

    .motw-bookmark {
        color: white;
        height: 0;
        padding: 0 1.2em 0 0;
        border: 0.9em solid red;
        line-height: 0.2em;
        border-right-color: transparent;
        font-size: 1.1em;
        font-weight: bold;
    }

    .motw-bookmark:hover {
        color: white;
        height: 0;
        padding: 0 1.2em 0 0;
        border: 0.9em solid #c00;
        line-height: 0.2em;
        border-right-color: transparent;
        font-size: 1.1em;
        font-weight: bold;
    }
</style>
