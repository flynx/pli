#=======================================================================
'''
this module defines the logger aspects.
'''

#-----------------------------------------------------------------------

__version__ = '''0.1.03'''
__sub_version__ = '''20040212153738'''
__copyright__ = '''(c) Alex A. Naanou 2003'''



#-----------------------------------------------------------------------

import sys
import time
import aspect 



#-----------------------------------------------------------------------
# LoggerAspect flags:
# make the aspect pre-condirioned
LOG_PRE = 1
# make the aspect post-conditioned.
LOG_POST = 2


#--------------------------------------------------------LoggerAspect---
# TODO make this thread-safe...
#
class LoggerAspect(aspect.Aspect):
	'''
	'''
	def __init__(self, file=None, mode=LOG_POST, format=None, verbosity=1):
		'''
		'''
		self.file = file
		self.mode = mode
		self.verbosity = verbosity
		if format == None:
			self.format = '[%(time)s] [%(mode)s] --'
		else:
			self.format = format
	# this is the part that is not thread safe...
	def out(self, *pargs, **nargs):
		'''
		this is the output method...
		'''
		# do dynamic output file linking...
		if self.file == None:
			output = sys.stderr
		else:
			output = self.file
		for i in pargs:
			print >> output, i,
		print >> output
	def pre(self, obj, meth, *pargs, **nargs):
		'''
		'''
		if self.mode&LOG_PRE:
			v = self.verbosity
			if v < 1:
				pass
			elif v == 1:
				self.out(self.format % {'time':time.strftime('%Y%m%d%H%M%S'), 'mode': 'pre'},\
							meth.__name__)
			elif v > 1:
				self.out(self.format % {'time':time.strftime('%Y%m%d%H%M%S'), 'mode': 'pre'},\
							meth.__name__, *pargs, **nargs)
	def post(self, obj, meth, ret, rexcept, *pargs, **nargs):
		'''
		'''
		if self.mode&LOG_POST:
			v = self.verbosity
			if v < 1:
				pass
			elif v == 1:
				self.out(self.format % {'time':time.strftime('%Y%m%d%H%M%S'), 'mode': 'post'},\
							meth.__name__, ret, rexcept)
			elif v > 1:
				self.out(self.format % {'time':time.strftime('%Y%m%d%H%M%S'), 'mode': 'post'},\
							meth.__name__, ret, rexcept, *pargs, **nargs)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
