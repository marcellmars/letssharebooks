<template>
  <div class="col col-xl-2 col-lg-3 col-md-4 col-sm-6 cols-12">
    <b-card overlay
      img-src="static/cover.jpg"
      img-alt="Card Image"
      text-variant="white"
      :title="book.title"
      :sub-title="getAuthors(book.authors)">
      <span class="card-text" v-for="f in book.formats">{{ f.format.toUpperCase() }}</span>
    </b-card>
  </div>
</template>

<script>
    export default {
        props: ['book'],
        methods: {
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
