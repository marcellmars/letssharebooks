import Vue from "vue";

import BootstrapVue from "bootstrap-vue";
import VueResource from "vue-resource";

import App from "./components/App.vue";
import LibraryCovers from "./components/LibraryCovers.vue";
import LibraryTable from "./components/LibraryTable.vue";
import SearchBar from './components/SearchBar.vue';

Vue.use(VueResource);
Vue.use(BootstrapVue);

import "bootstrap-vue/dist/bootstrap-vue.css";
import "bootstrap/dist/css/bootstrap.css";

Vue.component('library-covers', LibraryCovers);
Vue.component('library-table', LibraryTable);
Vue.component('search-bar', SearchBar);

Vue.http.options.root = 'http://localhost:2018';

new Vue({
    el: "#app",
    render: h => h(App)
});
