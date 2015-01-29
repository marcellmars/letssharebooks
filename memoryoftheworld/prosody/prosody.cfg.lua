-- Prosody Example Configuration File
--
-- Information on configuring Prosody can be found on our
-- website at http://prosody.im/doc/configure
--
-- Tip: You can check that the syntax of this file is correct
-- when you have finished by running: luac -p prosody.cfg.lua
-- If there are any errors, it will let you know what and where
-- they are, otherwise it will keep quiet.
--
-- The only thing left to do is rename this file to remove the .dist ending, and fill in the
-- blanks. Good luck, and happy Jabbering!

-- run_as_root = true

---------- Server-wide settings ----------
-- Settings in this section apply to the whole server and are the default settings
-- for any virtual hosts

-- This is a (by default, empty) list of accounts that are admins
-- for the server. Note that you must create the accounts separately
-- (see http://prosody.im/doc/creating_accounts for info)
-- Example: admins = { "user1@example.com", "user2@example.net" }
admins = {"biblibothekar@xmpp.memoryoftheworld.org" }
--admins = {}
-- Enable use of libevent for better performance under high load
-- For more information see: http://prosody.im/doc/libevent
--use_libevent = true;

-- This is the list of modules Prosody will load on startup.
-- It looks for mod_modulename.lua in the plugins folder, so make sure that exists too.
-- Documentation on modules can be found at: http://prosody.im/doc/modules
modules_enabled = {

	-- Generally required
		"roster"; -- Allow users to have a roster. Recommended ;)
		"saslauth"; -- Authentication for clients and servers. Recommended if you want to log in.
		"tls"; -- Add support for secure TLS on c2s/s2s connections
		"dialback"; -- s2s dialback support
		"disco"; -- Service discovery

	-- Not essential, but recommended
		"private"; -- Private XML storage (for room bookmarks, etc.)
		"vcard"; -- Allow users to set vCards
		--"privacy"; -- Support privacy lists
		--"compression"; -- Stream compression (Debian: requires lua-zlib module to work)

	-- Nice to have
		"legacyauth"; -- Legacy authentication. Only used by some old clients and bots.
		"version"; -- Replies to server version requests
		"uptime"; -- Report how long server has been running
		"time"; -- Let others know the time here on this server
		"ping"; -- Replies to XMPP pings with pongs
		"pep"; -- Enables users to publish their mood, activity, playing music and more
		"register"; -- Allow users to register on this server using a client and change passwords
		"adhoc"; -- Support for "ad-hoc commands" that can be executed with an XMPP client

	-- Admin interfaces
		"admin_adhoc"; -- Allows administration via an XMPP client that supports ad-hoc commands
		"admin_telnet"; -- Opens telnet console interface on localhost port 5582

	-- Other specific functionality
		"bosh"; -- Enable BOSH clients, aka "Jabber over HTTP"
		--"httpserver"; -- Serve static files from a directory over HTTP
		--"groups"; -- Shared roster support
		--"announce"; -- Send announcement to all online users
		--"welcome"; -- Welcome users who register accounts
		--"watchregistrations"; -- Alert admins of registrations
		--"motd"; -- Send a message to users when they log in
	-- Debian: do not remove this module, or you lose syslog
	-- support
		"posix"; -- POSIX functionality, sends server to background, enables syslog, etc.
		--"auth_anonymous";
		"http";
};

-- These modules are auto-loaded, should you
-- (for some mad reason) want to disable
-- them then uncomment them below
modules_disabled = {

	-- "presence"; -- Route user/contact status information
	--
	-- "message"; -- Route messages
	-- "iq"; -- Route info queries
	-- "offline"; -- Store offline messages
};

-- Disable account creation by default, for security
-- For more information see http://prosody.im/doc/creating_accounts
--allow_registration = true;

-- Debian:
--   send the server to background.
--
daemonize = false;

-- Debian:
--   Please, don't change this option since /var/run/prosody/
--   is one of the few directories Prosody is allowed to write to
--
pidfile = "prosody.pid";

-- These are the SSL/TLS-related settings. If you don't want
-- to use SSL/TLS, you may comment or remove this

ssl = {
		key = "/etc/prosody/certs/wildcard_memoryoftheworld.org_20130714.key";
		--certificate = "/etc/prosody/certs/example.com.crt";
		certificate = "/etc/prosody/certs/wildcard_memoryoftheworld.org_20130714_combined.crt";
}
-- Only allow encrypted streams? Encryption is already used when
-- available. These options will cause Prosody to deny connections that
-- are not encrypted. Note that some servers do not support s2s
-- encryption or have it disabled, including gmail.com and Google Apps
-- domains.

c2s_require_encryption = true;
s2s_require_encryption = true;

-- Select the authentication backend to use. The 'internal' providers
-- use Prosody's configured data storage to store the authentication data.
-- To allow Prosody to offer secure authentication mechanisms to clients, the
-- default provider stores passwords in plaintext. If you do not trust your
-- server please see http://prosody.im/doc/modules/mod_auth_internal_hashed
-- for information about using the hashed backend.

authentication = "internal_hashed"

-- Select the storage backend to use. By default Prosody uses flat files
-- in its configured data directory, but it also supports more backends
-- through modules. An "sql" backend is included by default, but requires
-- additional dependencies. See http://prosody.im/doc/storage for more info.

--storage = "sql" -- Default is "internal" (Debian: "sql" requires one of the
-- lua-dbi-sqlite3, lua-dbi-mysql or lua-dbi-postgresql packages to work)

-- For the "sql" backend, you can uncomment *one* of the below to configure:
--sql = { driver = "SQLite3", database = "prosody.sqlite" } -- Default. 'database' is the filename.
--sql = { driver = "MySQL", database = "prosody", username = "prosody", password = "secret", host = "localhost" }
--sql = { driver = "PostgreSQL", database = "prosody", username = "prosody", password = "secret", host = "localhost" }

-- Logging configuration
-- For advanced logging see http://prosody.im/doc/logging
--
-- Debian:
--  Logs info and higher to /var/log
--  Logs errors to syslog also
log = {
	--{ to = "console"};
	-- Log files (change 'info' to 'debug' for debug logs):
	debug = "prosody.log";
	error = "*console";
	-- Syslog:
	--{ levels = { "error" }; to = "syslog";  };
}


--bosh_ports = {	port = 5280;
--		path = "http-bind";
--	ssl = {
--		key = "/etc/ssl/private/wildcard_memoryoftheworld.org_20130714.key";
--		--certificate = "/etc/prosody/certs/example.com.crt";
--		certificate = "/etc/ssl/certs/wildcard_memoryoftheworld.org_20130714_combined.crt";
--	}
--}
--bosh_ports = {"http-bind"};
http_ports = { 	5280 }
http_paths = { 	bosh = "/http-bind"; 
		files = "/";}
http_interfaces = { "*" }
 
https_ports = { 5281 }
https_interfaces = { "*" }
https_ssl = { 
		certificate = "/etc/prosody/certs/wildcard_memoryoftheworld.org_20130714_combined.crt";
		key = "/etc/prosody/certs/wildcard_memoryoftheworld.org_20130714.key";
		} 
ssl = { 
		certificate = "/etc/prosody/certs/wildcard_memoryoftheworld.org_20130714_combined.crt";
		key = "/etc/prosody/certs/wildcard_memoryoftheworld.org_20130714.key";
		} 

cross_domain_bosh = true;
consider_bosh_secure = true;
----------- Virtual hosts -----------
-- You need to add a VirtualHost entry for each domain you wish Prosody to serve.
-- Settings under each VirtualHost entry apply *only* to that host.
VirtualHost "localhost"


VirtualHost "xmpp.memoryoftheworld.org"
	http_host = "bosh.memoryoftheworld.org";
	--enabled = false -- Remove this line to enable this host
	--authentication = "anonymous";
	--allow_anonymous_s2s = true;
	-- Assign this host a certificate for TLS, otherwise it would use the one
	-- set in the global section (if any).
	-- Note that old-style SSL on port 5223 only supports one certificate, and will always
	-- use the global one.
	ssl = {
		--key = "/etc/prosody/certs/example.com.key";
		key = "/etc/prosody/certs/wildcard_memoryoftheworld.org_20130714.key";
		--certificate = "/etc/prosody/certs/example.com.crt";
		certificate = "/etc/prosody/certs/wildcard_memoryoftheworld.org_20130714_combined.crt";
	}

VirtualHost "anon.memoryoftheworld.org"
	http_host = "bosh.memoryoftheworld.org";
	--enabled = false -- Remove this line to enable this host
	authentication = "anonymous";
	allow_anonymous_s2s = true;
	-- Assign this host a certificate for TLS, otherwise it would use the one
	-- set in the global section (if any).
	-- Note that old-style SSL on port 5223 only supports one certificate, and will always
	-- use the global one.
	ssl = {
		--key = "/etc/prosody/certs/example.com.key";
		key = "/etc/prosody/certs/wildcard_memoryoftheworld.org_20130714.key";
		--certificate = "/etc/prosody/certs/example.com.crt";
		certificate = "/etc/prosody/certs/wildcard_memoryoftheworld.org_20130714_combined.crt";
	}
------ Components ------
-- You can specify components to add hosts that provide special services,
-- like multi-user conferences, and transports.
-- For more information on components, see http://prosody.im/doc/components


---Set up a MUC (multi-user chat) room server on conference.example.com:
Component "conference.memoryoftheworld.org" "muc"
	restrict_room_creation = true
	max_history_messages = 0


-- Set up a SOCKS5 bytestream proxy for server-proxied file transfers:
--Component "proxy.example.com" "proxy65"

---Set up an external component (default component port is 5347)
--
-- External components allow adding various services, such as gateways/
-- transports to other networks like ICQ, MSN and Yahoo. For more info
-- see: http://prosody.im/doc/components#adding_an_external_component
--
--Component "gateway.example.com"
--	component_secret = "password"

------ Additional config files ------
-- For organizational purposes you may prefer to add VirtualHost and
-- Component definitions in their own config files. This line includes
-- all config files in /etc/prosody/conf.d/

Include "conf.d/*.cfg.lua"
