<template>
    <b-button-toolbar justify>
        <b-dropdown variant="danger" right :text="in_search" >
            <b-dropdown-item @click="in_search='Authors'">Authors</b-dropdown-item>
            <b-dropdown-item @click="in_search='Titles'">Titles</b-dropdown-item>
            <b-dropdown-item @click="in_search='Tags'">Tags</b-dropdown-item>
        </b-dropdown>
        <b-col>
            <v-select
                class="vselect"
                @input="atInput($event)"
                :debounce="250"
                :on-search="getOptions"
                :options="options"
                maxHeight="18em"
                placeholder="Search MotW">
            </v-select>
        </b-col>
        <b-button variant="danger">Search</b-button>
    </b-button-toolbar>
</template>

<script>
    import vSelect from "vue-select";

    export default {
        data() {
            return {
                options: [],
                xargs: '?max_results=500',
                label: 'val',
                in_search: "Authors",
            }
        },
        methods: {
            atInput(e) {
                if (this.in_search === "Titles") {
                    this.in_search = "Title"
                }
                let sq = {
                    'resource': "books",
                    'query': `"${this.in_search.toLowerCase()}": "${e}"`,
                    'params': NaN,
                    'status': `${this.in_search.toLowerCase()}: ${e}`
                }
                this.$emit('atInput', sq)
            },
            getOptions(search, loading) {
                if (search.length != 4) {
                    loading(false)
                    return
                }
                loading(true)
                this.$http.get(
                    `autocomplete/${this.in_search.toLowerCase()}/${search.toLowerCase()}${this.xargs}`
                )
                    .then(response => {
                        return response.json()
                    })
                    .then(data => {
                        let s = new Set(this.options)
                        for (let d of data._items) {
                            s.add(d[this.label])
                        }
                        this.options = Array.from(s);
                        s.clear()
                        this.meta = data._meta;
                        this.links = data._links;
                        loading(false)
                    });
            }
        },
        components: {
            vSelect
        }
    }
</script>

<style scoped>
    .col,
    .v-select {
        display: block;
        width: 100%;
        padding-right: 0px;
        padding-left: 0px;
    }

    a {
        color: black;
        font-weight: bold;
        text-decoration: none;
    }
</style>
