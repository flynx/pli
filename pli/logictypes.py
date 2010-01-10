#=======================================================================

__version__ = '''0.1.21'''
__sub_version__ = '''20091228013755'''
__copyright__ = '''(c) Alex A. Naanou 2003'''

__doc__ = '''\
this module defines a number of utilities and objects to assist advanced
usage of standard python types.
'''

#-----------------------------------------------------------------------

import copy

import pli.pattern.mixin.mapping as mapping
import pli.pattern.proxy.utils as proxyutils
import pli.objutils as objutils


#-----------------------------------------------------------------------
#-------------------------------------------------------------Pattern---
class Pattern(object):
	'''
	'''
	pass


#-------------------------------------------------------------Compare---
class Compare(Pattern):
	'''
	'''
	original = True

	def __init__(self, eq, name=None):
		self._eq = eq
		if name == None:
			self._name = self.__class__.__name__
		else:
			self._name = name
	def __call__(self):
		'''
		create a copy of self.
		'''
		res = copy.copy(self)
		res.original = False
		return res
	def __repr__(self):
		if self.original is True:
			return self._name
		return '<%s object %s>' % (self._name, hash(self))
	# comparison methods...
	def __cmp__(self, other):
		return self._eq
	def __eq__(self, other):
		return self._eq == 0
	def __ne__(self, other):
		return self._eq != 0
	def __gt__(self, other):
		return self._eq > 0
	def __ge__(self, other):
		return self._eq >= 0
	def __lt__(self, other):
		return self._eq < 0
	def __le__(self, other):
		return self._eq <= 0

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# this will compare to any value as equel (almost oposite to None)
Any = ANY = Compare(0, 'ANY')

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# this is bigger than any value...
MAXIMUM = Compare(1, 'MAXIMUM')

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# this is smaller than any value...
MINIMUM = Compare(-1, 'MINIMUM')


#-----------------------------------------------------------------AND---
class AND(Pattern):
	'''
	AND(A, B[, ..]) == X iff X == A and X == B [and ..]
	'''
	def __init__(self, A, B, *patterns):
		'''
		'''
		self.patterns = (A, B) + patterns
	def __repr__(self):
		'''
		'''
		return 'AND(%s)' % ', '.join(repr(p) for p in self.patterns)
	# XXX revise comparison order...
	def __eq__(self, other):
		return False not in [ other == p for p in self.patterns ]
	def __ne__(self, other):
		for p in self.patterns:
			if other != p:
				return True
		return False


#------------------------------------------------------------------OR---
class OR(Pattern):
	'''
	OR(A, B[, ..]) == X iff X == A or X == B [and ..]
	'''
	def __init__(self, A, B, *patterns):
		'''
		'''
		self.patterns = (A, B) + patterns
	def __repr__(self):
		'''
		'''
		return 'OR(%s)' % ', '.join(repr(p) for p in self.patterns)
	# XXX revise comparison order...
	def __eq__(self, other):
		for p in self.patterns:
			if other == p:
				return True
		return False
	def __ne__(self, other):
		return False not in [ other != p for p in self.patterns ]


#-----------------------------------------------------------------NOT---
class NOT(Pattern):
	'''
	NOT(A) == X iff A != X
	'''
	def __init__(self, obj):
		self.obj = obj
	def __repr__(self):
		'''
		'''
		return 'NOT(%r)' % self.obj
	def __eq__(self, other):
		return not (self.obj == other)
	def __ne__(self, other):
		return not (self.obj != other)


#------------------------------------------------------------------IN---
# NOTE: this looks odd :)
class IN(Pattern):
	'''
	IN(A, B) == X iff B == X and A in X
	'''
	def __init__(self, obj, container=ANY):
		self.obj = obj
		self.container = container
	def __repr__(self):
		'''
		'''
		return 'IN(%r, %r)' % (self.obj, self.container)
	def __eq__(self, other):
		return self.container == other and self.obj in other
	def __ne__(self, other):
		return self.container != other or self.obj not in other


#------------------------------------------------------------------AT---
class AT(Pattern):
	'''
	AT(A, B) == X iff A in X and X[B] == A

	NOTE: this works as good as python's containers accept patterns.
		  this mostly amounts to staying clear of using patterns as 
		  indexes.
	'''
	def __init__(self, obj, position=ANY):
		self.obj = obj
		self.position = position
	def __repr__(self):
		return 'AT(%r, %r)' % (self.obj, self.position)
	def __eq__(self, other):
		try:
			if other == SEQUENCE:
				return self.obj in other \
						and other[self.position] == self.obj
			else:
				# mappings...
				return self.obj in other.values() \
						and other[self.position] == self.obj
		except (KeyError, IndexError):
			return False
	def __ne__(self, other):
		try:
			if other == SEQUENCE:
				return self.obj not in other \
						or other[self.position] != self.obj
			else:
				return self.obj not in other.values() \
						or other[self.position] != self.obj
		except (KeyError, IndexError):
			return False



#-----------------------------------------------------------------------
# TODO rename...
# TODO add chaining support...
# TODO add shadowing support... (via NOTHING, afect chained values)
class ErxCONTAINER(Pattern, mapping.Mapping):
	'''

	has the folowing notions:
		- length, if content is sizable or has length
		- content/containment
		- bounds
	'''
	def __init__(self, data=()):
		objutils.termsuper(ErxCONTAINER, self).__init__(data)
		self._data = data
	# mapping-like interface...
	# NOTE: this is mainly needed to bypass pythons dict optimizations
	# 		thus enabling patterns... 
	def __getitem__(self, pattern):
		'''
		'''
		# XXX might be good to make this check the obvious first...
		for e in self:
			if pattern == e:
				return e
		# XXX should this fail like this??
		raise KeyError, pattern
	def __setitem__(self, pattern, value):
		'''
		'''
		del self[pattern]
		self._data += (value,)
	def __delitem__(self, pattern):
		'''
		'''
		res = list(self)
		while pattern in res:
			res.remove(pattern)
		self._data = tuple(res)
	##!!! need raw iter, to iterate and detect content items...
	def __iter__(self):
		'''
		'''
		for e in self._data:
			if isinstance(e, CONTENT):
				for ee in e:
					yield ee
			else:
				yield e
	# pattern interface...
	def __eq__(self, other):
		'''
		'''
		for e in other:
			if e not in self:
				return False
		return len(self) == len(other)
	def __ne__(self, other):
		'''
		'''
		pass


C = ErxCONTAINER


##!!! should this be a view or a container?
class ORDERED(ErxCONTAINER):
	'''
	takes a container as argument and returns a container that also considers
	the nothion of order.
	'''
	def __eq__(self, other):
		'''
		'''
		if len(self) == len(other):
			return tuple(self) == tuple(other)
		return False
	def __ne__(self, other):
		'''
		'''
		pass


##!!! should this be a view or a container?
class CONTENT(ErxCONTAINER):
	'''
	like a container but matches a part of a container.
	'''
		


# views...
class VIEW(ErxCONTAINER):
	'''
	'''
	def __init__(self, pattern, container):
		'''
		'''
		objutils.termsuper(VIEW, self).__init__()
		self.pattern = pattern
		self.container = container

	def __getitem__(self, pattern):
		'''
		'''
		try:
			return self.container[AND(pattern, self.pattern)]
		except KeyError:
			raise KeyError, pattern
	def __setitem__(self, pattern, value):
		'''
		'''
		try:
			self.container[AND(pattern, self.pattern)] = value
		except KeyError:
			raise KeyError, pattern
	def __delitem__(self, pattern):
		'''
		'''
		del self.container[AND(pattern, self.pattern)]
	def __iter__(self):
		'''
		'''
		pattern = self.pattern
		for e in self.container:
			if pattern == e:
				yield e


# XXX this should match the value or item pattern...
# XXX need a reliable way to position this at next/prev values... this
#	  must be as independent of container manipulation as possible...
# XXX need an efficient way to directly position within a container...
# 	  the "visited bag" approach is BAD for very large containers!
# 	  one way to do this is to remember a "current" element. but this
# 	  will break if it is deleted or modified...
class ITEM(Pattern):
	'''
	'''
	def __init__(self, pattern, container, visited=()):
		'''
		'''
		objutils.termsuper(ITEM, self).__init__()
		self.pattern = pattern
		self.container = container
		self.visited = visited

	@property
	# XXX may be a good idea to combine value with assign a-la
	# 	  jQuery... actually, might even add delete into the mix -- we
	# 	  do have a NOTHING pattern don't we?
	# 	  ...still need some more thought.
	def value(self):
		'''
		'''
		visited = self.visited
		if len(visited) == 0:
			return self.container[self.pattern]
		elif len(visited) == 1:
			return self.container[AND(NOT(self.visited[0]), self.pattern)]
		return self.container[AND(NOT(OR(*self.visited)), self.pattern)]
	##!!! what should happen of we changed the value or updated the container 
	##!!! so as this does not have a value anymore?
	def assign(self, value):
		'''
		'''
		try:
			self.container[self.value] = value
		except KeyError:
			# this means we are not looking at a meaningfull
			# position...
			# add a new element.
			##!!! is this correct???
			self.container[NOTHING] = value
		return self
	##!!! revise...
	def delete(self):
		'''
		'''
		try:
			del self.container[self.value]
		except KeyError:
			pass
		return self

	@property
	def next(self):
		'''
		'''
		visited = self.visited + (self.value,)
		res = self.__class__(self.pattern, self.container, visited)
		# this is here to break things and to prevent ust to iterate
		# beyond where we started...
		res.value
		return res
	@property
	def prev(self):
		'''
		'''
		visited = self.visited
		# we can't iterate over the beginning...
		if len(visited) == 0:
			raise KeyError, self.pattern
		pattern = self.pattern
		container = self.container
		for v in visited[::-1]:
			if v not in container:
				# remove the non-existing elements...
				visited = visited[:-1]
				# this is to handle the case of we are positioned
				# somewhere in a chain and all the items we saw before
				# do not exist any longer...
				if len(visited) == 0:
					raise KeyError, self.pattern
				continue
		res = self.__class__(pattern, container, visited[:-1])
		# this is here to break things and to prevent ust to iterate
		# beyond where we started...
		res.value
		return res



# variable length contents...
class OF(CONTENT):
	'''
	OF(A, N) == X iff A occurs N times in X

	Pythonism for N of A in Eryx.
	'''
	def __init__(self, obj, count):
		super(OF, self).__init__()
		self.obj, self.count = obj, count
		



#-----------------------------------------------------------------------
# this is to define basic pattern combination mathematics.
# Ex:
# 	Pab = Pa | Pb		-- Pab is a pattern that will match either Pa
# 						   or Pb...
#
# Operations:
# 	|
# 	&
# 	+
# 	rep
# 	not
# 	
#
##class Pattern(object):
##	'''
##	'''
##	# cmp
##	def __eq__(self, other):
##		'''
##		'''
##		pass
##	def __ne__(self, other):
##		'''
##		'''
##		pass
##	def __gt__(self, other):
##		'''
##		'''
##		pass
##	def __ge__(self, other):
##		'''
##		'''
##		pass
##	def __lt__(self, other):
##		'''
##		'''
##		pass
##	def __le__(self, other):
##		'''
##		'''
##		pass
##	# op
##	##!!!


#--------------------------------------------------------------oftype---
class OfType(Pattern):
	'''
	this will create an object that can be used as a predicate to test type, 
	and it will copare True to objects of that type.
	'''
	def __init__(self, *types, **n):
		'''
		'''
		self._types = types
		if 'doc' in n:
			self.__doc__ = n['doc']
	def __call__(self, other):
		'''
		test if the the other object object is of type.
		'''
		return isinstance(other, self._types) is True
	__eq__ = __call__
	def __ne__(self, other):
		return not self(other) 
##		return not isinstance(other, self._types) is True
	def __gt__(self, other):
		return False
	def __ge__(self, other):
		return True
	def __lt__(self, other):
		return False
	def __le__(self, other):
		return True

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
oftype = OfType


#-------------------------------------------------OfTypeWithPredicate---
class OfTypeWithPredicate(OfType):
	'''
	'''
	def __call__(self, other):
		'''
		'''
		if self.__predicate__(other):
			return super(OfTypeWithPredicate, self).__call__(other)
		return False
	__eq__ = __call__
	# NOTE: this is intended to be oveloaded... (by default it will
	#       break the object...)
	def __predicate__(self, other):
		'''
		this will check the object.

		must return True or False.
		'''
		raise NotImplementedError


#----------------------------------------------OfTypeWithArgPredicate---
# WARNING: this might not be compatible with CPythons pickle...
class OfTypeWithArgPredicate(OfTypeWithPredicate):
	'''
	'''
	def __init__(self, *p, **n):
		'''
		'''
		super(OfTypeWithArgPredicate, self).__init__(*p, **n)
		if 'predicate' in n:
			self.__predicate__ = n['predicate']
		else:
			raise TypeError, 'a predicate must be given.'

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

ofptype = OfTypeWithArgPredicate


#-----------------------------------------------------------------------
# simple type predicates...
INT = isint = oftype(int)
FLOAT = isfloat = oftype(float)
COMPLEX = iscomplex = oftype(complex)

STR = isstr = oftype(str)
UNICODE = isunicode = oftype(unicode)

LIST = islist = oftype(list)
TUPLE = istuple = oftype(tuple)
DICT = isdict = oftype(dict)
SET = isset = oftype(set)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# other odd predicates :)
ODD = isodd = ofptype(int, long, predicate=lambda o: o%2 != 0)
EVEN = iseven = ofptype(int, long, predicate=lambda o: o%2 == 0)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# general type groups predicates...
NUMBER = isnumber = oftype(int, float, complex) 

STRING = isstring = oftype(str, unicode)

SEQUENCE = issequence = oftype(list, tuple)
CONTAINER = iscontainer = oftype(list, tuple, dict, set)

ITERABLETYPE = isiterabletype = oftype(str, unicode, list, tuple, dict, set)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
IDENT = isident = ofptype(str, unicode, predicate=lambda o: len(o) > 0 \
												and False not in [ c.isalnum() \
																	for c in o.split('_') ] \
												and  o[0].isalpha())


###-----------------------------------------------------------------------
##class isLike(Pattern):
##	'''
##	'''
##	def __init__(self, *types, **n):
##		'''
##		'''
##		self._types = types
##		if 'doc' in n:
##			self.__doc__ = n['doc']
##	def __call__(self, other):
##		'''
##		test if the the other object object is of type.
##		'''
##		return isinstance(other, self._types) is True
##	__eq__ = __call__
##	def __ne__(self, other):
##		return not isinstance(other, self._types) is True
##	def __gt__(self, other):
##		return False
##	def __ge__(self, other):
##		return True
##	def __lt__(self, other):
##		return False
##	def __le__(self, other):
##		return True



#-----------------------------------------------------------------------
#-------------------------------------------------------dictcopyunite---
def dictcopyunite(*members):
	'''
	'''
	res = {}
	for m in members:
		res.update(m)
	return res


#---------------------------------------------------AbstractDictChainMixin---
# TODO split this into several mix-ins....
# NOTE: this was not designed to be used directly...
class AbstractDictChainMixin(mapping.Mapping):
	'''
	'''
	# mapping interface...
	def __getitem__(self, name):
		'''
		'''
		for m in self.__iterchainmembers__():
			if name in m:
				return m[name]
		raise KeyError, 'key "%s" is not present in any of the members.' % name
	def __setitem__(self, name,  value):
		'''
		'''
		# find source...
		# set
		raise TypeError, 'can\'t add values to an AbstractDictChainMixin object.'
	def __delitem__(self, name):
		'''
		'''
		raise TypeError, 'can\'t delete values from an AbstractDictChainMixin object.'
	def __contains__(self, name):
		'''
		'''
		for m in self.__iterchainmembers__():
			if name in m:
				return True
		return False
	def __iter__(self):
		'''
		'''
		seen = []
		for m in self.__iterchainmembers__():
			for n in m:
				if n not in seen:
					seen += [n]
					yield n
	# AbstractDictChainMixin specific extension interface...
##	def __iterchainmembers__(self):
##		'''
##		this will yield dicts, elements of the chain.
##		'''
##		raise NotImplementedError
	# AbstractDictChainMixin specific methods...
	def todict(self):
		'''
		this will return a dict copy of the DictUnion object.
		'''
		return dict(self.items())


#-----------------------------------------------------------DictUnion---
# XXX might be good to combine this and DictChain... (this will be
#     quite easy using the itermembers instead of self._members)
class DictUnion(AbstractDictChainMixin):
	'''
	this is a dict like object, that acts as a union of its members but
	without modifieng its members in any way.

	this is similar to a sequential update of all members, but retains
	the container information for each item, and does not have the
	overhead of creating a new resulting dict.

	NOTE: because of the nature of dicts, the later added members (unite)
	      have higher priority than the former.
	NOTE: the members added in one call (be it __init__, unite or tailunite)
		  have descending priority -- first highest last lowest.
	NOTE: due to ints nature this object is *live*, e.g. it emidiatly 
	      reflects all modifications to its members as they are modified.
	'''
	_members = ()

	def __init__(self, *members):
		'''
		'''
		members = list(members)
		members.reverse()
		self._members = tuple(members)
	# AbstractDictChainMixin specific extension interface...
	def __iterchainmembers__(self):
		'''
		'''
		for m in self._members:
			yield m
	# the DictUnion specific interface...
	# XXX should these depend on __iterchainmembers__ or directly on
	#     _members????
	def unite(self, *others):
		'''
		add members to the union object.

		NOTE: this method will add members to the top of the pririty
		      stack.
		NOTE: the elements are added in sequence, thus, the later elements
		      have higher priority.
		'''
		others = list(others)
		others.reverse()
		self._members = tuple(others) + self._members
	def tailunite(self, *others):
		'''
		this is the same as unite but adds low priority members (to the
		botom of the priority stack).

		NOTE: the elements are added in sequence, thus, the later elements
		      have lower priority.
		'''
		others = list(others)
		self._members = self._members + tuple(others)
	def memberindex(self, obj):
		'''
		'''
		return list(self._members).index(obj)
	def removemember(self, obj):
		'''
		'''
		if obj in self._members:
			self._members = tuple(list(self._members).remove(obj))
			return
		raise TypeError, '%s does not contain %s as a member.' % (self, obj)
	def clearmembers(self):
		'''
		'''
##		del self._members[:]
		self._members = ()
	def members(self):
		'''
		'''
		return self._members
	def popmember(self, index=0):
		'''

		NOTE: this by default will remove the highest priority member.
		'''
		m = list(self._members)
		res = m.pop(index)
		self._members = tuple(m)
		return res
	itermembers = __iterchainmembers__
	def getcontainerof(self, name):
		'''
		'''
		for m in self._members:
			if name in m:
				return m
		raise KeyError, '%s does not contain "%s"' % (self, name)
	def getallcontainersof(self, name):
		'''
		'''
		res = []
		for m in self._members:
			if name in m:
				res += [m]
		if res == []:
			raise KeyError, '%s does not contain "%s"' % (self, name)
		return res


#---------------------------------------------------WritableDictUnion---
# modes:
# get the last occurance...
GET_LOCAL_LAST = 0
# get the first occurance...
GET_LOCAL_FIRST = 1

# if key is not contained in union, add it to the last member...
WRITE_NEW_TO_LAST = 0
# if key is not contained in union, add it to the first member...
WRITE_NEW_TO_FIRST = 2
# if the key is present in the union more than once, override the last
# occurance...
WRITE_TO_LAST_OWNER = 0
# if the key is present in the union more than once, override the first
# occurance...
WRITE_TO_FIRST_OWNER = 4
# write to local (temporary) dict...
# NOTE: if this is set, other write opts will be ignored...
WRITE_LOCAL = 8
# disable write...
WRITE_DISABLED = 16

# delete the last occurance of key...
DELETE_LAST = 0
# delete the first occurance of key...
DELETE_FIRST = 32 
# enable local key delete...
DELETE_LOCAL = 64
# disable deletion of anything but local keys...
DELETE_LOCAL_ONLY = 128
# disable delete...
DELETE_DISABLED = 256

class WritableDictUnion(DictUnion):
	'''
	'''
	__modify_props__ = GET_LOCAL_FIRST \
						| WRITE_NEW_TO_FIRST \
						| WRITE_TO_FIRST_OWNER \
						| DELETE_FIRST \
						| DELETE_LOCAL

	def __init__(self, *members):
		'''
		'''
		super(WritableDictUnion, self).__init__(*members)
		self._locals = {}
	def __getitem__(self, name):
		'''
		'''
		props = getattr(self, '__modify_props__', 0)
		if props & GET_LOCAL_FIRST:
			if name in self._locals:
				return self._locals[name]
			else:
				return super(WritableDictUnion, self).__getitem__(name)
		try:
			return super(WritableDictUnion, self).__getitem__(name)
		except KeyError:
			if name in self._locals:
				return self._locals[name]
			raise KeyError, name
	def __setitem__(self, name, value):
		'''
		'''
		props = getattr(self, '__modify_props__', 0)
		if props & WRITE_DISABLED:
			raise TypeError, 'can\'t add values to a dict union object (writing is disabled).'
		elif props & WRITE_LOCAL:
			self._locals[name] = value
		else:
			try:
				if props & WRITE_TO_FIRST_OWNER:
					self.getallcontainersof(name)[0][name] = value
				else:
					self.getallcontainersof(name)[-1][name] = value
			except KeyError:
				##!!! problem if there are no memebers... raise an apropriate error...
				if props & WRITE_NEW_TO_FIRST:
					self.members()[0][name] = value
				else:
					self.members()[-1][name] = value
	def __contains__(self, name):
		'''
		'''
		if name in self._locals or super(WritableDictUnion, self).__contains__(name):
			return True
		return False
	def __delitem__(self, name):
		'''
		'''
		props = getattr(self, '__modify_props__', 0)
		if props & DELETE_DISABLED:
			raise TypeError, 'can\'t delete items (deletion is disabled).'
		if props & DELETE_LOCAL and name in self._locals:
			del self._locals[name]
		elif not props & DELETE_LOCAL_ONLY:
			if props & DELETE_FIRST:
				del self.getallcontainersof(name)[0][name]
			else:
				del self.getallcontainersof(name)[-1][name]
		else:
			raise TypeError, 'can\'t delete from contained dicts.'
	def __iter__(self):
		'''
		'''
		seen = []
		props = getattr(self, '__modify_props__', 0)
		if props & GET_LOCAL_FIRST:
			for k in self._locals:
				yield k
				seen += [k]
		for k in super(WritableDictUnion, self).__iter__():
			if k not in seen:
				yield k
				seen += [k]
		if not props & GET_LOCAL_FIRST:
			for k in self._locals:
				if k not in seen:
					yield k



#-------------------------------------------------------DictTypeUnion---
# WARNING: this is not done!
class DictTypeUnion(DictUnion, dict):
	'''
	this is a diriviation from dict that can contain oun data.
	'''
	##!!!
	pass


#---------------------------------------------------BasicMappingChain---
class BasicMappingChain(AbstractDictChainMixin, mapping.Mapping):
	'''
	
	NOTE: this class was designed as a basic base class (atleast the
	      __iterchainmembers__ method should be overloaded).
	NOTE: do not forget to call the original __iterchainmembers__.
	NOTE: this, if used as-is will not differ from a dict.
	'''
	_dict_data = None

	def __init__(self, *p, **n):
		'''
		'''
		self._dict_data = {}
		super(BasicMappingChain, self).__init__(*p, **n)
	proxyutils.proxymethods((
		'__setitem__',
		'__delitem__',
		'clear',
		), '_dict_data')
	def __iterchainmembers__(self):
		'''
		'''
		yield self._dict_data

	def localkeys(self):
		'''
		return list of local to the current node keys.
		'''
		return self._dict_data.keys()


#--------------------------------------------------------MappingChain---
class MappingChain(BasicMappingChain):
	'''
	this is a basic mapping chain element.

	when a key can not be found in the local data then the request is 
	forwarded to the .chain_next attribute.

	NOTE: .chain_next can be None, then no other forwarding is done.
	NOTE: editing is possible only to the local data.
	'''
	chain_next = None

	def __iterchainmembers__(self):
		'''
		'''
		for v in super(MappingChain, self).__iterchainmembers__():
			yield v
		if self.chain_next != None:
			yield self.chain_next


#-----------------------------------------------MappingChainLiveMixin---
class MappingChainLiveMixin(object):
	'''
	'''
	_chain_attr_name = None
	_chain_next_obj = None
	
	chain_next = property(
			fget=lambda self: getattr(self.__chain_next_obj__, self.__chain_attr_name__),
			fset=lambda self, val: (setattr(self, '__chain_next_obj__', val[0]), 
									setattr(self, '__chain_attr_name__', val[1])))


#-----------------------------------------------------------DictChain---
class DictChain(MappingChain, mapping.DictLike):
	'''
	same as MappingChain but more dict like.

	see docs for:
		pli.logictypes.MappingChain
		pli.pattern.mixin.mapping.DictLike
	'''
	pass


#-------------------------------------------------------LiveDictChain---
class LiveDictChain(MappingChainLiveMixin, DictChain):
	'''
	'''
	pass


#---------------------------------------------------------dictchainto---
def dictchainto(dct):
	'''
	create a dictchain over a mapping.

	helper/factory function.
	'''
	d = DictChain()
	d.chain_next = dct
	return d
	

#-----------------------------------------------------livedictchainto---
def livedictchainto(obj, attr):
	'''
	create a live dictchain over a mapping.

	helper/factory function.
	'''
	d = LiveDictChain()
	d.chain_next = (obj, attr)
	return d



#-----------------------------------------------------------------------
#---------------------------------------------------------ObjectUnion---
# TODO rename....
# TODO split to various mix-ins...
##class BasicObjectUnion(object):
class ObjectUnion(object):
	'''
	this represents the union of the attr of several objects.
	'''
	def __init__(self, *members):
		'''
		'''
		members = list(members)
		members.reverse()
		self._members = tuple(members)
	##!!!
	def __getattr__(self, name):
		'''
		'''
		for o in self._members:
			if hasattr(o, name):
				return getattr(o, name)
##			# Q: which is faster, this or the "if hasattr..."???
##			try:
##				return getattr(o, name)
##			except AttributeError:
##				pass
		raise AttributeError, name
##	def __setattr__(self, name, value):
##		'''
##		'''
##		raise TypeError, 'ca\'t write attributes of a ObjectUnion object.'
##	def __delattr__(self, name, value):
##		'''
##		'''
##		pass
	def __hasattr__(self, name):
		'''
		'''
		for o in self._members:
			if hasattr(o, name):
				return True
		return False
	# interface methods...
	##!!!


#=======================================================================
if __name__ == '__main__':
	d0 = {'a':1, 'b':2}
	d1 = {'c':'!!!!!', 'b':'x'}

	D = WritableDictUnion(d0, d1)

	D['b'] = '*****'

	print D['b']

	print D.todict()
	print d0, d1

	print 'a' in D

	print isodd(3), isodd(6)

	print isident('b0_c'), isident('aaa'), isident(''), isident('321_4')

	# check the dict chain...
	d = DictChain(a=1, b=2, c=3)
	print d.todict()
	d.chain_next = DictChain(c=4, d=5, e=6)
	print d.todict()
	d.chain_next.chain_next = dict(e=7, f=8, g=9)
	print d.todict()


	class X(object):
		xxx = dict(a=1, b=2)

	x = X()

	ld = livedictchainto(x, 'xxx')
	ld['b'] = 3
	ld['c'] = 4

	print ld.keys()

	x.xxx = {}

	print ld.keys()

	ld['aaa'] = 'bbb'

	print ld.keys()

	del ld['aaa']

	print ld.keys()

	print ANY, ANY()

	print AND((1, ANY), (ANY, 2))
	print AND((1, ANY), (ANY, 2)) == (1, 2)
	print AND((1, ANY), (ANY, 2)) != (ANY, 9)
	print OR((1, ANY), (ANY, 2)) == (1, 8)
	print OR((1, ANY), (ANY, 2)) != (7, 8)

	print AT(1, 10) == range(100)
	print AT(10, 10) == range(100)


	e = C((1, 2, 3, 'a', 'b', 'c', CONTENT(C((1.1, 2.2, 3.3)))))

	print e

	print e[ANY]
	print e[STRING]
	print e[3]
	print e[FLOAT]
	print len(e)
	##!!! there should be a way to access content items...
##	print e[CONTENT]

	print e == (1, 2, 3, 'a', 'c', 1.1, 2.2, 3.3, 'b')
	print ORDERED(e) == (1, 2, 3, 'a', 'c', 1.1, 2.2, 3.3, 'b')
	print ORDERED(e) == (1, 2, 3, 'a', 'b', 'c', 1.1, 2.2, 3.3)
	print ORDERED(CONTENT(e)) == (1, 2, 3, 'a', 'b', 'c', 1.1, 2.2, 3.3)


	v = VIEW(NUMBER, e)
	print len(v)
	v[INT] = 1
	print len(v)

	print list(v)

	i = ITEM(NUMBER, e)
	print i.value
	print i.next.value
	print i.next.next.value
	print i.next.next.next.value
	print i.next.next.next.assign(2)
	print i.next.next.next.value
	# this will assign a value that does not match the pattern of
	# either the item or the view. thus, it will not appear in either
	# of them.
	# ...assigning to an item an that item still not having a value may
	# be counter intuitive.
	# another similar case would be assigning a value that we already
	# passed (this depends on the scheme of the positioning algorithm
	# of the item...)
	##!!! this makes the item inconsistent... 
	##!!! ...asigning t a value incompatible to the pattern will make the 
	##!!! item object inconsistent -- heed to handle this in some obvious way
##	print i.next.next.next.assign('aaa')
##	print i.next.next.next
	print list(v)
	print list(e)

	print i.value
	print i.next.value
	print i.next.next.value
	print i.next.next.next.value
	print i.next.next.next.prev.value
	print i.next.next.next.prev.prev.value
	print i.next.next.next.prev.prev.prev.value

	##!!! this should be True both ways...
	print CONTENT((2, 3, 4)) == range(10)
	print range(10) == CONTENT((2, 3, 4))



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
