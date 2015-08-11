/* ----------------------------------------------------------------------------
 * Global configuration and state
 * ----------------------------------------------------------------------------
 */

var ITEMS_PER_PAGE = 16;
var GRID_ROW_SIZE = 4;

var STATE = {
    show_modal: false, // open book modal window
    navigation_direction: 0, // arrow navigation direction (0 - left, 1 - right)
    last_id: '', // uuid of the last fetched book
    query: {
        'text': '',
        'property': '',
        'librarian': '',
    }
};

/* ----------------------------------------------------------------------------
 * This differentiates webapp and portable libraries. Add PORTABLE variable
 * to portable library (e.g. var PORTABLE = true).
 * ----------------------------------------------------------------------------
 */

var is_this_portable = function() {
    return !_.isUndefined(window.PORTABLE); 
};

/* --------------------------------------------------------------------------
 * Handles navigation: has external dependencies, primarily STATE
 * -------------------------------------------------------------------------- */

var nav = {

    // maps state field to input html elements
    'state_field_mapping': {
        'text'     : '#text',
        'property' : '#property',
        'librarian': '#librarian'
    },

    // Adds complete toolbar to the top of the page
    'init_toolbar': function () {
        var self = this;
        $('#home').click(function () {
            // going back to the homepage lists ALL books in the DB
            // (i.e. resets the search)
            _.each(self.state_field_mapping, function(field, property) {
                $(field).val('');
            });
            window.location.hash = '';
            location.reload();
        });
        $('#search').click(function() {
            search.query();
        });
        $('#text').bind('keydown', function(e) {
            // if enter is pressed
            if(e.which == 13) {
                search.query();
            }
        });
        $('#load-more input').click(function() {
            ui.render_page();
        });
        $("#property").change(function () {
            ui.change_autocomplete();
        });
        
    },

    'disable_load_more': function () {
        $('#load-more input').remove();
    },

    // infinite scroll
    'init_scroll': function() {
        $(window).scroll(function () {
            if ($(window).scrollTop() + screen.height >= $(document).height()) {
                ui.render_page();
            };
        });
    },
    
    // trigger rendering of the modal by clicking on the main link
    '_show_modal': function(el) {
        el.find('h2 .more_about').click();
    },
    
    // opens modal next to the current one
    'open_next_modal': function(current) {
        STATE.navigation_direction = 1;
        var next = current.next();
        // try to find next book in the same row
        if (next.length) {
            this._show_modal(next);
        } else {
            // try to move to the row below
            col = current.parents('.row').next().find('.col:first');
            if (col.length) {
                this._show_modal(col);
            };
        };
    },
    
    // opens modal previous to the current one
    'open_prev_modal': function(current) {
        STATE.navigation_direction = 0;
        var prev = current.prev();
        // try to find previous book in the same row
        if (prev.length) {
            this._show_modal(prev);
        } else {
            // try to move to the row above
            col = current.parents('.row').prev().find('.col:last');
            if (col.length) {
                this._show_modal(col);
            };
        };
    },

    // opens window for local importing
    'open_import_modal': function() {
        var modal = $(common.templates.import_modal({}));
        modal.dialog(ui.modal_defaults);
        modal.dialog('open');
    },

    // handles onload browser history
    'push_to_history': function() {
        var data = {};
        _.each(this.state_field_mapping, function(field, property) {
            // serialize only non-empty fields
            var field_value = $(field).val();
            if (field_value) {
                data[property] = field_value;
            };
        });
        var serialized = $.param(data);
        history.pushState(data, '', '#' + serialized);
    },

    // parses params and dispaches on search
    'handle_hash_state': function(event) {
        var deserialized = $.deparam(event);
        if (_.isEmpty(deserialized)) { return };
        if (!_.isUndefined(deserialized.librarian)) {
            $('#librarian').append(['<option value="', deserialized.librarian,
                                    '">', deserialized.librarian,
                                    '</option>'].join('')); 
        };
        // fill the visible query fields
        _.each(this.state_field_mapping, function(field, property) {
            $(field).val(deserialized[property]);
        });
        return search.query();
    },
};

/* --------------------------------------------------------------------------
 * Handles elements rendering
 * -------------------------------------------------------------------------- */

var ui = {

    // fetches list of book from the server
    'render_page': function (empty) {
        nav.push_to_history();
        var self = this;
        $.ajax({type: 'POST',
                url: 'get_books',
                contentType: 'application/json',
                processData: false,
                data: JSON.stringify(STATE),
                dataType: 'json',
                success: function (data) {
                    self.parse_response(data, empty);
                }
         });
    },

    // parses response from the server and renders books
    'parse_response': function (data, empty) {
        var self = this;
        // empty main container and render books
        if (empty) {
            $('#content').empty();
        };
        $.each(data['books'], this.render_book);
        STATE.last_id = data['last_id'];
        if (STATE.last_id === null) {
            nav.disable_load_more();
        };
        // update ui
        self.update_toolbar(data);
        this.setup_modal();
        if (is_this_portable()) {
            // mark books that were authord by the one of the authors of the
            // currently selected book
            $('.cover').hover(
                function() {
                    var selected_librarian = $(this).attr('rel');
                    $.each($('.cover').not($(this)), function(i) {
                        var cover = $(this);
                        var librarian = cover.attr('rel');
                        if (selected_librarian == librarian) {
                            cover.find('.cover-highlight').show();
                        }
                    });
                }, function() {
                    $('.cover-highlight').hide();
                }
            );
        };
        // alert on import click
        $('.import').click(function(e) {
            nav.open_import_modal();
        });
        // directly open the dialog window if show_modal
        if (STATE.show_modal) {
            var book_index = 0; // show first if navigation_direction is right
            if (STATE.navigation_direction === 0) {
                book_index = data['books'].length - 1;
            }
            var book_uuid = data['books'][book_index].uuid;
            $('.cover h2 [rel="' + book_uuid  +  '"].more_about').click();
        };
    },

    // renders single book
    'render_book': function(i, book) {
        $(document).on('click', '.author', function(e) {
            search.by_author($(this).data('authors'));
        });
        var book_content = gen_book_content(book);
        // find last row in the css grid
        var row = $('#content .row:last');
        // start new row if last one has GRID_ROW_SIZE elements
        if (i % GRID_ROW_SIZE == 0) {
            row = $('<div>').addClass('row').appendTo('#content');
        };
        $(row).append(book_content);
    },

    'change_autocomplete': function() {
        var source = [];
        var property = $('#property').val();
        if (property == 'authors') {
            source = STATE.autocomplete.authors;
        } else if (property == 'title') {
            source = STATE.autocomplete.titles;
        };
        $('#text').autocomplete({source: source, minLength:2});
    },

    'update_toolbar': function(data) {
        STATE.autocomplete = {
            authors: data['authors'],
            titles: data['titles']
        };
        if (is_this_portable()) {
            var metadata = this.generate_metadata(data['books']);
            STATE.autocomplete = {
                authors: metadata['authors'],
                titles: metadata['titles']
            };
        };
        this.change_autocomplete();
        
        $('#librarian').empty();
        if (data['librarians'].length > 1) {
            $('#librarian').append(['<option value="" selected>',
                                    String(data['librarians'].length),
                                    ' librarians online</option>'].join(''));
        } 
        $.each(data['librarians'], function(index, item) {
            $('#librarian').append(['<option value="',
                                    item,
                                    '"',
                                    '>',
                                    item,
                                    '</option>'].join('')); 
        });
        if (STATE.query.librarian) {
            $('#librarian').val(STATE.query.librarian);
        } else if (data['librarians'].length == 1 ) {
            if (is_this_portable()) {
                // if single librarian then update dropdown and title page
                var librarian = data['librarians'][0];
                var sufix = "'s Library";
                $('#librarian').val(librarian);
                if ($.inArray(librarian.slice(-1), ['s', 'z']) >= 0) {
                    sufix = "' Library";
                };
                document.title = librarian + sufix;
            } else {
                $('#librarian').val(data['librarians'][0]);
            };
        };
    },

    
    // generate distinct list of authors, titles and librarians
    'generate_metadata': function(books) {
        var sadd = function(s, v) {
            if ($.inArray(v, s) == -1) {
                s.push(v);
            };
        };
        var metadata = {
            'authors': [],
            'titles': [],
        };
        $.each(books, function(i, book) {
            var authors = book.authors;
            $.each(authors, function(j, author) {
                sadd(metadata['authors'], author);
            });
            sadd(metadata['titles'], book.title);
        });
        return metadata;
    },

    // modal default conf
    'modal_defaults': {
        autoOpen: false,
        modal: true,
        minHeight: 600,
        minWidth: 800,
        position: { my: 'center top', at: 'center top'},
        closeOnEscape: true
    },

    // sets up modal book window
    'setup_modal': function () {
        var self = this;
        $('.more_about').click(function(e) {
            var uuid = $(this).attr('rel');
            $.getJSON('book', {uuid: uuid}).done(function( book ) {
                var modal = $(gen_book_modal(book));
                var _conf = self.modal_defaults;
                _conf.open = function() {
                    $('.ui-widget-overlay').bind('click', function() {
                        modal.dialog('close');
                    })
                };
                _conf.close = function() {
                    STATE.show_modal = false;
                };
                modal.dialog(_conf);
                $(modal).find('.import').click(function(e) {
                    nav.open_import_modal();
                });
                modal.dialog("open");
                // navigate modals with left/right arrows
                $(modal).keydown(function(e) {
                    var this_book = $(['.col .cover h2 [rel="',
                                       book.uuid,
                                       '"].more_about'].join('')).parents('.col');
                    if (this_book.length) {
                        // navigate right
                        if (e.which === 39) {
                            modal.dialog('close');
                            nav.open_next_modal(this_book);
                        }
                        // navigate left
                        else if (e.which === 37) {
                            modal.dialog('close');
                            nav.open_prev_modal(this_book);
                        };
                    };
                });
            });
            e.preventDefault();
        });
    }
};

/* --------------------------------------------------------------------------
 * Handles search
 * -------------------------------------------------------------------------- */

var search = {

    'query': function () {
        // reset last_id for search
        STATE.last_id = null;
        // fill STATE
        STATE.query.text = $('#text').val();
        STATE.query.property = $('#property').val();
        STATE.query.librarian = $('#librarian').val();
        ui.render_page(true);
    },
    
    'by_author': function (author) {
        $('#text').val(author);
        $('#property').val('authors');
        this.query();
    }
};

/* --------------------------------------------------------------------------*/

var init_page = function () {
    nav.init_toolbar();
    // nav.init_scroll();
    /* do not display tooltip for modal close button (it gets automatically
     displayed */
    //$(document).tooltip({items: '*:not(.ui-dialog-titlebar-close)'});
    if (window.location.hash != '') {
      var state = window.location.hash.substr(1);
      nav.handle_hash_state(state);
    } else {
      ui.render_page();
    }
    window.onpopstate = function(e) {
      var state = window.location.hash.substr(1);
      nav.handle_hash_state(state);
    };
};

/* --------------------------------------------------------------------------*/

var init_template_data = function() {

    /** Renders book inside grid */
    window.gen_book_content = function (book) {
        return common.templates.book_content(common.gen_book_data(book));
    };

    /** Renders book modal */
    window.gen_book_modal = function (book) {
        return common.templates.book_modal(common.gen_book_data(book));
    };
};

/* --------------------------------------------------------------------------*/

$(document).ready(function () {
    $(document).ajaxStart(function () { 
        $('body').addClass("loading"); 
    });
    $(document).ajaxStop(function () { 
        $('body').removeClass("loading"); 
    });
    init_template_data();
    // try to connect to local calibre server and init page when done
    if (is_this_portable()) {
            init_page();
    } else {
        localCalibre.done(function(success) {
            init_page();
        })
    };
});