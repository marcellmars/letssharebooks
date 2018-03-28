<template>
    <div>
        <nav-bar :links="shelf.links"
                 :meta="shelf.meta">
        </nav-bar>
        <b-table :items="shelf.books"
                 :fields="fields"
                 @row-clicked="rowClicked"
                 striped
                 hover
                 small>         
        </b-table>
        <nav-bar :links="shelf.links" :meta="shelf.meta"">
        </nav-bar>
    </div>
</template>

<script>
    import NavBar from './NavBar.vue'
    import {
        eventBus
    } from '../main';

    export default {
        props: ['searchQuery',
            'shelf',
        ],
        data: function() {
            return {
                fields: {
                    'authors': {
                        label: 'Authors',
                        formatter: 'authorsCommaSpace',
                        tdClass: 'btitle w-25'
                    },
                    'title': {
                        label: 'Title',
                    },
                    'pubdate': {
                        label: 'Year',
                        formatter: 'publishedYear',
                    },
                    'formats': {
                        label: 'File',
                        formatter: 'getFormats',
                        tdClass: 'formats-download'
                    }

                },
                links: {
                    'next': false,
                    'prev': false
                },
                meta: {},
                book: {}
            }
        },
        methods: {
            authorsCommaSpace(t) {
                if (t.length > 3) {
                    t = t.slice(0, 3)
                    t.push("et al.")
                }
                return t.join(',<br/>')
            },
            publishedYear(d) {
                return `${d}`.slice(0, 4) + '&nbsp;'
            },
            getFormats(key, value, book) {
                let f = '';
                for (let frm of book['formats']) {
                    let book_url = book.library_url + frm.dir_path + frm.file_name
                    let download_stripe = `<a class="motw_table_link" href="${book_url}">.${frm.format }</a>, `;
                    f += download_stripe;
                }
                return f.slice(0, -3)
            },
            rowClicked(item, row, event) {
                this.book = item;
                this.$store.state.showModal = true;
                this.$store.state.singleBook = false;
                this.$router.push('/book/' + item['_id'])
            }
        },
        components: {
            NavBar
        }
    }
</script>

<style scoped>
    .table:hover {
        cursor: pointer;
    }
</style>