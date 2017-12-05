<template>
    <b-button-toolbar justify>
        <b-dropdown variant="danger" right :text="in_search" >
            <b-dropdown-item @click="in_search='Authors';options=[];ph=''">Authors</b-dropdown-item>
            <b-dropdown-item @click="in_search='Titles';options=[];ph=''">Titles</b-dropdown-item>
            <b-dropdown-item @click="in_search='Tags';options=[];ph=''">Tags</b-dropdown-item>
        </b-dropdown>
        <b-col>
            <v-select
                class="vselect"
                @input="atInput($event)"
                :debounce="250"
                :on-search="getOptions"
                :options="options"
                maxHeight="18em"
                :placeholder="ph">
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
                categories: {
                    'authors': new Set(),
                    'titles': new Set(),
                    'tags': new Set()
                },
                label: 'val',
                in_search: "Authors",
                ph: "Search MotW"
            }
        },
        methods: {
            atInput(e) {
                if (this.in_search === "Titles") {
                    this.in_search = "Title"
                }
                let sq = {
                    'resource': "books",
                    'db_query': `"${this.in_search.toLowerCase()}": "${e}"`,
                    'url_ params': NaN,
                    'status': `${this.in_search.toLowerCase()}: ${e}`
                }
                this.$emit('atInput', sq)
            },
            getOptions(search, loading) {
                this.options = Array.from(this.categories[this.in_search.toLowerCase()]);
                if (search.length != 4) {
                    loading(false)
                    return
                }
                loading(true)

                this.$http.get('libraries/on')
                    .then(response => {
                        return response.json()
                    })
                    .then(data => {
                        let libraries = []
                        for (let item of data._items) {
                            libraries.push(item._id)
                        }
                        return JSON.stringify(libraries)
                    })
                    .then(data => {
                        console.log(data)
                        this.$http.get(
                                `autocomplete/${this.in_search.toLowerCase()}/${search.toLowerCase()}`, {
                                    params: {
                                        'where': `{"library_uuid": {"$in": ${data}}}`,
                                        'max_results': 5000
                                    }
                                })
                            .then(response => {
                                return response.json()
                            })
                            .then(data => {
                                let c = this.in_search.toLowerCase()
                                for (let d of data._items) {
                                    this.categories[c].add(d[this.label])
                                }
                                this.options = Array.from(this.categories[c]);
                                this.meta = data._meta;
                                this.links = data._links;
                                loading(false)
                            });
                    })
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
