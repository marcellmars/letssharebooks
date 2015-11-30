var common = {

    //
    // Initialize js/html templates
    //
    
    'templates': {
        'book_permalink':
            _.template($('#book-permalink-tmpl').text().trim()),
        'book_downloads':
            _.template($('#book-downloads-tmpl').text().trim()),
        'book_content':
            _.template($('#book-content-tmpl').text().trim()),
        'book_modal':
            _.template($('#book-modal-tmpl').text().trim()),
        'book_modal_attr_title':
            _.template($('#book-modal-attr-title-tmpl').text().trim()),
        'import_modal':
            _.template($('#import-modal-tmpl').text().trim()),
        'external_link':
            _.template($('#external-link-tmpl').text().trim()),
        'search_properties':
            _.template($('#search-properties-tmpl').text().trim()),
    },

    //
    // Customization for different libraries
    //
    // * define external link in the header
    // * select which book properties will be rendered
    //
    
    'layout': {
        
        'header': {

            'link': {
                'text': 'MEMORY OF THE WORLD',
                'href': 'https://www.memoryoftheworld.org'
            },

            'dropdown': {
                'field': 'librarians',
            },
            
            'search': {
                'properties_order': [
                    'authors', 'title', 'tags', 'pubdate', 'formats', 'all'
                ],
                'properties': {
                    'authors': {
                        'text': 'Author',
                        'placeholder': 'type here...'
                    },
                    'title': {
                        'text': 'Title',
                        'placeholder': 'type here...'
                    },
                    'tags': {
                        'text': 'Tag',
                        'placeholder': 'type here...'
                    },
                    'pubdate': {
                        'text': 'Date',
                        'placeholder': 'e.g. "2013-12-22"'
                    },
                    'formats': {
                        'text': 'Format',
                        'placeholder': 'e.g. "pdf"'
                    },
                    'all': {
                        'text': 'All metadata',
                        'placeholder': 'type here...'
                    },
                }
            }
        },
        
        // book permalink page
        'book-permalink': {
            'properties': [
                
                {'name': 'Title',
                 'render': function(book) {return book.title;},
                 'if_display': function(book) {return true;}},
                
                {'name': 'Authors',
                 'render': function(book) {
                     return book.authors.join(', ');
                 },
                 'if_display': function(book) {return true;}},
                
                {'name': 'Publisher',
                'render': function(book) {return book.publisher;},
                 'if_display': function(book) {
                     return book.publisher !== null;
                 }},
                
                {'name': 'Download',
                 'render': function(book) {
                     return common.templates.book_downloads({book: book});
                 },
                 'if_display': function(book) {
                     return book.formats[0] != '0';
                 }},
                
                {'name': 'About',
                 'render': function(book) {return book.comments;},
                 'if_display': function(book) {
                     return book.comments !== null;
                 }},
            ]
        },
        
        // book modal (and default)
        'book-modal': {
            'properties': [
                
                {'name': 'Title',
                 'render': function(book) {
                     return common.templates.book_modal_attr_title({book: book});
                 },
                 'if_display': function(book) {return true;}},
                
                {'name': 'Authors',
                 'render': function(book) {
                     return book.authors.join(', ');
                 },
                 'if_display': function(book) {return true;}},
                
                {'name': 'Publisher',
                'render': function(book) {return book.publisher;},
                 'if_display': function(book) {
                     return book.publisher !== null;
                 }},
                
                {'name': 'Download',
                 'render': function(book) {
                     return common.templates.book_downloads({book: book});
                 },
                 'if_display': function(book) {
                     return book.formats[0] != '0';
                 }},
                
                {'name': 'About',
                 'render': function(book) {return book.comments;},
                 'if_display': function(book) {
                     return book.comments !== null;
                 }},
            ]
        }
    },

    //
    // Do basic customizations
    //
    'init_custom': function() {
        // external link definition
        $('#external-link').append(common.templates.external_link(
            common.layout.header.link));
        // search
        $('#search-form #property').append(common.templates.search_properties(
            common.layout.header.search));
        // property placeholder
        $("#search-form #property").change(function () {
            var props = common.layout.header.search.properties;
            var property = $(this).val();
            $('#text').attr('placeholder',
                            props[property].placeholder);
        });
    },

    //
    // Prepare book data for rendering
    //
    'gen_book_data': function(book, target) {
        if (_.isUndefined(target)) {
            target = 'book-modal';
        };
        book.application_id = '';
        var format = book.formats[0];
        var metadata_urls = [
            book.title.replace(/\?/g, ''),
            [book.prefix_url,
             book.format_metadata[format].dir_path,
             'metadata.opf'].join(''),
            [book.prefix_url,
             book.format_metadata[format].dir_path,
             'cover.jpg'].join('')];
        $.each(book.formats, function(i, format) {
            if (book.prefix_url === undefined) {
                book.prefix_url = document.location.origin + "/";
            };
            metadata_urls.push(
                [book.prefix_url + book.format_metadata[format].file_path]);
        });
        return {
            'book': book,
            'properties': this.layout[target].properties,
            'metadata_urls': encodeURIComponent(metadata_urls.join('__,__'))
        };
    },

    //
    // Detect mobile browser
    // http://stackoverflow.com/questions/11381673/detecting-a-mobile-browser
    // 

    detect_mobile: function() {
        var check = false;
        (function(a){if(/(android|bb\d+|meego).+mobile|avantgo|bada\/|blackberry|blazer|compal|elaine|fennec|hiptop|iemobile|ip(hone|od)|iris|kindle|lge |maemo|midp|mmp|mobile.+firefox|netfront|opera m(ob|in)i|palm( os)?|phone|p(ixi|re)\/|plucker|pocket|psp|series(4|6)0|symbian|treo|up\.(browser|link)|vodafone|wap|windows ce|xda|xiino/i.test(a)||/1207|6310|6590|3gso|4thp|50[1-6]i|770s|802s|a wa|abac|ac(er|oo|s\-)|ai(ko|rn)|al(av|ca|co)|amoi|an(ex|ny|yw)|aptu|ar(ch|go)|as(te|us)|attw|au(di|\-m|r |s )|avan|be(ck|ll|nq)|bi(lb|rd)|bl(ac|az)|br(e|v)w|bumb|bw\-(n|u)|c55\/|capi|ccwa|cdm\-|cell|chtm|cldc|cmd\-|co(mp|nd)|craw|da(it|ll|ng)|dbte|dc\-s|devi|dica|dmob|do(c|p)o|ds(12|\-d)|el(49|ai)|em(l2|ul)|er(ic|k0)|esl8|ez([4-7]0|os|wa|ze)|fetc|fly(\-|_)|g1 u|g560|gene|gf\-5|g\-mo|go(\.w|od)|gr(ad|un)|haie|hcit|hd\-(m|p|t)|hei\-|hi(pt|ta)|hp( i|ip)|hs\-c|ht(c(\-| |_|a|g|p|s|t)|tp)|hu(aw|tc)|i\-(20|go|ma)|i230|iac( |\-|\/)|ibro|idea|ig01|ikom|im1k|inno|ipaq|iris|ja(t|v)a|jbro|jemu|jigs|kddi|keji|kgt( |\/)|klon|kpt |kwc\-|kyo(c|k)|le(no|xi)|lg( g|\/(k|l|u)|50|54|\-[a-w])|libw|lynx|m1\-w|m3ga|m50\/|ma(te|ui|xo)|mc(01|21|ca)|m\-cr|me(rc|ri)|mi(o8|oa|ts)|mmef|mo(01|02|bi|de|do|t(\-| |o|v)|zz)|mt(50|p1|v )|mwbp|mywa|n10[0-2]|n20[2-3]|n30(0|2)|n50(0|2|5)|n7(0(0|1)|10)|ne((c|m)\-|on|tf|wf|wg|wt)|nok(6|i)|nzph|o2im|op(ti|wv)|oran|owg1|p800|pan(a|d|t)|pdxg|pg(13|\-([1-8]|c))|phil|pire|pl(ay|uc)|pn\-2|po(ck|rt|se)|prox|psio|pt\-g|qa\-a|qc(07|12|21|32|60|\-[2-7]|i\-)|qtek|r380|r600|raks|rim9|ro(ve|zo)|s55\/|sa(ge|ma|mm|ms|ny|va)|sc(01|h\-|oo|p\-)|sdk\/|se(c(\-|0|1)|47|mc|nd|ri)|sgh\-|shar|sie(\-|m)|sk\-0|sl(45|id)|sm(al|ar|b3|it|t5)|so(ft|ny)|sp(01|h\-|v\-|v )|sy(01|mb)|t2(18|50)|t6(00|10|18)|ta(gt|lk)|tcl\-|tdg\-|tel(i|m)|tim\-|t\-mo|to(pl|sh)|ts(70|m\-|m3|m5)|tx\-9|up(\.b|g1|si)|utst|v400|v750|veri|vi(rg|te)|vk(40|5[0-3]|\-v)|vm40|voda|vulc|vx(52|53|60|61|70|80|81|83|85|98)|w3c(\-| )|webc|whit|wi(g |nc|nw)|wmlb|wonu|x700|yas\-|your|zeto|zte\-/i.test(a.substr(0,4)))check = true})(navigator.userAgent||navigator.vendor||window.opera);
        this.is_mobile = check;
    },

    substringMatcher: function(strs) {
        return function findMatches(q, cb) {
            var matches, substringRegex;

            // an array that will be populated with substring matches
            matches = [];

            // regex used to determine if a string contains the substring `q`
            substrRegex = new RegExp(q, 'i');

            // iterate through the pool of strings and for any string that
            // contains the substring `q`, add it to the `matches` array
            $.each(strs, function(i, str) {
                if (substrRegex.test(str)) {
                    matches.push(str);
                }
            });

            cb(matches);
        };
    }
};

common.detect_mobile();
common.init_custom();
