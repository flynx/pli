#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20090827170844'''
__copyright__ = '''(c) Alex A. Naanou 2007'''


#-----------------------------------------------------------------------

import ZODB
import persistent

import zodbutils

import pli.pattern.proxy.utils as putil


#-----------------------------------------------------------------------
#
# NOTE: the current version of zc.set (Zope) was used as a reference 
#       point for this module...
#       motivation for this was to a) I could not find a stable version
#       of the above module (backporting is more expensive than
#       maintaining) and b) it was fun using the pli infrastructure.
# TODO as soon as set becomes part of ZODB, use that...
#
#
#-----------------------------------------------------------------------
#-----------------------------------------------------------stripdata---
# XXX is this efficient??
def stripdata(meth):
	'''
	'''
	def _stripdata(self, other):
		'''
		'''
		if isinstance(other, self.__class__):
			other = other._data
		return meth(self, other)
	return _stripdata


#----------------------------------------------------------wrapresult---
# XXX might be good to move this to pli...
def wrapresult(meth):
	'''
	'''
	def _wrapresult(self, *p, **n):
		'''
		'''
		res = meth(self, *p, **n)
		o = self.__class__()
		o._data = res
		return o
	return _wrapresult


#-----------------------------------------------------------------------
#----------------------------------------------------------------zset---
class zset(persistent.Persistent):
	'''
	'''
	def __init__(self, data=()):
		'''
		'''
		self._data = set(data)
	
	# basic non-mutating methods...
	putil.proxymethods((
			'__cmp__',
			'__contains__',
			'__hash__',
			'__iter__',
			'__len__',
		), '_data')
	
	# basic mutating methods (transactional)...
	putil.proxymethods((
			'add',
			'clear',
			'difference_update',
			'discard',
			'intersection_update',
			'pop',
			'remove',
			'symmetric_difference_update',
			'update',
		), '_data',
		decorators=(zodbutils.mutating,))

	# mutating methods that take sets (self._data needs to be passed
	# in, instead of self)...
	putil.proxymethods((
			'__iand__',
			'__ior__',
			'__isub__',
			'__ixor__'
		), '_data',
		decorators=(
			zodbutils.mutating,
			stripdata,
		))
	
	# non-mutating methods that take sets (self._data needs to be passed
	# in, instead of self)...
	putil.proxymethods((
			'__eq__',
			'__ge__',
			'__gt__',
			'__le__',
			'__lt__',
			'__ne__',
			'issubset',
			'issuperset',
		), '_data',
		decorators=(stripdata,))

	# methods returning sets that need to be wrapped in zset...
	putil.proxymethods((
			'difference',
			'intersection',
			'symmetric_difference',
			'union',
		), '_data',
		decorators=(wrapresult,))

	# methods returning sets that need to be wrapped in zset, and need
	# self._data stripped out...
	putil.proxymethods((
			'__and__',
			'__or__',
			'__rand__',
			'__ror__',
			'__rsub__',
			'__rxor__',
			'__sub__',
			'__xor__',
		), '_data',
		decorators=(
			stripdata,
			wrapresult,
		))

	# custom methods...
	def __repr__(self):
		'''
		'''
		return '%s.%s(%s)' % (
			self.__class__.__module__,
			self.__class__.__name__,
			repr(list(self._data)))
	def copy(self):
		'''
		'''
		return self.__class__(self._data)


#-----------------------------------------------------------------------
if __name__ == '__main__':

	s = zset(xrange(20))

	print s

	# zodbutils.mutating...
	s.update(xrange(10, 30))

	print len(s)

	print 2 in s

	# stripdata...
	print zset(xrange(5, 15)).issubset(s)
	print s.issuperset(set(xrange(5, 15)))

	# wrapresult...
	print s.difference(set(xrange(5, 25)))
	print s.difference(zset(xrange(5, 25)))

	# XXX check combinations...



#=======================================================================
#											 vim:set ts=4 sw=4 nowrap :
