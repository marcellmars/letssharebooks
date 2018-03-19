<template>
    <b-button-toolbar justify>
        <b-button class="col left-arrow"
                  variant="info"
                  pill
                  v-if="links.prev"
                  @click="fetchBooks({'endpoint': links.prev.href, 'status': meta.status})">
            &lt;&lt; prev
        </b-button>

        <b-button disabled
                  class="col"
                  variant="warning"
                  pill>
            {{ meta.max_results * (meta.page - 1) }}-
            {{ Math.min(meta.page * meta.max_results, meta.total) }} of {{ meta.total }}
            ({{ meta.status }})
        </b-button>

        <b-button class="col right-arrow"
                  variant="info"
                  pill
                  v-if="links.next"
                  @click="fetchBooks({'endpoint': links.next.href, 'status': meta.status})">
            next &gt;&gt;
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
                    n.firstElementChild.src="data:image/gif;base64,R0lGODlhAQABAIABAP///wAAACH5BAEKAAEALAAAAAABAAEAAAICTAEAOw==";
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
</style>
