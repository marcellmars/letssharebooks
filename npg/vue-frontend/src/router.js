import {
    store
} from './store/store';
import {
    eventBus,
} from './main';
import SingleBook from './components/SingleBook.vue';


function processSearch(url) {
    store.state.searchQuery = {
        'endpoint': url.fullPath,
        'status': url.params.field + ": " + url.params.value
    };
}

function processRoot(url) {
    console.log("ProcessRoot");
    console.log(url);
    store.state.searchQuery = {
        'endpoint': '/books' + url.fullPath,
        'status': 'all books'
    };
}

function processBooks(url) {
    store.state.searchQuery = {
        'endpoint': url.fullPath,
        'status': 'all books'
    };
}

function processBook(url) {
    return {
        id: url.params.id
    };
 }

export const routes = [{
        'path': '/search/:field/:value',
        template: '',
        props: processSearch
    },
    {
        'path': '/',
        template: '',
        props: processRoot
    },
    {
        'path': '/books',
        template: '',
        props: processBooks
    },
    {
        'path': '/book/:id',
        component: SingleBook,
        props: processBook
    }
]
