#=======================================================================

__version__ = '''0.0.04'''
__sub_version__ = '''20040724012609'''
__copyright__ = '''(c) Alex A. Naanou 2003'''

__doc__ = '''\
this module defines a number of utilities and objects to assist advanced
usage of standard python types.
'''

#-----------------------------------------------------------------------



#-----------------------------------------------------------------------
# TODO create a logic proxy, with adapters....
#      UNION(*p), INTERSECTION(*n), ...
#
#-------------------------------------------------------------_Comare---
class _Comare(object):
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
ANY = _Comare(0)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# this is bigger than any value...
MAXIMUM = _Comare(1)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# this is smaller than any value...
MINIMUM = _Comare(-1)



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
class DictUnion(object):
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
##	def __setitem__(self, name,  value):
##		'''
##		'''
##		# find source...
##		# set
##		raise TypeError, 'can\'t add values to a dict union object.'
##	def __delitem__(self, name):
##		'''
##		'''
##		raise TypeError, 'can\'t delete values from a dict union object.'
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
##	def __len__(self):
##		'''
##		'''
##		pass
##	def __cmp__(self):
##		'''
##		'''
##		pass
##	def __eq__(self):
##		'''
##		'''
##		pass
##	def __ge__(self):
##		'''
##		'''
##		pass
##	def __gt__(self):
##		'''
##		'''
##		pass
##	def __le__(self):
##		'''
##		'''
##		pass
##	def __lt__(self):
##		'''
##		'''
##		pass
##	def __ne__(self):
##		'''
##		'''
##		pass
##	def __repr__(self):
##		'''
##		'''
##		pass
##	def __str__(self):
##		'''
##		'''
##		pass
##	def __reduce__(self):
##		'''
##		'''
##		pass
##	def __reduce_ex__(self):
##		'''
##		'''
##		pass
	def keys(self):
		'''
		'''
		return list(self)
	def values(self):
		'''
		'''
		return list(self.itervalues())
	def items(self):
		'''
		'''
		return list(self.iteritems())
	def iterkeys(self):
		'''
		'''
		return self.__iter__()
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
	def get(self, name, dfl=None):
		'''
		'''
		try:
			return self[name]
		except KeyError:
			if dfl == None:
				raise
			return dfl
	def has_key(self, name):
		'''
		'''
		return name in self
##	def setdefault(self):
##		'''
##		'''
##		pass
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
		return dict(*self.items())


#-------------------------------------------------------DictTypeUnion---
# WARNING: this is not done!
class DictTypeUnion(DictUnion, dict):
	'''
	this is a diriviation from dict that can contain oun data.
	'''
	##!!!
	pass


#-----------------------------------------------------------ListUnion---
##def ListUnion(list):
##	'''
##	'''
##	pass


#-------------------------------------------------------DictIntersect---
##class DictIntersect(object):
##	'''
##	'''
##	pass



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
