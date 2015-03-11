import SimpleHTTPServer
import BaseHTTPServer
import SocketServer
import os
import shutil
import posixpath
import urllib
import mimetypes
import piggyphoto as pp


class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):       
    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def live(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.wfile.write("""
        <html>
          <head>
            <title>preview photo capturing</title>
            <script>
        
        var counter = 0; 
        var capture = function () {{
            counter += 1;
            if (counter > 1000) {{
                document.querySelector('body').removeChild(document.querySelector('img'))
                document.querySelector('body').appendChild(document.createElement('img'))
                counter = 0;
                }}
            document.querySelector('img').src = "http://localhost:{}/preview";
            document.querySelector('img').style["transform"] = "scale(-1, -1)";
            }};
        
            </script>
          </head>
          <body onload="window.setInterval(capture, 300)">
            <img/>
          <body>
        </html>
        """.format(SERVER_PORT))
        
    def preview(self):
        preview_path = "{}preview.jpg".format(TEMP_DIR)
        C.capture_preview(preview_path)
        try:
            f = open(preview_path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None

        if not f:
            self.send_error(404, "File not found")
            return None
        
        self.send_response(200)
        self.send_header("Content-type", "image/jpeg")
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Pragma', 'no-cache')
        self.send_header('Expires', '0')
        self.end_headers()
        self.copyfile(f, self.wfile)
        f.close()
        
    def capture_photo(self):
        capture_path = "{}capture.jpg".format(TEMP_DIR)
        C.capture_image(capture_path)
        try:
            f = open(capture_path, 'rb')
        except IOError:
            self.send_error(404, "File not found")
            return None

        if not f:
            self.send_error(404, "File not found")
            return None
        
        self.send_response(200)
        self.send_header("Content-type", "image/jpeg")
        fs = os.fstat(f.fileno())
        self.send_header("Content-Length", str(fs[6]))
        self.send_header("Last-Modified", self.date_time_string(fs.st_mtime))
        self.end_headers()
        self.copyfile(f, self.wfile)
        f.close()
        return
       
    def do_GET(self):
        if self.path[1:] in "capture":
            self.capture_photo()
        elif self.path[1:] in "preview":
            self.preview()
        elif self.path[1:] in "live":
            self.live()

    def translate_path(self, path):
       # abandon query parameters
        path = path.split('?', 1)[0]
        path = path.split('#', 1)[0]
        path = posixpath.normpath(urllib.unquote(path))
        words = path.split('/')
        words = filter(None, words)
        path = os.getcwd()
        for word in words:
            drive, word = os.path.splitdrive(word)
            head, word = os.path.split(word)
            if word in (os.curdir, os.pardir):
                continue
            path = os.path.join(path, word)
        return path
   
    def guess_type(self, path):
        base, ext = posixpath.splitext(path)
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        ext = ext.lower()
        if ext in self.extensions_map:
            return self.extensions_map[ext]
        else:
            return self.extensions_map['']

    if not mimetypes.inited:
        mimetypes.init()

    extensions_map = mimetypes.types_map.copy()
    extensions_map.update({
        '': 'application/octet-stream',
        })

C = pp.camera()
C.leave_locked()
    
SERVER_PORT = 9980

## before starting this script on linux
## one should use mkram from ../utils/
## and make RAM filesystem at /tmp/RAM

TEMP_DIR = "/tmp/RAM/"
if not os.path.isdir(TEMP_DIR):
    try:
        os.mkdir("/tmp/RAM")
    except Exception as e:
        TEMP_DIR = "/tmp/"
        print("Error making /tmp/RAM directory: {}".format(e))
        
SocketServer.TCPServer.allow_reuse_address = True
httpd = BaseHTTPServer.HTTPServer(("", SERVER_PORT), HTTPHandler)
httpd.serve_forever()
