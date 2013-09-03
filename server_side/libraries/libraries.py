import subprocess
import os
import cherrypy
import requests

class JSONBooks:
    def __init__(self, domain = "web.dokr"):
        self.domain = domain

    def get_tunnel_ports(self, login="tunnel"):
        uid = subprocess.check_output(["grep", "{0}".format(login), "/etc/passwd"]).split()[0].split(":")[2]
        return subprocess.check_output(["/usr/local/bin/get_tunnel_ports.sh", uid]).split()

    def search(self, search):
        

    def get_metadata(self):
        for port in self.get_tunnel_ports():
            base_url = 'http://{port}.{domain}/'.format(port=port, domain=self.domain)
            search = 'ajax/search?query='



class Root(object):

    @cherrypy.expose
    @cherrypy.tools.json_out()
    @cherrypy.tools.json_in()
    def initpage(self):
        json_books = JSONBooks()
        cl = cherrypy.request.headers['Content-Length']
        body = cherrypy.request.body.read(int(cl))
        #body = simplejson.loads(rawbody)
        # do_something_with(body)
        return json_books.get_metadata()

    @cherrypy.expose
    def index(self):
        return """
<html>
<head><title>Libraries</title>
<script type="text/javascript" src="http://ajax.googleapis.com/ajax/libs/jquery/1.4.2/jquery.min.js"></script>
<script type="text/javascript" src="static/jquery.min.js"></script>
<script type='text/javascript'>
function initpage() {
    $.ajax({
      type: 'POST',
      url: "initpage",
      contentType: "application/json",
      processData: false,
      data: $('#updatebox').val(),
      success: function(data) {
                    $('#content').append('<p>'+ data + '</p>'); 
      },
      dataType: "json"
    });
}

$(document).ready(initpage);

</script>
</title>
<body>
<input type='textbox' id='updatebox' value='{}' size='20' />
<input type='submit' value='Update' onClick='initpage(); return false' />
<div id="content"></div>
</body>
</html>
"""

current_dir = os.path.dirname(os.path.abspath(__file__))
conf = {'/static': {'tools.staticdir.on': True,
                    'tools.staticdir.dir': os.path.join(current_dir, 'static'),
                    'tools.staticdir.content_types': {'javascript': 'application/javascript',
                                                      'css': 'text/css'}}}
cherrypy.server.socket_host = '0.0.0.0'
cherrypy.quickstart(Root(), '/', config=conf)
