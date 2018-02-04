#!/usr/bin/env python
"""
server that response with ip host number for serial number
"""
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import csv

snip = {}

class S(BaseHTTPRequestHandler):

    def _set_headers(self, code=200):
        self.send_response(code)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        self._set_headers()
        print self.path
        param = self.path.split('/')
        if len(param) == 2 and param[1] in snip:
            host = snip[param[1]]
            self.wfile.write(host)
        else:
            self.wfile.write(0)

    def do_POST(self):
        # Doesn't do anything with posted data
        content_length = int(self.headers['Content-Length']) # <--- Gets the size of data
        post_data = self.rfile.read(content_length) # <--- Gets the data itself
        print post_data # <-- Print post data
        self._set_headers()

def run(server_class=HTTPServer, handler_class=S, port=8000):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print 'Starting httpd... on port %d' % port
    httpd.serve_forever()

if __name__ == "__main__":
    with open('sn2ip.csv', 'rb') as csvfile:
        for row in csv.reader(csvfile):
            if len(row) == 2:
                snip[row[1]] = row[0]
            
    run()
