#=======================================================================

__version__ = '''0.0.02'''
__sub_version__ = '''20050824031152'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------



#------------------------------------------------------------Dispatch---
# NOTE: might be good to split this into several classes (interigator
#       and dispatch)
# TODO write docs...
# TODO write the following extencions:
# 		- two way dispatch...
# 		  the rules will be something like:
# 		  	<in> <action> <out>
# 		  	or
# 		  	<in> <in_action> <out> <out_action>
# 		- dedicated interigator (with more control over the order and
# 		  behavior)...
class Dispatch(object):
	'''
	'''
	def __init__(self, interigators=None):
		'''
		'''
		if interigators == None:
			interigators = []
		self._interigators = interigators
		self._dispatchtable = {}
		self._defailthandler = None
	# interface methods:
	def addhandler(self, key, handler, force=False):
		'''
		'''
		if key is None:
			raise TypeError, 'key can\'t be None.'
		if not force and not callable(handler):
			raise TypeError, 'handler must be callable.'
		self._dispatchtable[key] = handler
	def setdefaulthandler(self, handler):
		'''
		'''
		self._defailthandler = handler
	# the interigator takes the object as argument and returns a key or
	# None.
	##!!! make the priority work...
	##!!! add default interigator... (???)
	def addinterigator(self, interigator, prio=None):
		'''
		'''
		self._interigators.insert(0, interigator)
##	def getinterigationdoc(self):
##		'''
##		'''
##		pass
	def handle(self, obj):
		'''
		'''
		# get the handler...
		handler = self.gethandler(self.getkeys(obj))
		if handler != None:
			return handler(obj)
		raise TypeError, 'can\'t handle %s, no compatible handler defined.'
	def getkeys(self, obj):
		'''
		get all possible non-None keys for the input.

		the list of keys is formed using the registered interigators 
		and the last key is always the original object.
		'''
		return [ r for r in [ i(obj) for i in self._interigators ] if r != None ] + [obj]
	##!! REVISE !!##
	def gethandler(self, keys):
		'''

		NOTE: keys must be iterable.
		'''
		dt = self._dispatchtable
		for k in keys:
			if k in dt:
				return dt[k]
		##!! raise an error??
		return self._defailthandler



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
