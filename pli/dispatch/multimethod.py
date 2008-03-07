#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20040823032011'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

class AbstractMulimethod(object):
	'''
	'''
	# this is the dict-like to be used as the dispatch table... 
	# NOTE: if this is None self will be used.
	__dispatcher__ = None

	def __call__(self, *pargs, **nargs):
		'''
		'''
		##!!!
		raise NotImplementedError


class ArgumentValueMultimethod(AbstractMulimethod):
	'''
	'''
	def __call__(self, *pargs, **nargs):
		'''
		'''
		if hasatter(self, '__dispatcher__') and self.__dispatcher__ != None:
			dispatcher = self.__dispatcher__
		else:
			dispatcher = self
		##!!!
		dispatcher[nargs != {} and (pargs, nargs) or pargs]


class ArgumentCountMultimethod(ArgumentValueMultimethod):
	'''
	'''
	pass


class ArgumentTypeMultimethod(ArgumentCountMultimethod):
	'''
	'''
	pass


##class Multimethod(ArgumentTypeMultimethod):
##	'''
##	'''
##	pass


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
