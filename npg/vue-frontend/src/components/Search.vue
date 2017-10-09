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
import vSelect from "vue-select"

export default {
    components: {vSelect},
    name: "search",
    data() {
	      return {
		        options: [],
	      }
    },
    methods: {
        getOptions(search, loading) {
            if (search.length != 4) {
                loading(false)
                return
            }
            loading(true)
            this.$http.get('http://localhost:5000/titles_ngrams/' + search.toLowerCase())
                .then(response => {
                    return response.json()})
                .then(data => {
                    let s = new Set(this.options)
                    for (var d of data["titles"]) {
                        s.add(d)
                    }
                    this.options = Array.from(s);
                    s.clear()
                    this.meta = data["_meta"];
                    this.links = data["_links"];
                    loading(false)
                });
        }
    }
}

</script>

<style>
</style>
