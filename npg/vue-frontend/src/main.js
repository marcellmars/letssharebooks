import Vue from "vue";

import BootstrapVue from "bootstrap-vue";
import VueResource from "vue-resource";

import App from "./components/App.vue";
import Collection from "./components/Collection.vue";

Vue.use(VueResource);
Vue.use(BootstrapVue);

import "bootstrap-vue/dist/bootstrap-vue.css";
import "bootstrap/dist/css/bootstrap.css";


Vue.component("collection", Collection);

new Vue({
    el: "#app",
    render: h => h(App)
});
