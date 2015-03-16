#!/usr/bin/env python

import SimpleHTTPServer
import BaseHTTPServer
import SocketServer
import os
import random
import shutil
import datetime
import posixpath
import urllib
import mimetypes

try:
    from piggyphoto import Camera as camera
except:
    from piggyphoto import camera
try:
    from piggyphoto import CameraList as cameraList
except:
    from piggyphoto import cameraList

class HTTPHandler(SimpleHTTPServer.SimpleHTTPRequestHandler):       
    def copyfile(self, source, outputfile):
        shutil.copyfileobj(source, outputfile)

    def connect(self):
        connect_camera()
        
    def status(self):
        s = connect_camera()
        connected = "false"
        if s:
            connected = "true"
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.wfile.write("""
        <html>
          <head>
            <title>photo capturing server status</title>
            <meta http-equiv="refresh" content="2"/>
            <script>
        var connected = {0};
        var connect = function() {{
           document.querySelector('iframe').src = "http://localhost:7711/connect";
           document.querySelector('button').style["display"] = "none";
        }}
        var sts = function() {{
          if (connected == false){{
            document.querySelector('button').style["display"] = "block";
            document.querySelector('div').style["display"] = "none";
          }}
        }}
            </script>
          </head>
          <body onload="sts()">
            <button style='width: 100%;font-weight: bold;background: red; color: white; display: none;' onClick='connect();'>CONNECT CAMERA</button></br>
            <center>
              <div style='width: 100%; height: 100%; background: green; color: white; font-weight: bold;'>{1} UP&RUNNING</div>
            </center>
            <iframe id='dummy' src='about:blank' style='display: none;'><iframe>
          <body>
        </html>
        """.format(connected, get_ts()))
       
    def live(self):
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.wfile.write("""
        <html>
          <head>
            <title>preview photo capturing</title>
            <script>
        var preview = true;
        var button = function() {{
        if (document.querySelector('button').textContent == "START PREVIEW") {{
          document.querySelector('button').textContent = "STOP PREVIEW";
          document.querySelector('button').style["background"] = "rgba(255,0,0,0.2)";
          preview = true;
          }} else {{
          document.querySelector('button').textContent = "START PREVIEW";
          document.querySelector('button').style["background"] = "rgba(0,255,0,0.2)";
          preview = false;
          }}
        }}

        var counter = 0; 
        var capture = function () {{
            if (preview == false) {{
               return
            }}
            counter += 1;
            if (counter > 1000) {{
                document.querySelector('body').removeChild(document.querySelector('img'))
                document.querySelector('body').appendChild(document.createElement('img'))
                counter = 0;
                }}
            document.querySelector('img').src = "http://localhost:{0}/preview";
            document.querySelector('img').style["transform"] = "scale(-1, -1)";
            }};
        
            </script>
          </head>
          <body onload="window.setInterval(capture, 300)">
            <button style='width: 100%;font-weight: bold;background: rgba(255,0,0,0.2)' onClick='button();'>STOP PREVIEW</button></br>
            <img/>
          <body>
        </html>
        """.format(SERVER_PORT))
        
    def preview(self):
        preview_path = "{0}preview.jpg".format(TEMP_DIR)
        if C:
            C.capture_preview(preview_path)
        else:
            return
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
        capture_path = "{0}capture.jpg".format(TEMP_DIR)
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
        elif self.path[1:] in "status":
            self.status()
        elif self.path[1:] in "connect":
            self.connect()

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

    def log_message(self, format, *args):
        ## this will shush the default logger
        pass

def get_ts():
    return datetime.datetime.now().isoformat().split("T")[1].split(".")[0] 
    

C = False
def connect_camera():
    global C
    if not C:
        try:
            C = camera()
            C.leave_locked()
            return True
        except:
            C = False
            return False
    else:
        clist = cameraList(autodetect=True)
        if str(clist).startswith("cameraList object with 0 elements"):
            C = False
            return False
        elif C.initialized:
            return True

              
SERVER_PORT = 7711

## before starting this script on linux
## one should use mkram from ../utils/
## and make RAM filesystem at /tmp/RAM

TEMP_DIR = "/tmp/RAM/"
if not os.path.isdir(TEMP_DIR):
    try:
        os.mkdir("/tmp/RAM")
    except Exception as e:
        TEMP_DIR = "/tmp/"
        print("Error making /tmp/RAM directory: {0}".format(e))

print("Location:http://localhost:7711/status")
SocketServer.TCPServer.allow_reuse_address = True
httpd = BaseHTTPServer.HTTPServer(("", SERVER_PORT), HTTPHandler)
httpd.serve_forever()
