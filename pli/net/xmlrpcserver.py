#=======================================================================

__version__ = '''0.0.07'''
__sub_version__ = '''20040430192015'''
__copyright__ = '''(c) Alex A. Naanou 2003-2004'''


#=======================================================================

import SocketServer, BaseHTTPServer
import xmlrpclib
import sys
import traceback



#-----------------------------------------------------------------------
#------------------------------------------------------RequestHandler---
# this is based on the xmlrpc server included in xmlrpc lib
# (xmlrpcserver.py) written by Fredrik Lundh, January 1999
# and coprighted:
#    Copyright (c) 1999 by Secret Labs AB.
#    Copyright (c) 1999 by Fredrik Lundh.
#    fredrik@pythonware.com
#    http://www.pythonware.com
#
# this code is modified by Alex A. Naanou <alex_nanou@yahoo.com>
#
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# TODO do a more thorough security check + test...
# TODO do a proper GET handler...
# TODO do a https server...
#
class RequestHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	'''
	this is the basic xmlrpc request handler. 
	'''
	# debug mode...
	__server_debug__ = False
	__verbosity__ = 0
	# this enables/disables basic security
	_sec_enabled = False
	# this defines the iterable containing the allowed client addresses
##	_sec_allowed_client_addr = ['127.0.0.1']

	def do_POST(self):
		'''
		the POST http command handler.
		'''
		# do security check...
		##!!!
		if self._sec_enabled and hasattr(self, '_sec_allowed_client_addr'):
			if self.client_address[0] not in self._sec_allowed_client_addr:
				# return err response...
				self.send_response(403)
				self.end_headers()
				self.wfile.write(response)
				# shut down the connection
				self.wfile.flush()
				self.connection.shutdown(1)
				return
		# handle the actual request...
		try:
			# get arguments
			data = self.rfile.read(int(self.headers["content-length"]))
			if self.__server_debug__ and self.__verbosity__ > 2:
				print '=' * 72
				print 'Request:'
				print '-' * 72
				print data
				print '=' * 72
			try:
				# parse the request...
				params, method = xmlrpclib.loads(data)
				# generate response
				response = self.call(method, params)
				if type(response) != type(()):
					response = (response,)
			except:
				# report exception back to server
				exc_type, exc_value, exc_trackback = sys.exc_info()
				if self.__server_debug__:
					# TODO verbosity level...
					print '=' * 72
					print 'ERR:', "%s:%s" % (exc_type, exc_value)
					if self.__verbosity__ > 1:
						print '-' * 72
						traceback.print_tb(exc_trackback)
					print '=' * 72
				response = xmlrpclib.dumps(xmlrpclib.Fault(1, "%s:%s" % (exc_type, exc_value)))
			else:
				##!!! use an encoding....
##				response = xmlrpclib.dumps(response, methodresponse=1, encoding='cp1251')
				response = xmlrpclib.dumps(response, methodresponse=1)
				if self.__server_debug__ and self.__verbosity__ > 2:
					print '=' * 72
					print 'Response:'
					print '-' * 72
					print response
					print '=' * 72
		except:
			# internal error, report as HTTP server error
			self.send_response(500)
			self.end_headers()
		else:
			# got a valid XML RPC response
			self.send_response(200)
			self.send_header("Content-type", "text/xml")
			self.send_header("Content-length", str(len(response)))
			self.end_headers()
			self.wfile.write(response)
			# shut down the connection (from Skip Montanaro)
			self.wfile.flush()
			self.connection.shutdown(1)
	# the GET handler
##	do_GET = do_POST
	def do_GET(self):
		'''
		the GET http command handler.
		'''
		# this currently does not differ from post...
		return self.do_POST()
	# override this method to implement RPC methods
	def call(self, method, params):
		'''
		base rpc call dispatch method (not for direct use).
		'''
		raise NotImplementedError, 'this method is not for direct use. (Call: %s(%s))' % (method, params)
	# utill methods...
##	def Error(self, faultCode=1, faultString='', **extra):
##		'''
##		'''
##		pass



#=======================================================================
if __name__ == '__main__':
	server = SocketServer.TCPServer(('', 8000), RequestHandler)
	server.serve_forever()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
