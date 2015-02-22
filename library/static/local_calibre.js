/** localCalibre manages connection to local calibre server */
var localCalibre = (function () {
    var connected = false;
    var gifLocation = 'http://localhost:56665/0.gif';
    /** connects to local calibre server with callback(success=true|false) */
    var connect = function(callback) {
        $('<img src="' + gifLocation + '" />').load(function() {
            console.log('Found local calibre server.');
		        connected = true;
            callback(true);
	      })
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
