import SimpleHTTPServer
import BaseHTTPServer
import SocketServer
import os
import shutil
import posixpath
import urllib
import mimetypes
import piggyphoto as pp

C = pp.camera()
C.leave_locked()


class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):       
    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)
        
    def preview(self):
        C.capture_preview("/tmp/preview.jpg")
        try:
            f = open("/tmp/preview.jpg", 'rb')
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
        C.capture_image("/tmp/cover.jpg")
        try:
            f = open("/tmp/cover.jpg", 'rb')
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


SocketServer.TCPServer.allow_reuse_address = True
httpd = BaseHTTPServer.HTTPServer(("", 7711), HTTPHandler)
httpd.serve_forever()
