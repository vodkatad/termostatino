import BaseHTTPServer
import SocketServer
import cgi


class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
    def do_POST(self):
        ctype, pdict = cgi.parse_header(self.headers.getheader('content-type'))
        postvars = {}
        try:
            if ctype == 'application/x-www-form-urlencoded':
                length = int(self.headers.getheader('content-length'))
                postvars = cgi.parse_qs(self.rfile.read(length),
                        keep_blank_values=1)
                assert postvars.get('foo', '') != ['simulate error']
            body = 'Something'
            self.send_response(200)
            self.send_header("Content-type", "text")
            self.send_header("Content-length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except:
            self.send_error(500)
            raise

    def do_GET(self):
        # demo for testing POST by web browser - without valid html
        body = 'Something\n<form method="post" action="http://%s:%d/">\n' \
                '<input name="foo" type="text"><input type="submit"></form>\n'\
                % self.server.server_address
        self.send_response(200)
        self.send_header("Content-type", "text/html")
        self.send_header("Content-length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


class ForkingHTTPServer(SocketServer.ForkingMixIn, BaseHTTPServer.HTTPServer):
    def finish_request(self, request, client_address):
        request.settimeout(30q)
        # "super" can not be used because BaseServer is not created from object
        BaseHTTPServer.HTTPServer.finish_request(self, request, client_address)


def httpd(handler_class=MyHandler, server_address=('localhost', 8000)):
    try:
        print "Server started"
        srvr = ForkingHTTPServer(server_address, handler_class)
        srvr.serve_forever()  # serve_forever
    except KeyboardInterrupt:
        srvr.socket.close()

if __name__ == "__main__":
    httpd()
