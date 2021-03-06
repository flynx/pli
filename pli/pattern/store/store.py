#=======================================================================

__version__ = '''0.0.49'''
__sub_version__ = '''20050112055753'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import time
import re
import weakref

import pli.pattern.mixin.mapping as mapping


#-----------------------------------------------------------------------
#---------------------------------------------------isstorecompatible---
def isstorecompatible(obj):
	'''
	this will test general store interface compatibility...
	'''
	return issubclass(type(obj), BaseStore) or type(obj) == type({})


#--------------------------------------------------------isstoredtype---
def isstoredtype(store, name):
	'''
	this will return True if the name is a stored type is store.
	'''
	return name in store._store_types



#-----------------------------------------------------------------------
#-----------------------------------------------------------BaseStore---
# TODO add onStoreLoad, onStoreSave and onStoreReload events!!
#      the handlers of these will accept the store instance as an
#      argument...
# TODO rename to MappingBaseStore...
#
class BaseStore(mapping.Mapping, mapping.BasicMappingProxy):
##class BaseStore(mapping.MappingWithMethods, mapping.BasicMappingProxy):
	'''
	'''
	# if this is true strict object type checking will be enabled...
	__stricttypes__ = False
	# if this is true there will be no abbility to "recreate" an object
	# using the add_object method.
	__strictnames__ = True
	# this will define the format used to generate a type attribute
	# name... (attrname = __typenameformat___ % <type>.__name__)
	__typenameformat___ = '%s'

	__source_attr__ = '_store_data'

	def __init__(self, name, *p, **n):
		'''
		'''
		self.__name__ = name
		self._store_types = {}
		self._store_data = {}
##		super(BaseStore, self).__init__(name)
	# dict minimal methods:
##	def __getitem__(self, key):
##		'''
##		'''
##		return self._store_data[key]
	def __setitem__(self, key, obj):
		'''
		'''
		if type(obj).__name__ not in self._store_types:
			if not self.__stricttypes__:
				# add objects' type...
				self.add_object_type(type(obj))
			else:
				raise TypeError, 'can\'t add object "' + str(obj) + '" to store "' + str(self) + '": unregistred type.'
		# add the object
		if self.__strictnames__ and key in self._store_data:
			raise TypeError, 'an object with the id "%s" already exists.' % key
##		self._store_data[key] = obj
		super(BaseStore, self).__setitem__(key, obj)
##	def __delitem__(self, key):
##		'''
##		'''
##		del self._store_data[key]
##	def __iter__(self):
##		'''
##		'''
##		return self._store_data.__iter__()
	# dict secondary methods:
	# NOTE: might be good to un comment these...
##	def __contains__(self, key):
##		'''
##		'''
##		return key in self._store_data
##	def iterkeys(self):
##		'''
##		'''
##		return self._store_data.iterkeys()
##	def itervalues(self):
##		'''
##		'''
##		return self._store_data.itervalues()
##	def iteritems(self):
##		'''
##		'''
##		return self._store_data.iteritems()
##	def keys(self):
##		'''
##		'''
##		return self._store_data.keys()
##	def values(self):
##		'''
##		'''
##		return self._store_data.values()
	# BaseStore specific methods...
	def add_object_type(self, otype):
		'''
		'''
		self._store_types[self.__typenameformat___ % otype.__name__] = otype
	##!!! REMOVE THIS !!!##
	def get_types(self):
		'''
		'''
		print '''WARNING: the pli.pattern.store.BaseStore.get_types method will be shortly removed!
		 use the itertypenames, itertypes methods instead!'''
		return self._store_types.keys()

	def gettypenames(self):
		'''
		this will return a list of type names supported by the store.
		'''
		return self._store_types.keys()
	def gettypes(self):
		'''
		this will return the types supported by the store.
		'''
		return self._store_types.values()
	def itertypenames(self):
		'''
		this will iterate through the type names supported by the store.
		'''
		for n in self._store_types.iterkeys():
			yield n
	def itertypes(self):
		'''
		this will iterate through the types supported by the store.
		'''
		for n in self._store_types.itervalues():
			yield n



#-----------------------------------------------------------------------
# Store mix-ins...
#--------------------------------------------------------WeakrefStore---
class WeakrefStore(BaseStore):
	'''
	'''
	def __init__(self, name, *p, **n):
		'''
		'''
		super(WeakrefStore, self).__init__(name, *p, **n)
		self._store_data = weakref.WeakValueDictionary()


#---------------------------------------------------AttrTypeBaseStore---
class AttrTypeBaseStore(BaseStore):
	'''
	mix-in/class. this provides access to stored object types through atributes.
	'''
	# this if set will check the attr name compliance with the python
	# variable name syntax...
	__check_type_name_format__ = True
##	__check_type_name_format__ = False
	# this will define a pattern against which the attribute name is to
	# be checked...
	__type_name_format__ = re.compile('[_a-zA-Z][_a-zA-Z\d]*$')

	# NOTE: if this is both an AttributeBaseStore and na
	#       AttrTypeBaseStore the name will get checked twice, and I
	#       see no beautifull way out of this....
##	def __setitem__(self, key, value):
##		'''
##		'''
##		if hasattr(self, '__check_type_name_format__') and self.__check_type_name_format__ and \
##				re.match(self.__type_name_format__, key) is None:
##			raise NameError, 'stored objects name must comply with python variable naming rules (got: "%s").' % key
##		super(AttrTypeBaseStore, self).__setitem__(key, value)
	def __getattr__(self, name):
		'''
		'''
		if name in ('_store_types',):
			return object.__getattribute__(self, '_store_types')
		if name in self._store_types:
			return self._store_types[name]
		try:
			return super(AttrTypeBaseStore, self).__getattr__(name)
		except AttributeError:
			# XXX is this correct....
			raise AttributeError, 'object "%s" has no attribute "%s"' % (self, name)
	def add_object_type(self, otype):
		'''
		'''
		name = self.__typenameformat___ % otype.__name__
		if hasattr(self, '__check_type_name_format__') and self.__check_type_name_format__ and \
				re.match(self.__type_name_format__, name) is None:
			raise NameError, 'stored objects name must comply with python variable naming rules (got: "%s").' % name
		super(AttrTypeBaseStore, self).add_object_type(otype)


#--------------------------------------------------------RPCBaseStore---
# this is here for the RPC interface...
class RPCBaseStore(BaseStore):
	'''
	mix-in/class. this provides rpc methods for stored object data access.
	'''
	def get_object_data(self, key, *attrs):
		'''
		'''
		obj = self[key]
		res = {}
		for attr in attrs:
			try:
				##!!! do type checking....
				res[attr] = getattr(obj, attr)
			except:
				# this might not be good for a generic version...
				res[attr] = ''
		return res
	def add_object(self, key, obj):
		'''
		this will add an object to store...
		'''
		self.__setitem__(key, obj)
	def update_object(self, key, data):
		'''
		this will update a set of attributes of an object.
		'''
		if hasattr(self[key], 'update'):
			##!!! check...
			return self[key].update(data)
		else:
			obj = self[key]
			for attr in data:
				return setattr(obj, attr, data[attr])
	def remove_object(self, key):
		'''
		'''
		self.__delitem__(key)


#---------------------------------------------------GroupingBaseStore---
class GroupingBaseStore(BaseStore):
	'''
	mix-in/class. this provides grouping behavior for stored objects...
	'''
	def __init__(self):
		'''
		'''
		raise NotImplementedError, 'not yet done...'


#--------------------------------------------------AttributeBaseStore---
class AttributeBaseStore(BaseStore):
	'''
	mix-in/class. this provides access to stored objects through store attributes.
	'''
	# this if set will check the attr name compliance with the python
	# variable name syntax...
	__check_key_format__ = True
	# this will define a pattern against which the attribute name is to
	# be checked...
	__key_format__ = re.compile('[_a-zA-Z][_a-zA-Z\d]*$')

	# NOTE: if this is both an AttributeBaseStore and na
	#       AttrTypeBaseStore the name will get checked twice, and I
	#       see no beautifull way out of this....
	def __setitem__(self, key, value):
		'''
		'''
		if hasattr(self, '__check_key_format__') and self.__check_key_format__ and \
				re.match(self.__key_format__, key) is None:
			raise NameError, 'stored objects name must comply with python variable naming rules (got: "%s").' % key
		super(AttributeBaseStore, self).__setitem__(key, value)
	def __getattr__(self, name):
		'''
		'''
		try:
			return super(AttributeBaseStore, self).__getattr__(name)
		except:
			return self[name]


#--------------------------------------------------------WrapperStore---
class WrapperBaseStore(BaseStore):
	'''
	mix-in/class. this provides access to wrapped/proxied stored objects.
	'''
	# this will define a wrapper object (
	# format: 
	# 	<wrapper>(<obj>) -> <wrapped>
	__wrapper__ = None

	def __getitem__(self, key):
		'''
		'''
		return self.__wrapper__(super(WrapperStore, self).__getitem__(key))
	def itervalues(self):
		'''
		'''
		for val in super(WrapperStore, self).itervalues():
			yield self.__wrapper__(val)
	def iteritems(self):
		'''
		'''
		for key, val in super(WrapperStore, self).iteritems():
			yield key, self.__wrapper__(val)
	def values(self):
		'''
		'''
		return [ self.__wrapper__(val) for val in super(WrapperStore, self).values() ]


#-----------------------------------------------AttributeWrapperStore---
class AttributeWrapperStore(AttributeBaseStore, WrapperBaseStore):
	'''
	mix-in/class. this provides access to wrapped/proxied stored objects through store attributes.
	'''



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
