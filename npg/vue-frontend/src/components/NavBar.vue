<template>
    <b-button-toolbar justify>
        <b-button class="col left-arrow"
                  variant="info"
                  pill
                  v-if="links.prev"
                  @click="flipPage('prev')">
            &lt;&lt; prev
        </b-button>

        <b-button disabled
                  class="col"
                  variant="warning"
                  pill>
            {{ bookresults * (meta.page - 1) }}-
            {{ Math.min(meta.page * bookresults, meta.total) }} of {{ meta.total }}
            ({{ meta.status }})
        </b-button>

        <b-button class="col right-arrow"
                  variant="info"
                  pill
                  v-if="links.next"
                  @click="flipPage('next')">
            next &gt;&gt;
        </b-button>
    </b-button-toolbar>
</template>

<script>
    export default {
        props: [
            'links',
            'bookresults',
            'meta'
        ],
        methods: {
            flipPage(page) {
                let sq = {}
                sq['resource'] = "books";
                sq['status'] = this.meta.status;
                if (page === "next") {
                    sq['params'] = new Map(
                        [["page", `${this.links.next.href.split('?')[1].split('&')[1].split('=')[1]}`]]
                    );
                } else if (page == "prev") {
                    sq['params'] = new Map(
                        [["page", `${this.links.next.href.split('?')[1].split('&')[1].split('=')[1]}`]]
                    );
                }
                console.log(sq)
                this.$emit('flipPage', sq);
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
