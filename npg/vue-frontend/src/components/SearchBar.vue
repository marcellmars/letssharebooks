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
                @on-change="getQuery($event)"
                :options="options"
                maxHeight="18em"
                resetOnOptionsChange="true"
                :placeholder="ph">
            </v-select>
        </b-col>
        <b-button variant="danger" @click="search">Search</b-button>
    </b-button-toolbar>
</template>

<script>
    import vSelect from "vue-select";

    export default {
        data() {
            return {
                options: [],
                query: "",
                categories: {
                    'authors': new Set(),
                    'titles': new Set(),
                    'tags': new Set()
                },
                in_search: "Authors",
                ph: "Search MotW"
            }
        },
        methods: {
            search() {
                let sq = {
                    'endpoint': `search/${this.in_search.toLowerCase()}/${this.query.toLowerCase()}`,
                    'status': `${this.in_search.toLowerCase()}: ${this.query.toLowerCase()}`
                }
                this.$emit('atInput', sq)
            },
            atInput(e) {
                let sq = {
                    'endpoint': `search/${this.in_search.toLowerCase()}/${e}`,
                    'status': `${this.in_search.toLowerCase()}: ${e}`
                }
                this.$emit('atInput', sq)
            },
            getOptions(search, loading) {
                console.log(search);
                this.query = search;
                this.options = Array.from(this.categories[this.in_search.toLowerCase()]);
                this.options.sort()
                if (search.length != 4) {
                    loading(false)
                    return
                }
                loading(true)
                this.$http.get(
                        `autocomplete/${this.in_search.toLowerCase()}/${search.toLowerCase()}`
                    )
                    .then(response => {
                        return response.json()
                    })
                    .then(data => {
                        let c = this.in_search.toLowerCase()
                        for (let d of data._items) {
                            this.categories[c].add(d)
                        }
                        this.options = Array.from(this.categories[c]);
                        this.options.sort();
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