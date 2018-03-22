<template>
    <b-button-toolbar justify>
        <b-button class="col left-arrow"
                  variant="link"
                  pill
                  v-if="links.prev"
                  @click="fetchBooks({'endpoint': links.prev.href, 'status': meta.status})">
            &lt;&lt; previous page
        </b-button>

        <b-button disabled
                  class="col status"
                  variant="secondary"
                  pill>
            {{ meta.max_results * (meta.page - 1)}}-{{Math.min(meta.page * meta.max_results, meta.total) }} of {{ meta.total }}
            ({{ meta.status }})
        </b-button>

        <b-button class="col right-arrow"
                  variant="link"
                  pill
                  v-if="links.next"
                  @click="fetchBooks({'endpoint': links.next.href, 'status': meta.status})">
            next page &gt;&gt;
        </b-button>
    </b-button-toolbar>
</template>

<script>
    export default {
        props: [
            'links',
            'meta'
        ],
        methods: {
            fetchBooks(l) {
                document.querySelectorAll(".card").forEach(
                    function(n) {
                        n.firstElementChild.src = "data:image/gif;base64,R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==";
                    })
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

    .status {
        border-top: 0.5em solid white;
        border-bottom: 0.5em solid white;
        border-left: 0px solid white;
        border-right : 0px solid white;
        padding-top: 0.1em;
    }
</style>