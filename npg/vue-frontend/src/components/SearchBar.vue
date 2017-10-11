<template>
<v-select
  @search:blur="loading(false)"
	:debounce="250"
	:on-search="getOptions"
	:options="options"
  maxHeight="18em"
	placeholder="Search MotW Authors"
>
</v-select>
</template>

<script>
import vSelect from "vue-select";

export default {
    data() {
	      return {
		        options: [],
            endpoint: 'titles_ngrams/',
            label: 'titles'
	      }
    },
    methods: {
        getOptions(search, loading) {
            if (search.length != 4) {
                loading(false)
                return
            }
            loading(true)
            this.$http.get(this.endpoint + search.toLowerCase())
                .then(response => {
                    return response.json()})
                .then(data => {
                    let s = new Set(this.options)
                    for (var d of data[this.label]) {
                        s.add(d)
                    }
                    this.options = Array.from(s);
                    s.clear()
                    this.meta = data["_meta"];
                    this.links = data["_links"];
                    loading(false)
                });
        }
    },
    components: {
        vSelect
    }
}

</script>

<style>
</style>
