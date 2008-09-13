#=======================================================================

__version__ = '''0.1.21'''
__sub_version__ = '''20080913125144'''
__copyright__ = '''(c) Alex A. Naanou 2003'''

__doc__ = '''\
this module defines a number of utilities and objects to assist advanced
usage of standard python types.
'''

#-----------------------------------------------------------------------

import copy

import pli.pattern.mixin.mapping as mapping
import pli.pattern.proxy.utils as proxyutils


#-----------------------------------------------------------------------
# TODO create a logic proxy, with adapters....
#      UNION(*p), INTERSECTION(*n), ...
#
#-------------------------------------------------------------Pattern---
class Pattern(object):
	'''
	'''
	pass


#-------------------------------------------------------------Compare---
class Compare(Pattern):
	'''
	'''
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
		return copy.copy(self)
	def __repr__(self):
		return '<%s object at %s>' % (self._name, hash(self))
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
	'''
	def __init__(self, *patterns):
		'''
		'''
		self.patterns = patterns
	
	# XXX revise comparison order...
	def __eq__(self, other):
		return False not in [ other == p for p in self.patterns ]
	def __ne__(self, other):
		for p in self.patterns:
			if other != p:
				return True
		return False
	# XXX do we need anthing else here??


#------------------------------------------------------------------OR---
class OR(Pattern):
	'''
	'''
	def __init__(self, *patterns):
		'''
		'''
		self.patterns = patterns
	
	# XXX revise comparison order...
	def __eq__(self, other):
		for p in self.patterns:
			if other == p:
				return True
		return False
	def __ne__(self, other):
		return False not in [ other != p for p in self.patterns ]
	# XXX do we need anthing else here??



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
class Pattern(object):
	'''
	'''
	# cmp
	def __eq__(self, other):
		'''
		'''
		pass
	def __ne__(self, other):
		'''
		'''
		pass
	def __gt__(self, other):
		'''
		'''
		pass
	def __ge__(self, other):
		'''
		'''
		pass
	def __lt__(self, other):
		'''
		'''
		pass
	def __le__(self, other):
		'''
		'''
		pass
	# op
	##!!!


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
isint = oftype(int)
isfloat = oftype(float)
iscomplex = oftype(complex)

isstr = oftype(str)
isunicode = oftype(unicode)

islist = oftype(list)
istuple = oftype(tuple)
isdict = oftype(dict)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# other odd predicates :)
isodd = ofptype(int, long, predicate=lambda o: o%2 != 0)
iseven = ofptype(int, long, predicate=lambda o: o%2 == 0)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# general type groups predicates...
isnumber = oftype(int, float, complex) 
isstring = oftype(str, unicode)
issequence = oftype(list, tuple)

isiterabletype = oftype(str, unicode, list, tuple, dict)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
isident = ofptype(str, unicode, predicate=lambda o: len(o) > 0 \
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

	print AND((1, ANY), (ANY, 2)) == (1, 2)
	print AND((1, ANY), (ANY, 2)) != (ANY, 9)
	print OR((1, ANY), (ANY, 2)) == (1, 8)
	print OR((1, ANY), (ANY, 2)) != (7, 8)


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
