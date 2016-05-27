import BaseHTTPServer
import SocketServer
import smtplib
import time
import threading
from email.mime.text import MIMEText
from secrets import ced_pwd

WANTED_IP = '130.192.147.17'
#WANTED_IP = '127.0.0.1'
LISTEN_PORT = 8000
WANTED_PATH = '/TermostatinoHandler'
FROM = 'ced.control@gmail.com'
TO = 'grassi.e@gmail.com'
HEARTBEAT_TIMEOUT = 2
HEARTBEAT_TIMER = 60

TEMP_ALARM = 32
COUNT_HIGHER_LIMIT = 6

def timer_hb():
	# We expect a heartbeat every 10'' and we send a warning mail
	# if we get less than 6 hb in 1'.
	print "timer"
	print TermostatinoHandler.count_heartbeat
	print TermostatinoHandler.missed_hb
        if TermostatinoHandler.count_heartbeat < HEARTBEAT_TIMEOUT:
		if TermostatinoHandler.missed_hb % 60 == 0:
			TermostatinoHandler.send_mail("Termostatino is not beating!", True)
		TermostatinoHandler.missed_hb += 1
	else:
		TermostatinoHandler.missed_hb = 0
	TermostatinoHandler.lock.acquire()
	TermostatinoHandler.count_heartbeat = 0
	TermostatinoHandler.lock.release()
	threading.Timer(HEARTBEAT_TIMER, timer_hb).start()

class ForkingHTTPServer(SocketServer.ForkingMixIn, BaseHTTPServer.HTTPServer):
    def finish_request(self, request, client_address):
        request.settimeout(30)
        # "super" can not be used because BaseServer is not created from object
        BaseHTTPServer.HTTPServer.finish_request(self, request, client_address)

class TermostatinoHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	count_heartbeat = 0
	count_temp_higher = 0
	missed_hb = 0
	last_seen_temp = None
	last_seen_time = None
	lock = threading.Lock()
	threading.Timer(HEARTBEAT_TIMER, timer_hb).start()
	
	#http://code.activestate.com/recipes/425210-simple-stoppable-server-using-socket-timeout/
	# http://stackoverflow.com/questions/10003866/http-server-hangs-while-accepting-packets
	def server_bind(self):
        	BaseHTTPServer.HTTPServer.server_bind(self)
	        self.socket.settimeout(1)

	def check_request(self):
		""" 
		Checks whether the request comes from our arduino.
		
		Return true if all parameters fit, false otherwise.
		"""
		return True
		#return self.client_address[0] == WANTED_IP and self.path == WANTED_PATH
		# The check on PORT is obviously redundant.

	@staticmethod
	def send_mail(body, error=False):
		if error:
			msg = MIMEText("TermostatinoHandler error: " + str(body))
			msg['Subject'] = 'TermostatinoHandler error'
		else:
			msg = MIMEText("CED temperature beyond the limit " + str(body))
			msg['Subject'] = 'CED temperature alarm'
		msg['From'] = FROM
		msg['To'] = TO
		try:
			s = smtplib.SMTP_SSL('smtp.gmail.com', 465)
			s.login(FROM, ced_pwd)
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
	def manage_temp(self, temp):
		# We will get a ton of mail if temperature continue to switch across the limit.
		# Otherwise a mail every hour after the first one.
		t = float(temp.split("=")[1])
		print t
		TermostatinoHandler.last_seen_temp = t
		TermostatinoHandler.last_seen_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.localtime())
		if t >= TEMP_ALARM:
			if TermostatinoHandler.count_temp_higher >= COUNT_HIGHER_LIMIT or TermostatinoHandler.count_temp_higher == 0:
				if TermostatinoHandler.count_temp_higher % 360 == 0:
					TermostatinoHandler.send_mail(t)
			TermostatinoHandler.count_temp_higher += 1
		else:
			TermostatinoHandler.count_temp_higher = 0

	def do_POST(self):
		#curl -v -d 'temp=45'  localhost:8000/TermostatinoHandler
		if self.check_request():
			length = int(self.headers["Content-Length"])
			entity = self.rfile.read(length)
			self.send_response(200, "Tutto OK!")
			self.end_headers()
			self.manage_temp(entity)
			TermostatinoHandler.lock.acquire()
			TermostatinoHandler.count_heartbeat += 1
			TermostatinoHandler.lock.release()
		else:
			TermostatinoHandler.send_mail("Wrong request POST", True)

	def do_GET(self):
		#curl -v  localhost:8000/TermostatinoQuery
		self.send_response(200, "Tutto OK!")
		print str(TermostatinoHandler.last_seen_temp)
		content = "\n<!DOCTYPE html><html><body><p> Temperature in CED: " + str(TermostatinoHandler.last_seen_temp) + "</p>"
		content += "<p> Got " + str(TermostatinoHandler.last_seen_time) + "</p></body></html>"
		self.send_header("Content-Type:", "text/html")
		self.send_header("Content-Length:", str(len(content)))
		self.end_headers()
		self.wfile.write(content)

server_address = ('', LISTEN_PORT)
#httpd = BaseHTTPServer.HTTPServer(server_address, TermostatinoHandler)
#httpd.serve_forever() 
try:
	print "Server started"
	srvr = ForkingHTTPServer(server_address, TermostatinoHandler)
        srvr.serve_forever()  # serve_forever
except KeyboardInterrupt:
	srvr.socket.close()

