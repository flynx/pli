#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20040909160930'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

from sets import Set

import pli.dispatch as dispatch
import pli.pattern.mixin.mapping as mapping
import pli.interface as interface



#-----------------------------------------------------------------------
#------------------------------------------------BasicMappingDispatch---
# this is a mapping mixin....
class BasicMappingDispatch(BasicDispatch, mapping.BasicMapping):
	'''
	this is a mapping dispatch object.

	this provides the capability to store objects in different mappings...
	'''
	# this is a dict with keys as markers and values are arbitery
	# mappings... 
	__targets__ = None

	# basic mapping methods...
	def __getitem__(self, name):
		'''
		'''
		for v in self.__targets__.itervalues():
			if name in v:
				return v[name]
		raise KeyError, name
	def __setitem__(self, name, value):
		'''
		'''
		self.reslove(valuse)[name] = value
	def __delitem__(self, name):
		'''
		'''
		for v in self.__targets__.itervalues():
			if name in v:
				del v[name]
	def __iter__(self):
		'''
		'''
		for v in self.__targets__.itervalues():
			for k in v:
				yield k
	# consistensy protocol...
	def __isconsistent__(self):
		'''
		'''
		# check if we have intersecting targets...
		res = []
		[ res.append(t.keys()) for k in self.__targets__.itervalues() ]
		return len(res) == len(Set(res))
	# dispatch method...
	def resolve(self, obj):
		'''
		return the apropriate target for the given object.
		'''
		raise NotImplementedError, 'the resolve method must be implemented.'


#---------------------------------------BasicMappingInterfaceDispatch---
class BasicMappingInterfaceDispatch(BasicMappingDispatch):
	'''
	'''
	def resolve(self, obj):
		'''
		'''
		return super(BasicMappingDispatch, self).resolve(interface.getinterfaces(obj))



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
