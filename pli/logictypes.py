#=======================================================================

__version__ = '''0.1.12'''
__sub_version__ = '''20050406044155'''
__copyright__ = '''(c) Alex A. Naanou 2003'''

__doc__ = '''\
this module defines a number of utilities and objects to assist advanced
usage of standard python types.
'''

#-----------------------------------------------------------------------

import pli.pattern.mixin.mapping as mapping


#-----------------------------------------------------------------------
# TODO create a logic proxy, with adapters....
#      UNION(*p), INTERSECTION(*n), ...
#
#------------------------------------------------------------_Compare---
class _Compare(object):
	'''
	'''
	def __init__(self, eq):
		self._eq = eq
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
Any = ANY = _Compare(0)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# this is bigger than any value...
MAXIMUM = _Compare(1)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# this is smaller than any value...
MINIMUM = _Compare(-1)



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
class oftype(Pattern):
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
		return not isinstance(other, self._types) is True
	def __gt__(self, other):
		return False
	def __ge__(self, other):
		return True
	def __lt__(self, other):
		return False
	def __le__(self, other):
		return True

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
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
# general type groups predicates...
isnumber = oftype(int, float, complex) 
isstring = oftype(str, unicode)
issequence = oftype(list, tuple)

isiterabletype = oftype(str, unicode, list, tuple, dict)



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


#-----------------------------------------------------------DictUnion---
##class DictUnion(mapping.MappingWithMethods):
# TODO split this into several mix-ins....
class DictUnion(mapping.Mapping):
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
	def __getitem__(self, name):
		'''
		'''
		for m in self._members:
			if name in m:
				return m[name]
		raise KeyError, 'key "%s" is not present in any of the members.' % name
	def __setitem__(self, name,  value):
		'''
		'''
		# find source...
		# set
		raise TypeError, 'can\'t add values to a dict union object.'
	def __delitem__(self, name):
		'''
		'''
		raise TypeError, 'can\'t delete values from a dict union object.'
	def __contains__(self, name):
		'''
		'''
		for m in self._members:
			if name in m:
				return True
		return False
	def __iter__(self):
		'''
		'''
		seen = []
		for m in self._members:
			for n in m:
				if n not in seen:
					seen += [n]
					yield n
	# the dict union specific interface...
	##!!! revise...
	def unite(self, *others):
		'''
		add members to the union object.

		NOTE: this method will add members to the top of the pririty
		      stack.
		'''
		others = list(others)
		others.reverse()
		self._members = tuple(others) + self._members
	##!!! revise...
	def tailunite(self, *others):
		'''
		this is the same as unite but adds low priority members (to the
		botom of the priority stack).
		'''
		others = list(others)
		others.reverse()
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
	def members(self):
		'''
		'''
		return self._members
	##!!! revise...
	def popmember(self, index=0):
		'''

		NOTE: this by default will remove the highest priority member.
		'''
		m = list(self._members)
		res = m.pop(index)
		self._members = tuple(m)
		return res
	def itermembers(self):
		'''
		'''
		for m in self._members:
			yield m
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
	def todict(self):
		'''
		this will return a dict copy of the DictUnion object.
		'''
		return dict(self.items())


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
# enable ocal key delete...
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
			return self._locals.get(name, super(WritableDictUnion, self).__getitem__(name))
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


#-------------------------------------------------------DictIntersect---
##class DictIntersect(object):
##	'''
##	'''
##	pass


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



if __name__ == '__main__':
	d0 = {'a':1, 'b':2}
	d1 = {'c':'!!!!!', 'b':'x'}

	D = WritableDictUnion(d0, d1)

	D['b'] = '*****'

	print D.todict()
	print d0, d1

	print 'a' in D




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
