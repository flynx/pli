#=======================================================================

__version__ = '''0.0.03'''
__sub_version__ = '''20040730003844'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import sys


#-----------------------------------------------------------------------

class Trace(object):
	'''
	'''
	def __init__(self, name, print_code=False, print_locals=False, print_globals=False, print_dividers=True, callback=None):
		'''
		'''
		self.__name__ = name
		self.print_code = print_code
		self.print_locals = print_locals
		self.print_globals = print_globals
		self.print_dividers = print_dividers
	def _traceinfo(self, frame, event, arg, level=0):
		'''
		'''
		print '%s --> %s: %s (%s)' % (self.__name__, frame.f_code.co_filename, frame.f_lineno, event)
		# code...
		if self.print_code:
			print '   | '
			# XXX remove the \n if present....
			print '   | ', open(frame.f_code.co_filename).readlines()[frame.f_lineno-1][:-1]
		# locals...
		if self.print_locals: 
			print '   | '
			print '   | locals:', frame.f_locals
		# globals....
		if self.print_globals: 
			print '   | '
			print '   | globals:', frame.f_globals
		print '   | '
	def start(self):
		'''
		'''
		if self.print_dividers: 
			print '-' * 72
		sys.settrace(self._traceinfo)
	def stop(self):
		'''
		'''
		sys.settrace(None)
		if self.print_dividers: 
			print '-' * 72


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
