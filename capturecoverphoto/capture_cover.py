import SimpleHTTPServer
import BaseHTTPServer
import SocketServer
import os
import shutil
import posixpath
import urllib
import mimetypes
import subprocess
import time

MOCK = True

class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):
    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def trigger_camera(self):
        #if MOCK: return True
        tc = subprocess.Popen(['gphoto2',
                               '--auto-detect',
                               '--capture-image-and-download',
                               '--force-overwrite',
                               '--set-config',
                               'autofocusdrive=0',
                               '--filename',
                               '/tmp/cover.jpg'])
        while tc.poll() is None:
            time.sleep(0.1)
        if tc.returncode == 0:
            return True
        else:
            return False
  
    def capture_photo(self):
        if not self.trigger_camera():
            return False
        
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
        os.chdir("/tmp/")
        if self.path[1:] in "capture":
            self.capture_photo()

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
