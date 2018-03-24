import Vue from "vue";

import BootstrapVue from 'bootstrap-vue';
import VueResource from 'vue-resource';
import {
    store
} from './store/store';

import App from './components/App.vue';
import MotwHeader from './components/MotwHeader.vue';
import LibraryCovers from './components/LibraryCovers.vue';
import LibraryTable from './components/LibraryTable.vue';
import SearchBar from './components/SearchBar.vue';

Vue.use(VueResource);
Vue.use(BootstrapVue);

import 'bootstrap-vue/dist/bootstrap-vue.css';
import 'bootstrap/dist/css/bootstrap.css';

Vue.component('motw-header', MotwHeader);
Vue.component('library-covers', LibraryCovers);
Vue.component('library-table', LibraryTable);
Vue.component('search-bar', SearchBar);

Vue.http.options.root = 'http://192.168.0.11:2018';

export const eventBus = new Vue();

new Vue({
    el: "#app",
    store,
    render: h => h(App)
});
