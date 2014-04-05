$(document).ready(function () {
    /* these are portable-specific overrides */

    window.gen_book_string_parts = function (base_url, format, book) {
        console.log("+ + + + + + + get_book_string_parts + + + + + + + +");
        console.log(format);
        book.application_id = '';
        var file_path = book.format_metadata[format].path
        directory_path = ""
        directory = file_path.split("/").slice(-3,-1)
        directory.forEach(function(el){directory_path += el + "/"});
        file_name = file_path.split("/").slice(-1);
        return {
            'base_url': '',
            'format': '',
            'book': book,
            'portable_book': directory_path + file_name,
            'portable_format': format
        }
    };

    window.gen_book_content = function (base_url, book, authors, formats) {
        console.log("+ + + + + + + gen_book_content + + + + + + + +");
        console.log(book);
        book.application_id = '';
        format = book.formats[0]
        file_path = book.format_metadata[format].path
        directory_path = ""
        directory = file_path.split("/").slice(-3,-1)
        directory.forEach(function(el){directory_path += el + "/"});
        file_cover = "cover.jpg";
        file_opf = "metadata"
        return {
            'base_url': '',
            'book': book,
            'book_title_stripped': '',
            'authors': authors,
            'formats': formats,
            'get_cover': '',
            'get_opf' : '',
            'portable_cover': directory_path + file_cover,
            'portable_opf': directory_path + file_opf
        }
    };

    window.gen_book_modal = function (base_url, book, formats) {
        console.log("+ + + + + + + gen_book_modal + + + + + + + +");
        book.application_id = '';
        console.log(formats);
        format = book.formats[0]
        file_path = book.format_metadata[format].path
        directory_path = ""
        directory = file_path.split("/").slice(-3,-1)
        directory.forEach(function(el){directory_path += el + "/"});
        file_cover = "cover.jpg";
        file_opf = "metadata"

        return { 
            'base_url': '',
            'book': book,
            'book_title_stripped': '',
            'formats': formats,
            'get_cover': '',
            'get_opf': '',
            'portable_cover': directory_path + file_cover,
            'portable_opf': directory_path + file_opf,
        }
    };
});
