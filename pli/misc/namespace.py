#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20040527144611'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import sys

import pli.logictypes as logictypes


#-----------------------------------------------------------------------
#-----------------------------------------------------------NameSpace---
class NameSpace(logictypes.DictUnion):
	'''
	'''
	def __getitem__(self, name):
		'''
		'''
		if type(name) is int:
			# return the scope...
			return self._members[name]
		return super(NameSpace, self).__getitem__(name)
	def __setitem__(self, name, value):
		'''
		this will set a variable to the topmost scope.
		'''
		if type(name) not in (str, unicode):
			raise TypeError, 'a name must be of either str or unicode type (got %s).' % type(name)
		self._members[0][name] = value



#-----------------------------------------------------------------------
#-----------------------------------------------------------namespace---
def namespace():
	'''
	this will return a dict union object that represents the current naespace stack.
	'''
	getframe = sys._getframe
	res = NameSpace()
	i = 1
	try:
		while True:
			res.tailunite(getframe(i).f_locals)
			i += 1
	except ValueError:
		pass
	return res



#=======================================================================
#											 vim:set ts=4 sw=4 nowrap :
