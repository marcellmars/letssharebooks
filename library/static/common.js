console.log('---------');
console.log($('#book-permalink-tmpl'));

var common = {
    'templates': {
        'book_permalink': _.template($('#book-permalink-tmpl').text().trim()),
        'book_content'  : _.template($('#book-content-tmpl').text().trim()),
        'book_modal'    : _.template($('#book-modal-tmpl').text().trim()),
        'import_modal'  : _.template($('#import-modal-tmpl').text().trim())
    },
    
    // Prepare book data for rendering
    'gen_book_data': function(book) {
        book.application_id = '';
        var format = book.formats[0];
        var metadata_urls = [
            book.title.replace(/\?/g, ''),
            [book.prefix_url, book.format_metadata[format].dir_path, 'metadata.opf'].join(''),
            [book.prefix_url, book.format_metadata[format].dir_path, 'cover.jpg'].join('')];
        $.each(book.formats, function(i, format) {
            metadata_urls.push([book.prefix_url + book.format_metadata[format].file_path]);
        });
        return {
            'book': book,
            'metadata_urls': encodeURIComponent(metadata_urls.join('__,__'))
        };
    }
};