/** localCalibre manages connection to local calibre server */
var localCalibre = (function () {
    var connected = false;
    var localLibrary = null;
    var baseGIFLocation = 'http://localhost:56665/';
    /** connects to local calibre server with callback(success=true|false) */
    var connect = function(callback) {
        // try to locate 0.gif
        $('<img src="' + baseGIFLocation + '/0.gif" />')
        // 0.gif is available
        .load(function() {
            console.log('Found local calibre server.');
		        connected = true;
            // fetch all active libraries
            $.getJSON('get_catalogs', {}).done(function(catalogs) {
                var count_local_gif_err = 0;
                // locate active libraries on local calibre server
                $.each(catalogs, function (i, catalog) {
                    if (localLibrary) {return};
                    var lib_gif = ['<img src="',
                                   baseGIFLocation,
                                   '/',
                                   catalog.library_uuid,
                                   '.gif" />'].join('');
                    $(lib_gif).load(function() {
                        console.log('>>>> ', catalog.library_uuid);
                        localLibrary = catalog.library_uuid;
                        callback(true);
                    })
                    .error(function() {
                        count_local_gif_err += 1;
                        console.log('!!!! ', catalog.library_uuid);
                        if (count_local_gif_err === catalogs.length) {
                            callback(false);
                        };
	                  });
                });
            });
	      })
        // 0.gif is not available
        .error(function() {
            console.log('Local calibre server not available');
            callback(false);
	      });
    };
    return {
        done: function(callback) {
            connect(callback);
        },
        is_connected: function() {
            return connected;
        }
    };
})();
