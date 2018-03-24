<template>
    <b-button-toolbar justify>
        <b-dropdown variant="disabled"right :text="in_search" >
            <b-dropdown-item class="search" @click="in_search='Authors';options=[];ph=''">Authors</b-dropdown-item>
            <b-dropdown-item @click="in_search='Titles';options=[];ph=''">Titles</b-dropdown-item>
            <b-dropdown-item @click="in_search='Tags';options=[];ph=''">Tags</b-dropdown-item>
        </b-dropdown>
        <b-col>
            <v-select class="vselect"
                      @input="atInput($event)"
                      :debounce="250"
                      :on-search="getOptions"
                      @on-change="getQuery($event)"
                      :options="options"
                      maxHeight="18em"
                      :placeholder="ph">
            </v-select>
        </b-col>
        <b-button variant="motwred" @click="search" class="motw-home font-weight-bold ">SEARCH</b-button>
    </b-button-toolbar>
</template>

<script>
    import vSelect from "vue-select";
    import {
        eventBus
    } from '../main';

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
                this.$store.state.searchQuery = {
                    'endpoint': `search/${this.in_search.toLowerCase()}/${this.query.toLowerCase()}`,
                    'status': `${this.in_search.toLowerCase()}: ${this.query.toLowerCase()}`
                }
                eventBus.$emit('reloadSearch')
            },
            atInput(e) {
                if (e.toLowerCase() == "null") {
                    return
                }
                this.$store.state.searchQuery = {
                    'endpoint': `search/${this.in_search.toLowerCase()}/${e}`,
                    'status': `${this.in_search.toLowerCase()}: ${e}`
                }
                eventBus.$emit('reloadSearch')
            },
            getOptions(search, loading) {
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

    a,
    .dropdown-item {
        border: 0px solid white;
    }
</style>