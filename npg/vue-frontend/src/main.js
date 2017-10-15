import Vue from "vue";

import BootstrapVue from "bootstrap-vue";
import VueResource from "vue-resource";

import App from "./components/App.vue";
import LibraryCovers from "./components/LibraryCovers.vue";

Vue.use(VueResource);
Vue.use(BootstrapVue);

import "bootstrap-vue/dist/bootstrap-vue.css";
import "bootstrap/dist/css/bootstrap.css";

Vue.component('library-covers', LibraryCovers);

Vue.http.options.root = 'http://localhost:5000';

new Vue({
    el: "#app",
    render: h => h(App)
});