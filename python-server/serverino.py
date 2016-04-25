import BaseHTTPServer

#WANTED_IP = '130.192.147.99'
WANTED_IP = '127.0.0.1'
LISTEN_PORT = 8000
WANTED_PATH = '/TermostatinoHandler'

class TermostatinoHandler(BaseHTTPServer.BaseHTTPRequestHandler):

	def check_request(self):
		""" 
		Checks whether the request comes from our arduino.
		
		Return true if all parameters fit, false otherwise.
		"""
		return self.client_address == (WANTED_IP, LISTEN_PORT) and self.path == WANTED_PATH
		# The check on PORT is obviously redundant.

	def send_mail(self, body, error=False):
		if error:
			print "sending an error mail"
		else:
			print "seen temp"
		print str(body)
	
	# log message is called automatically in some cases so right now we do not use this.
	#def log_message(self, format, *args):
	#	print "log message"
	#	self.send_mail(format)

	#def log_error(self, format, *args):
	#	print "log error"
	#	self.send_mail(format, True)

	def do_GET(self):
		self.send_response(200, "Tutto OK!")
		#curl -v localhost:8000/TermostatinoHandler

	def do_POST(self):
		if self.check_request:
			length = int(self.headers["Content-Length"])
			self.send_response(200, "Tutto OK!")
			entity = self.rfile.read(length)
			self.send_mail(entity)
			#curl -v -d 'temp:45'  localhost:8000/TermostatinoHandler
		else:
			self.send_mail("Wrong request", True)

server_address = ('', LISTEN_PORT)
httpd = BaseHTTPServer.HTTPServer(server_address, TermostatinoHandler)
httpd.serve_forever() 

