-- this config file is prepared for prosody 0.9+

admins = {"marcell@chat.memoryoftheworld.org" }

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

daemonize = false;

pidfile = "prosody.pid";

-- These are the SSL/TLS-related settings. If you don't want
-- to use SSL/TLS, you may comment or remove this

ssl = {
		key = "/etc/ssl/private/wildcard_memoryoftheworld.org_20130714.key";
		--certificate = "/etc/prosody/certs/example.com.crt";
		certificate = "/etc/ssl/certs/wildcard_memoryoftheworld.org_20130714_combined.crt";
}

c2s_require_encryption = true;
s2s_require_encryption = true;


authentication = "internal_hashed"

log = {
	debug = "prosody.log";
	error = "prosody.err";
	"*console";
}

http_ports = { 	5280 }
http_paths = { 	bosh = "/http-bind"; 
		files = "/";}
http_interfaces = { "*" }
 
https_ports = { 5281 }
https_interfaces = { "*" }
https_ssl = { 
		certificate = "/etc/ssl/certs/wildcard_memoryoftheworld.org_20130714_combined.crt";
		key = "/etc/ssl/private/wildcard_memoryoftheworld.org_20130714.key";
		} 
ssl = { 
		certificate = "/etc/ssl/certs/wildcard_memoryoftheworld.org_20130714_combined.crt";
		key = "/etc/ssl/private/wildcard_memoryoftheworld.org_20130714.key";
		} 

cross_domain_bosh = true;
consider_bosh_secure = true;

----------- Virtual hosts -----------
-- You need to add a VirtualHost entry for each domain you wish Prosody to serve.
-- Settings under each VirtualHost entry apply *only* to that host.
VirtualHost "localhost"


VirtualHost "chat.memoryoftheworld.org"
	http_host = "bosh.memoryoftheworld.org";
	ssl = {
		--key = "/etc/prosody/certs/example.com.key";
		key = "/etc/ssl/private/wildcard_memoryoftheworld.org_20130714.key";
		--certificate = "/etc/prosody/certs/example.com.crt";
		certificate = "/etc/ssl/certs/wildcard_memoryoftheworld.org_20130714_combined.crt";
	}

VirtualHost "anon.memoryoftheworld.org"
	http_host = "bosh.memoryoftheworld.org";
	authentication = "anonymous";
	allow_anonymous_s2s = true;
	ssl = {
		--key = "/etc/prosody/certs/example.com.key";
		key = "/etc/ssl/private/wildcard_memoryoftheworld.org_20130714.key";
		--certificate = "/etc/prosody/certs/example.com.crt";
		certificate = "/etc/ssl/certs/wildcard_memoryoftheworld.org_20130714_combined.crt";
	}
------ Components ------
-- You can specify components to add hosts that provide special services,
-- like multi-user conferences, and transports.
-- For more information on components, see http://prosody.im/doc/components


---Set up a MUC (multi-user chat) room server on conference.example.com:
Component "conference.memoryoftheworld.org" "muc"
	restrict_room_creation = true
	max_history_messages = 0

Include "conf.d/*.cfg.lua"
