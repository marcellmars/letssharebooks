import Vue from 'vue';
import VueRouter from 'vue-router';

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

Vue.use(VueRouter);
Vue.use(VueResource);
Vue.use(BootstrapVue);

import 'bootstrap-vue/dist/bootstrap-vue.css';
import 'bootstrap/dist/css/bootstrap.css';

Vue.component('motw-header', MotwHeader);
Vue.component('library-covers', LibraryCovers);
Vue.component('library-table', LibraryTable);
Vue.component('search-bar', SearchBar);

Vue.http.options.root = 'http://localhost:2018';

export const eventBus = new Vue();

import { routes } from './router.js';
export const router = new VueRouter({
    routes
});

new Vue({
    el: "#app",
    store,
    router,
    render: h => h(App)
});
