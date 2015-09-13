//
// localCalibre manages connection to local calibre server
//

var localCalibre = (function () {
    var connected = false;
    var localLibrary = null;
    var baseGIFLocation = 'http://localhost:56665/';

    //
    // connects to local calibre server with callback(success=true|false)
    //
    var connect = function(callback) {
        // don't connect when serving with file://...
        if (document.location.origin === "file://") {
            callback(false);
            return;
        }
        // first, try to locate 0.gif
        $('<img src="' + baseGIFLocation + '0.gif" />')
        // 0.gif is available
        .load(function() {
		        connected = true;
            // fetch all active libraries - we want to check if any of these
            // is served also on local calibre instance
            $.getJSON('get_catalogs', {}).done(function(catalogs) {
                var count_local_gif_err = 0;
                // locate active libraries on local calibre server by
                // iterating over catalogs and loading corresponding gif
                $.each(catalogs, function (i, catalog) {
                    if (localLibrary) { return };

                    local_library_uuid = catalog.library_uuid;
                    // remove portable tags
                    if (catalog.library_uuid.indexOf("p::") == 0) {
                        local_library_uuid = catalog.library_uuid.slice(3,-3);
                    }
                    // construct and load gif
                    var lib_gif = ['<img src="', baseGIFLocation,
                                   local_library_uuid, '.gif" />'].join('');
                    $(lib_gif).load(function() {
                        localLibrary = catalog.library_uuid;
                        callback(true);
                    })
                    // count missing gifs
                    .on('error', function() {
                        count_local_gif_err += 1;
                        if (count_local_gif_err === catalogs.length) {
                            callback(false);
                        };
	                  });
                });
            });
	      })
        // 0.gif is not available
       .on('error', function() {
           callback(false);
	     });
    };
    return {
        done: function(callback) {
            connect(callback);
        },
        /** returns true if there is local calibre with LSB that
          * has opened library with the given uuid */
        isSharing: function(uuid) {
            return connected && (localLibrary === uuid);
        },
        /** returns true if import links for books should be rendered */
        showImportLinks: function(uuid) {
            return connected && (localLibrary != uuid);
        }
    };
    })();
