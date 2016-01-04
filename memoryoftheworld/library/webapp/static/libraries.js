/* ----------------------------------------------------------------------------
 * Global configuration and state
 * ----------------------------------------------------------------------------
 */

var STATE = {
    show_modal: false, // open book modal window
    navigation_direction: 0, // arrow navigation direction (0 - left, 1 - right)
    last_id: '', // uuid of the last fetched book
    query: {
        'text': '',
        'property': '',
        'dvalue': '',
        'dproperty': common.layout.header.dropdown.field,
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

    //
    // maps state field to input html elements
    //
    'state_field_mapping': {
        'text'     : '#text',
        'property' : '#property',
        'dvalue' : '#dropdown',
    },

    //
    // Adds complete toolbar to the top of the page
    //
    'init_toolbar': function () {
        var self = this;
        $('.home-link').click(function () {
            // going back to the homepage lists ALL books in the DB
            // (i.e. resets the search)
            _.each(self.state_field_mapping, function(field, property) {
                $(field).val('');
            });
            window.location.hash = '';
            location.reload();
        });
        $('#search').click(function(e) {
            search.query(true);
            e.stopImmediatePropagation();
            e.preventDefault();
        });
        $('#text').bind('keydown', function(e) {
            // if enter is pressed
            if (e.which == 13) {
                search.query(true);
                e.stopImmediatePropagation();
                e.preventDefault();
            };
        });
        $('#load-more input').click(function() {
            ui.render_page();
        });
        $("#property").change(function () {
            ui.change_autocomplete();
        });
    },

    //
    // enable LOAD MORE button
    //
    'enable_load_more': function () {
        $('#load-more input').removeClass('hidden');
    },

    //
    // disable LOAD MORE button
    //
    'disable_load_more': function () {
        $('#load-more input').addClass('hidden');
    },

    //
    // trigger rendering of the modal by clicking on the main link
    //
    '_show_modal': function(cover) {
        var uuid = $(cover).find('.cover h2 .more_about').attr('rel');
        if (uuid) {
            ui.open_book_modal(uuid, false);
        };
    },

    //
    // opens modal next to the current one
    //
    'open_next_modal': function(current) {
        STATE.navigation_direction = 1;
        var next = current.next();
        if (next.length) {
            if (STATE.last_id !== null && next.next().length == 0) {
                // if there are no more books displayed then
                // try to load more from the server
                ui.render_page();
            };
            this._show_modal(next);
        };
    },

    //
    // opens modal previous to the current one
    //
    'open_prev_modal': function(current) {
        STATE.navigation_direction = 0;
        var prev = current.prev();
        if (prev.length) {
            this._show_modal(prev);
        };
    },

    //
    // opens window for local importing
    //
    'open_import_modal': function() {
        var modal = common.templates.import_modal({});
        $('#modal').empty().append(modal);
        $('#modal').modal();
    },

    //
    // pushes current state to the browser history
    //
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

    //
    // parses search params and initiates search
    // (triggered by onhashchange event)
    //
    'handle_hash_state': function(event, push_state) {
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
        return search.query(push_state);
    }
};

/* --------------------------------------------------------------------------
 * Handles elements rendering
 * -------------------------------------------------------------------------- */

var ui = {

    //
    // pre-render
    //
    'init': function() {
        var self = this;
        nav.init_toolbar();
        if (window.location.hash != '') {
            // first check if there are any params. if any, process them and
            // push state to browser history (true)
            var state = window.location.hash.substr(1);
            nav.handle_hash_state(state, true);
        } else {
            // if not, then just render page as is and push state
            ui.render_page();
            nav.push_to_history();
        };

        // this event will fire when 'back' button is pressed
        $(window).bind('hashchange', function(e) {
            var state = window.location.hash.substr(1);
            // don't push now to state
            nav.handle_hash_state(state, false);
        });
        
        // setup autocomplete
        $.getJSON('autocomplete', {}).done(function(data) {
            if (data === null) {return;}
            STATE.autocomplete = data;
            // populate dropdown
            var _prop = common.layout.header.dropdown.field;
            if (data[_prop].length > 1) {
                $('#dropdown').append(['<option value="" selected>',
                                       String(data[_prop].length),
                                       ' ',
                                       _prop,
                                       ' online',
                                       '</option>'].join(''));
            }
            $.each(data[_prop], function(index, item) {
                $('#dropdown').append(
                    ['<option value="', item, '">', item, '</option>'].join(''));
            });
            self.update_toolbar();
            self.change_autocomplete();
        });
    },

    //
    // initiates the page content rendering by fetching list of books
    // from the server
    //
    'render_page': function (empty) {
        var self = this;
        $('body').addClass('loading');
        $.ajax({type: 'POST',
                url: 'get_books',
                contentType: 'application/json',
                processData: false,
                data: JSON.stringify({'last_id': STATE.last_id, 'query': STATE.query}),
                dataType: 'json',
                success: function (data) {
                    $('body').removeClass('loading');
                    self.parse_response(data, empty);
                }
               });
    },

    //
    // parses response from the server and renders books
    //
    'parse_response': function (data, empty) {
        var self = this;
        // empty main container and render books
        if (empty) {
            $('#content').empty();
        };
        $.each(data['books'], this.render_book);
        STATE.last_id = data['last_id'];
        if (STATE.last_id === null) {
            // disable LOAD MORE button when there are no more results
            nav.disable_load_more();
        } else {
            nav.enable_load_more();
        };
        this.setup_modal();
        if (!is_this_portable()) {
            // mark books that were authored by the one of the authors of the
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
        // display all books by the author whose name is clicked
        $(document).on('click', '.author', function(e) {
            search.by_author($(this).data('authors'));
            e.stopImmediatePropagation();
            e.preventDefault();
        });
        // alert on import click
        $(document).on('click', '.import-to-calibre', function(e) {
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
        // update ui
        self.update_toolbar();
        // init all tooltips
        $('[data-toggle="tooltip"]').tooltip();
    },

    //
    // renders single book
    //
    'render_book': function(i, book) {
        var book_content = common.templates.book_content(
            common.gen_book_data(book));
        // create grid row
        var row = $('#content .row:last');
        if (!row.length) {
            row = $('<div>').addClass('row').appendTo('#content');
        };
        $(row).append(book_content);
    },

    //
    // dynamically update autocomplete data based on the selected property
    //
    'change_autocomplete': function() {
        var source = [];
        var property = $('#property').val();
        if (property == 'authors') {
            source = STATE.autocomplete.authors;
        } else if (property == 'title') {
            source = STATE.autocomplete.titles;
        } else if (property == 'tags') {
            source = STATE.autocomplete.tags;
        } else if (property == 'formats') {
            source = STATE.autocomplete.formats;
        };
        $('#text').typeahead('destroy').typeahead(
            {minLength: 2, highlight: false, hint: false},
            {name: property, source: common.substringMatcher(source)});
    },

    //
    // update toolbar data
    //
    'update_toolbar': function() {
        var cached = STATE.autocomplete;
        if(cached === undefined) {return;}
        
        // update total number of books in the header
        if (cached.num_books > 0) {
            $('#num-books').text(
                cached.num_books + ' books, ' + $('.cover').length + ' shown');
        } else {
            $('#num-books').text('no books');
        };

        // populate dropdown
        var _prop = common.layout.header.dropdown.field;
        if (STATE.query.dvalue) {
            $('#dropdown').val(STATE.query.dvalue);
        }
        else if (cached[_prop].length == 1 ) {
            var first_item = cached[_prop][0];
            var suffix = '';
            $('#dropdown').val(first_item);
            if (is_this_portable()) {
                $('#dropdown').prop('disabled', 'disabled');
                // if single item then update title page
                if (_prop == 'librarians') {
                    suffix = "'s library";
                    if ($.inArray(first_item.slice(-1), ['s', 'z']) >= 0) {
                        suffix = "' library";
                    };
                }
                document.title = first_item + suffix;
            };
        };
    },

    //
    // sets up modal book window
    //
    'setup_modal': function () {
        var self = this;
        $('.more_about').click(function(e) {
            var uuid = $(this).attr('rel');
            self.open_book_modal(uuid, true);
            e.stopImmediatePropagation();
            e.preventDefault();
        });
    },

    //
    // opens book info inside modal window
    //
    'open_book_modal': function(uuid, firstRun) {
        var self = this;
        $.getJSON('book', {uuid: uuid}).done(function( book ) {
            var this_book = $(['.col .cover h2 [rel="',
                               book.uuid,
                               '"].more_about'].join('')).parents('.col');
            var modal = common.templates.book_modal(
                common.gen_book_data(book));
            $('#modal').empty();
            $('#modal').off('keydown');
            $('#modal').keydown(function(e) {
                if (this_book.length) {
                    // navigate right
                    if (e.which === 39) {
                        nav.open_next_modal(this_book);
                    }
                    // navigate left
                    else if (e.which === 37) {
                        nav.open_prev_modal(this_book);
                    }
                    // exit
                    else if (e.which === 27) {
                        $('#modal').modal('hide');
                    };
                };
            });
            var mc = new Hammer(document.getElementById('modal'));
            mc.on("swipeleft swiperight", function(ev) {
                if (this_book.length) {
                    // navigate right
                    if (ev.type == 'swipeleft') {
                        nav.open_next_modal(this_book);
                    }
                    // navigate left
                    else if (ev.type == 'swiperight') {
                        nav.open_prev_modal(this_book);
                    };
                };
            });
            $('#modal').append(modal);
            // open modal only on first click
            if (firstRun) {
                $('#modal').modal();
            };
        });
    }
};

/* --------------------------------------------------------------------------
 * Handles search
 * -------------------------------------------------------------------------- */

var search = {

    //
    // initiate search by populating STATE and calling render_page
    // push_state param determines whether state should be pushed to the
    // browser history
    //
    'query': function (push_state) {
        // reset last_id for search
        STATE.last_id = null;
        // fill STATE
        STATE.query.text = $('#text').val();
        STATE.query.property = $('#property').val();
        STATE.query.dvalue = $('#dropdown').val();
        // if user initiated action (e.g. click for search)
        if (push_state) {
            nav.push_to_history();
        };
        ui.render_page(true);
    },

    //
    // search by author only
    //
    'by_author': function (author) {
        $('#text').val(author);
        $('#property').val('authors');
        this.query(true);
    }
};

/* --------------------------------------------------------------------------*/

var init_page = function () {
    
};

/* --------------------------------------------------------------------------*/

$(document).ready(function () {
    localCalibre.done(function(success) {
        ui.init();
    });
});
