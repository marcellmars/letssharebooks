<template>
    <b-button-toolbar justify clearfix>
        <b-button class="float-left"
                  variant="link"
                  pill
                  v-if="links.prev"
                  @click="fetchBooks({'endpoint': links.prev.href, 'status': meta.status}, false)">&lt;&lt; prev page&nbsp;&nbsp;&nbsp;&nbsp</b-button>

        <b-button disabled
                  class="col status mw-100"
                  variant="text-muted"
                  pill>
            {{ meta.max_results * (meta.page - 1)}}-{{Math.min(meta.page * meta.max_results, meta.total) }} of {{ meta.total }}
            ({{ meta.status }})
        </b-button>

        <b-button class="float-right"
                  variant="link"
                  pill
                  v-if="links.next"
                  @click="fetchBooks({'endpoint': links.next.href, 'status': meta.status}, true)">&nbsp;&nbsp;&nbsp;&nbsp;next page &gt;&gt;</b-button>
    </b-button-toolbar>
</template>

<script>
    import {
        eventBus
    } from '../main';

    export default {
        props: [
            'links',
            'meta'
        ],
        methods: {
            fetchBooks(searchQuery, reload) {
                /* if (reload) {*/
                /* document.querySelectorAll(".card").forEach(*/
                /* function(n) {*/
                /* n.firstElementChild.src = "data:image/gif;base64,R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==";*/
                /* })*/
                /* }*/
            this.$store.state.searchQuery = searchQuery;
            eventBus.$emit('reloadSearch');
        }
    }
    }
</script>

<style scoped>
    .right-arrow {
        font-weight: bold;
        text-align: right !important;
    }

    .left-arrow {
        font-weight: bold;
        text-align: left !important;
    }

    .status {
        color: black;
        /* font-weight: bold; */
        border-top: 0.5em solid white;
        border-bottom: 0.5em solid white;
        border-left: 0px solid white;
        border-right: 0px solid white;
        padding-top: 0.1em;
    }
</style>