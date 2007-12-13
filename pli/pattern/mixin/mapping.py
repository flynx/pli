#=======================================================================

__version__ = '''0.1.03'''
__sub_version__ = '''20071206152113'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

_marker = 'This is a marker string... (WARNING: do not use this in any way!)'

# NOTE: none of the defined here classes will contaminate the namespace
#       of the object that derrives from any one or combination of
#       them.

#-----------------------------------------------------------------------
#-----------------------------------------------------------ismapping---
def ismapping(obj):
	'''
	'''
	return isinstance(obj, (AbstractMapping, dict))


#-----------------------------------------------------------------------
#-----------------------------------------------------AbstractMapping---
class AbstractMapping(object):
	'''
	'''
	pass


#-----------------------------------------------------------------------
#--------------------------------------------------------BasicMapping---
class BasicMapping(AbstractMapping):
	'''
	this defines the basic mapping interface.
	'''
	# root methods:
	def __getitem__(self, key):
		'''
		'''
		#raise NotImplementedError, 'root method __getitem__ not implemented.'
		return super(BasicMapping, self).__getitem__(key)
	def __setitem__(self, key, value):
		'''
		'''
		#raise NotImplementedError, 'root method __setitem__ not implemented.'
		return super(BasicMapping, self).__setitem__(key, value)
	def __delitem__(self, key):
		'''
		'''
		#raise NotImplementedError, 'root method __delitem__ not implemented.'
		return super(BasicMapping, self).__delitem__(key)
	def __iter__(self):
		'''
		'''
		#raise NotImplementedError, 'root method __iter__ not implemented.'
		return super(BasicMapping, self).__iter__()
	
	# 2nd generation methods:
	def __contains__(self, key):
		'''
		'''
		try:
			self[key]
			return True
		except KeyError:
			return False

	def __len__(self):
		'''
		'''
		return len([k for k in self])
	
##	# do we need these here???
##	def __reduce__(self):
##		'''
##		'''
##		pass
##	def __reduce_ex__(self):
##		'''
##		'''
##		pass
##
##	def __repr__(self):
##		'''
##		'''
##		pass
##	def __str__(self):
##		'''
##		'''
##		pass
##
##	def __hash__(self):
##		'''
##		'''
##		pass


#---------------------------------------------------BasicMappingProxy---
# NOTE: this is slower than a direct proxy...
class BasicMappingProxy(AbstractMapping):
	'''
	'''
	__source_attr__ = '__source__'

	#__source__ = {}

	# root methods:
	def __getitem__(self, key):
		'''
		'''
		return getattr(self, self.__source_attr__)[key]
	def __setitem__(self, key, value):
		'''
		'''
		getattr(self, self.__source_attr__)[key] = value
	def __delitem__(self, key):
		'''
		'''
		del getattr(self, self.__source_attr__)[key]
	def __iter__(self):
		'''
		'''
		return getattr(self, self.__source_attr__).__iter__()
	
	# 2nd generation methods:
	def __contains__(self, key):
		'''
		'''
		return key in getattr(self, self.__source_attr__)

	def __len__(self):
		'''
		'''
		return len(getattr(self, self.__source_attr__))
	

#---------------------------------------------------ComparableMapping---
class ComparableMapping(BasicMapping):
	'''
	this defines the basic comparability interface for the basic mapping.
	'''
	# 2nd generation methods:
##	def __cmp__(self, other):
##		'''
##		'''
##		##!!! ugly !!!##
##		if hasattr(other, '__iter__') and hasattr(other, '__getitem__'):
##			return cmp(dict([ (k, self[k]) for k in self ]), dict([ (k, other[k]) for k in other ]))
##		return -1

	def __eq__(self, other):
		'''
		'''
		if hasattr(other, '__iter__') and hasattr(other, '__getitem__'):
			return dict([ (k, self[k]) for k in self ]) == dict([ (k, other[k]) for k in other ])
		return False
	def __ne__(self, other):
		'''
		'''
		return not self == other

	def __gt__(self, other):
		'''
		'''
		if hasattr(other, '__iter__') and hasattr(other, '__getitem__'):
			return dict([ (k, self[k]) for k in self ]) > dict([ (k, other[k]) for k in other ])
		return False
	def __lt__(self, other):
		'''
		'''
		if hasattr(other, '__iter__') and hasattr(other, '__getitem__'):
			return dict([ (k, self[k]) for k in self ]) < dict([ (k, other[k]) for k in other ])
		return False
	def __ge__(self, other):
		'''
		'''
		if hasattr(other, '__iter__') and hasattr(other, '__getitem__'):
			return dict([ (k, self[k]) for k in self ]) >= dict([ (k, other[k]) for k in other ])
		return False
	def __le__(self, other):
		'''
		'''
		if hasattr(other, '__iter__') and hasattr(other, '__getitem__'):
			return dict([ (k, self[k]) for k in self ]) <= dict([ (k, other[k]) for k in other ])
		return False


#------------------------------------------MappingWithIteratorMethods---
class MappingWithIteratorMethods(BasicMapping):
	'''
	this defines the mapping iterators.
	'''
	# 2nd generation methods:
	def iterkeys(self):
		'''
		'''
		for k in self:
			yield k
	def itervalues(self):
		'''
		'''
		for k in self:
			yield self[k]
	def iteritems(self):
		'''
		'''
		for k in self:
			yield k, self[k]


#-----------------------------------------MappingWithListConstructors---
class MappingWithListConstructors(BasicMapping):
	'''
	this defines the mapping list constructors.
	'''
	# 2nd generation methods:
	def keys(self):
		'''
		'''
		return list(self)
	def values(self):
		'''
		'''
		return [ self[k] for k in self ]
	def items(self):
		'''
		'''
		return [ (k, self[k]) for k in self ]


#-----------------------------------------------MappingWithGetMethods---
class MappingWithGetMethods(BasicMapping):
	'''
	this defines the get and setdefault methods.
	'''
	# 2nd generation methods:
	def get(self, key, default=_marker):
		'''
		'''
		if key in self:
			return self[key]
		elif default == _marker:
			raise KeyError, (len(self) == 0 and 'get(): dictionary is empty' or '%s' % key)
		return default
	def setdefault(self, key, default=None):
		'''
		'''
		if key not in self:
			self[key] = default
		return self.get(key, default)


#--------------------------------------------MappingWithModifyMethods---
class MappingWithModifyMethods(BasicMapping):
	'''
	this defines the mapping in-place modification methods.
	'''
	# 2nd generation methods:
	def pop(self, key, default=_marker):
		'''
		'''
		if key in self:
			o = self[key]
			del self[key]
			return o
		elif default == _marker:
			raise KeyError, (len(self) == 0 and 'pop(): dictionary is empty' or '%s' % key)
		return default
	def popitem(self):
		'''
		'''
		# fake loop!! :))
		for k in self:
			return k, self[k]
		raise KeyError, 'popitem(): dictionary is empty'

	def clear(self):
		'''
		'''
		for k in self:
			del self[k]
	def update(self, data):
		'''
		'''
		for k in data:
			self[k] = data[k]


#--------------------------------------------MappingWithModifyMethods---
class MappingWithMappingConstructors(BasicMapping):
	'''
	this defines mapping methods that create new mappings.
	'''
	# 2nd generation methods:
	def copy(self):
		'''
		'''
		o = self.__class__()
		for k in self:
			o[k] = self[k]
		return o
	def fromkeys(self, keys, value=None):
		'''
		'''
		o = self.__class__()
		for k in keys:
			o[k] = value
		return o


#----------------------------------------------MappingWithTestMethods---
class MappingWithTestMethods(BasicMapping):
	'''
	this defines test/predicate methods.
	'''
	# 2nd generation methods:
	def has_key(self, key):
		'''
		'''
		return key in self


#--------------------------------------------------MappingWithMethods---
# Q: should this be split into finer-grained classes???
class MappingWithMethods(MappingWithIteratorMethods, 
						 MappingWithListConstructors, 
						 MappingWithGetMethods,
						 MappingWithModifyMethods,
						 MappingWithMappingConstructors,
						 MappingWithTestMethods):
	'''
	this defines the mapping interface methods (as in dict).
	'''
	pass


#-------------------------------------------------------------Mapping---
class Mapping(MappingWithMethods, ComparableMapping):
	'''
	this defines the basic complete mapping.
	'''
	pass


#------------------------------------------------------------DictLike---
class DictLike(Mapping):
	'''
	this defines a dict like.
	'''
	def __init__(self, *pargs, **nargs):
		'''
		'''
		parg_len = len(pargs)
		if parg_len not in (0, 1):
			raise TypeError, '%s expected at most 1 arguments (got %s).' % (self.__class__, len(pargs))
		elif parg_len == 1:
			# seq...
			seq = pargs[0]
			try:
				for i, o in enumerate(seq):
					e = list(o)
					if len(e) != 2:
						raise TypeError, 'length of element %s must be 2 (got: %s).' % (i, len(e))
					self[e[0]] = e[1]
			except:
				raise TypeError, 'can\'t convert element #%s of sequence to list.' % i
		if len(nargs) > 0:
			# mapping...
			for k in nargs:
				self[k] = nargs[k]
	


#-----------------------------------------------------------------------
# XXX move this elsewhere...

import pli.pattern.proxy.utils as proxyutils


#---------------------------------------------------Matting2AttrMixin---
class Mapping2AttrMinimalMixin(Mapping):
	'''
	provides a minimal simple drop-in mixin to enable access to the objects 
	namespace through a mapping interface.

	NOTE: this shadows the already defined functionality.
	'''
	proxyutils.proxymethods((
			# minimal set...
			'__getitem__',
			'__setitem__',
			'__delitem__',
			'__iter__',
			# for speed...
			'__contains__',
			'__len__',
		), '__dict__')


#---------------------------------------------------Matting2AttrMixin---
class Mapping2AttrMixin(Mapping2AttrMinimalMixin):
	'''
	provides a simple drop-in mixin to enable access to the objects 
	namespace through a mapping interface.

	NOTE: this shadows the already defined functionality.
	'''
	proxyutils.proxymethods((
			# other methods...
			'kyes',
			'iterkeys',
			'values',
			'itervalues',
			'items',
			'iteritems',
			'get',
			'pop',
			'update',
			'copy',
		), '__dict__')




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
