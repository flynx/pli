#=======================================================================
#=======================================================================

__version__ = '''0.1.00'''
__sub_version__ = '''20040223152229'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

##import sys
##import new
##import types
##import weakref
import operator
from pli.functional import *



#-----------------------------------------------------------------------
#
# WARNING: this is not yet complete!!!
#
# NOTE: this works about twice faster than the *clever* version.
##!! BUG: this apears not to work with the % operator (e.g. '%d' % pobj)
class callproxy(object):
	'''
	this is a dumb callproxy.
	'''
	__slots__ = ['p_obj', 'p_queue', 'p_cache', 'p_drop_refs', 'p_callback', 'p_safe', '__weakref__']
	def __init__(self, obj, queue=None, cache=None, drop_refs=0, callback=None, safe=1):
		# do some correctness checks
		if safe:
			# callback test
			if callback != None:
				if not callable(callback):
					raise TypeError, 'callback object must be callable.'
			elif queue == None:
				raise TypeError, 'one of either callback or queue objects must be specified.'
			# test if queue supports append
			elif not hasattr(queue, 'append'):
				raise TypeError, 'queue object must have an "append" method.'
			# test if this supports dict interface
			if cache != None and (not hasattr(cache, '__setitem__') or not hasattr(cache, '__getitem__') or not hasattr(cache, 'keys')):
				raise TypeError, 'cache object must support "__setitem__", "__getitem__" and "keys" methods'
##			# if this is true there is no point in this in the first place!
##			elif callback == None and queue == None:
##					raise TypeError, 'one of either callback or queue objects must be specified.'
		osetattr = object.__setattr__
		osetattr(self, 'p_obj', obj)
		osetattr(self, 'p_queue', queue)
		osetattr(self, 'p_cache', cache)
		osetattr(self, 'p_drop_refs', drop_refs)
		osetattr(self, 'p_callback', callback)
		osetattr(self, 'p_safe', safe)
	def __getattr__(self, name):
		target = getattr(self.p_obj, name)
		if self.p_cache != None and hasattr(self.p_cache, 'update'):
			if target in self.p_cache.keys():
				return self.p_cache[target]
			else:
				pobj = callproxy(target, self.p_queue, self.p_cache, self.p_drop_refs, self.p_callback, self.p_safe)
				self.p_cache.update({target: pobj})
				return pobj
		return self.__class__(target, self.p_queue, self.p_cache, self.p_drop_refs, self.p_callback, self.p_safe)
	def __call__(self, *p, **n):
		# check if callable...
		if not callable(self.p_obj):
			self.p_obj(*p, **n)
		if self.p_queue != None:
			# queue the call
			self.p_queue.append(curry(self.p_obj, *p, **n))
			# do the callback.
			if self.p_callback != None:
				return self.p_callback(*(self.p_obj,) + p, **n)
			return None
		elif self.p_callback != None:
				return self.p_callback(*(self.p_obj,) + p, **n)
		# we get here if safe is False...
		# WARNING: this is currently incompatible with the python version!
		return self.p_obj(*p, **n)
	def __setattr__(self, name, val):
		setattr(self.p_obj, name, val)
	def __delattr__(self, name):
		delattr(self.p_obj, name)
	def __repr__(self):
		return '<callproxy at %s to %.100s at %s>' % (hex(id(self)), self.p_obj.__class__.__name__, hex(id(self.p_obj)))
	def __str__(self):
		return str(self.p_obj)
	def __iter__(self):
		return self.p_obj.__iter__()
	def __hash__(self):
		return hash(self.p_obj)
	def __nonzero__(self):
		if hasattr(self.p_obj, '__nonzero__'):
			return self.p_obj.__nonzero__()
		elif hasattr(self.p_obj, '__len__'):
			return len(self.p_obj)
		else:
			return 1
	def __len__(self):
		return len(self.p_obj)
	def __unicode__(self):
		return self.p_obj.__unicode__()
	def __cmp__(self, other):
		# get the original type if the other side is callproxy
		if isinstance(other, callproxy):
			other = other.p_obj
		return cmp(self.p_obj, other)
##	def __lt__(self, other):
##		return self.p_obj.__lt__(other)
##	def __le__(self, other):
##		return self.p_obj.__le__(other)
##	def __eq__(self, other):
##		return self.p_obj.__eq__(other)
##	def __ne__(self, other):
##		return self.p_obj.__ne__(other)
##	def __gt__(self, other):
##		return self.p_obj.__gt__(other)
##	def __ge__(self, other):
##		return self.p_obj.__ge__(other)

	# number interface...
	# NOTE: if you have the strength to read this section, be my guest! 
	#             (I did not even have the strength to write it.. :) )
	def __add__(x, y):
		if isinstance(x, callproxy):
			x = (x).p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return operator.__add__(x, y)
	def __sub__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return operator.__sub__(x, y)
	def __mul__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return operator.__mul__(x, y)
	def __floordiv__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return operator.__floordiv__(x, y)
	def __truediv__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return operator.__truediv__(x, y)
	def __div__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return operator.__div__(x, y)
	def __mod__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return operator.__mod__(x, y)
	def __divmod__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return x.__divmod__(y)
	def __pow__(x, y, z):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		if isinstance(z, callproxy):
			z = z.p_obj
		return x.__pow__(y, z)
	def __neg__(self):
		return operator.__neg__(self.p_obj)
	def __pos__(self):
		return operator.__pos__(self.p_obj)
	def __abs__(self):
		return operator.__abs__(self.p_obj)
	def __invert__(self):
		return operator.__invert__(self.p_obj)
	def __lshift__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return operator.__lshift__(x, y)
	def __rshift__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return operator.__rshift__(x, y)
	def __and__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return operator.__and__(x, y)
	def __xor__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return operator.__xor__(x, y)
	def __or__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return operator.__or__(x, y)
	def __int__(self):
		return int(self.p_obj)
	def __long__(self):
		return long(self.p_obj)
	def __float__(self):
		return float(self.p_obj)
	def __oct__(self):
		return oct(self.p_obj)
	def __hex__(self):
		return hex(self.p_obj)
	def __iadd__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return x.__iadd__(y)
	def __isub__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return x.__isub__(y)
	def __imul__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return x.__imul__(y)
	def __ifloordiv__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return x.__ifloordiv__(y)
	def __itruediv__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return x.__itruediv__(y)
	def __idiv__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return x.__idiv__(y)
	def __imod__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return x.__imod__(y)
	def __ipow__(x, y, z):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		if isinstance(z, callproxy):
			z = z.p_obj
		return x.__ipow__(y, z)
	def __ilshift__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return x.__ilshift__(y)
	def __irshift__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return x.__irshift__(y)
	def __iand__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return x.__iand__(y)
	def __ixor__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return x.__ixor__(y)
	def __ior__(x, y):
		if isinstance(x, callproxy):
			x = x.p_obj
		if isinstance(y, callproxy):
			y = y.p_obj
		return x.__ior__(y)

	##!!!




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
