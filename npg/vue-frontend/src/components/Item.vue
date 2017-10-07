<template>
  <div class="col col-xl-2 col-lg-3 col-md-4 col-sm-6 cols-12">
    <b-card overlay
      img-src="static/cover.jpg"
      img-alt="Card Image"
      text-variant="white"
      :title="book.title"
      :sub-title="getAuthors(book.authors)">
      <div class="card-text" v-html="getFormats(book.formats)"></div>
    </b-card>
  </div>
</template>

<script>
    export default {
        props: ['book'],
        methods: {
            getFormats(formats) {
                let f = "Download: ";
                for (var frm of formats) {
                    var download_stripe = '<a href="' + frm.dir_path + frm.file_name + '">' + frm.format.toUpperCase() + '</a>, '; 
                    f += download_stripe;
                }
                return f.slice(0,-3)
            },
            getAuthors(authors) {
                return authors.join(", ");
            }
        }
    }
</script>

<style scoped>
.col {
    padding-left: 2px;
    padding-right: 2px;
    padding-bottom: 2px;
    padding-top: 2px;
}

.card-body {
    padding:0px;
}

.card-text, .card-title, .card-subtitle {
    font-size: 1.2em;
    background: black;
    margin:0px;
}

.card-text {
    width:100%;
    position:absolute;
    bottom:0;
}
</style>
