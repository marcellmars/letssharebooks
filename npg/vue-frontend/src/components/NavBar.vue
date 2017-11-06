<template>
        <b-button-toolbar justify>
            <b-button class="col left-arrow"
                      variant="info"
                      pill
                      v-if="links.prev"
                      @click="fetchBooks(links.prev.href)">
                &lt;&lt; prev
            </b-button>

            <b-button disabled
                      class="col"
                      variant="warning"
                      pill>
                {{ bookresults * (meta.page - 1) }}-
                {{ Math.min(meta.page * bookresults, meta.total) }} of {{ meta.total }}
                (page:{{ meta.page }})
            </b-button>

            <b-button class="col right-arrow"
                      variant="info"
                      pill
                      v-if="links.next"
                      @click="fetchBooks(links.next.href)">
                next &gt;&gt;
            </b-button>
        </b-button-toolbar>
</template>

<script>
    export default {
        props: ['links',
            'bookresults',
            'meta'
        ],

        methods: {
            fetchBooks(l) {
                this.$emit('fetchBooks', l);
            }
        }
    }
</script>

<style scoped>
    .right-arrow {
        font-weight: bold;
        text-align: right;
    }

    .left-arrow {
        font-weight: bold;
        text-align: left;
    }
</style>
