<template>
<v-select
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
            endpoint: 'autocomplete/titles/',
            xargs: '?max_results=500',
            label: 'val'
	      }
    },
    methods: {
        getOptions(search, loading) {
            if (search.length != 4) {
                loading(false)
                return
            }
            loading(true)
            this.$http.get(this.endpoint + search.toLowerCase() + this.xargs)
                .then(response => {
                    return response.json()})
                .then(data => {
                    let s = new Set(this.options)
                    for (var d of data._items) {
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

<style>
</style>
