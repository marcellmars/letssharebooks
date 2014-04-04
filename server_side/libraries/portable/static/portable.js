$(document).ready(function () {
    /* these are portable-specific overrides */

    window.gen_book_string_parts = function (base_url, format, book) {
        return {
            'base_url': '/get/',
            'format': '/',
            'book': book,
            'portable_book': ''
        }
    };

    window.gen_book_content = function (base_url, book, authors, formats) {
        return {
            'base_url': base_url,
            'book': book,
            'book_title_stripped': ' ' + book.title.replace(/\?/g, ''),
            'authors': authors,
            'formats': formats,
            'get_cover': '/get/cover',
            'get_opf' : '/get/opf/',
            'portable_cover': '',
            'portable_opf': ''
        }
    };

    window.gen_book_modal = function (base_url, book, formats) {
        return {
            'base_url': base_url,
            'book': book,
            'book_title_stripped': ' ' + book.title.replace(/\?/g, ''),
            'formats': formats,
            'get_cover': '/get/cover/',
            'get_opf': '/get/opf/',
            'portable_cover': '',
            'portable_opf': ''
        }
    };
});