import BaseHTTPServer
import smtplib
from email.mime.text import MIMEText

#WANTED_IP = '130.192.147.99'
WANTED_IP = '127.0.0.1'
LISTEN_PORT = 8000
WANTED_PATH = '/TermostatinoHandler'
FROM = 'ced.control@gmail.com'
TO = 'grassi.e@gmail.com'

class TermostatinoHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	count_heartbeat = 0
	def check_request(self):
		""" 
		Checks whether the request comes from our arduino.
		
		Return true if all parameters fit, false otherwise.
		"""
		return self.client_address == (WANTED_IP, LISTEN_PORT) and self.path == WANTED_PATH
		# The check on PORT is obviously redundant.

	def send_mail(self, body, error=False):
		if error:
			msg = MIMEText("Wrong request to TermostatinoHandler " + str(body))
			msg['Subject'] = 'TermostatinoHandler error'
		else:
			msg = MIMEText("CED temperature beyond the limit " + str(body))
			msg['Subject'] = 'CED temperature alarm'
		msg['From'] = FROM
		msg['To'] = TO
		try:
			s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			s.login(FROM, 'ufficiotica2?0')
			s.sendmail(FROM, TO, msg.as_string())
			s.quit()
		except smtplib.SMTPConnectError as sce:
			## TODO log error somewhere I will look.
			print sce
		except smtplib.SMTPException as se:
			print se
	
	# log_message is called automatically in some cases so right now we do not use this 
	# but call directly send_mail from the do_*
	#def log_message(self, format, *args):
	#	print "log message"
	#	self.send_mail(format)

	#def log_error(self, format, *args):
	#	print "log error"
	#	self.send_mail(format, True)

	def do_GET(self):
		if self.check_request():
			self.send_response(200, "Tutto OK!")
		else:
			self.send_mail("Wrong request GET", True)
		#curl -v localhost:8000/TermostatinoHandler

	def do_POST(self):
		if self.check_request():
			length = int(self.headers["Content-Length"])
			self.send_response(200, "Tutto OK!")
			entity = self.rfile.read(length)
			self.send_mail(entity)
			#curl -v -d 'temp:45'  localhost:8000/TermostatinoHandler
		else:
			self.send_mail("Wrong request POST", True)

server_address = ('', LISTEN_PORT)
httpd = BaseHTTPServer.HTTPServer(server_address, TermostatinoHandler)
httpd.serve_forever() 

