import BaseHTTPServer

class TermostatinoHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_GET(self):
		self.send_response(200, "Tutto OK!")

	def do_POST(self):
		length = int(self.headers["Content-Length"])
		entity = self.rfile.read(length)
		print entity
		self.send_response(200, "Tutto OK!")

server_address = ('', 8000)
httpd = BaseHTTPServer.HTTPServer(server_address, TermostatinoHandler)
httpd.serve_forever() 

