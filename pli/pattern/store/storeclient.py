#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20040803232005'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import store


#-----------------------------------------------------------------------
##!!! revise !!!##
#---------------------------------------------------------StoreClient---
class GenericStaticStoreClient(store.BaseStore):
	'''
	'''
	__source_store__ = None

	def __init__(self, filters=()):
		'''
		'''
		if self.__source_store__ == None:
			raise TypeError, 'no store defined.'
		super(GenericStaticStoreClient, self).__init__(None)
		self._store_data = self.__source_store__
		self._store_types = self.__source_store__._store_types
		self._store_filters = filters
	def __getattr__(self, name):
		'''
		'''
		# deligate the call to the original store object
		# constructors...
		store = self.__source_store__
		if not hasattr(store, name):
			raise AttributeError, '%s has no attribute "%s"' % (self, name)
		if name in store._store_types:
			return getattr(store, name)
		raise AttributeError, ''
	def isaccessible(self, key):
		'''
		'''
		obj = self._store_data[key]
		if hasattr(obj, '__store_public__') and obj.__store_public__ or\
				None not in [f(obj) for f in self._store_filters]:
			return True
		return False
	def __getitem__(self, key):
		'''
		'''
		if self.isaccessible(key):
			return self._store_data[key]
	def __setitem__(self, key, obj):
		'''
		'''
		if key in self._store_data and not self.isaccessible(key):
			raise KeyError, 'can\'t set the "%s" item.' % key
##		BaseStore.__setitem__(self, key, obj)
		super(GenericStaticStoreClient, self).__setitem__(key, obj)
	def __delitem__(self, key):
		'''
		'''
		if key in self._store_data and not self.isaccessible(key):
			raise KeyError, 'can\'t remove the "%s" item.' % key
##		BaseStore.__delitem__(self, key)
		super(GenericStaticStoreClient, self).__delitem__(key)
	def __iter__(self):
		'''
		'''
		for n in self._store_data:
			if self.isaccessible(n):
				yield n
	def iterkeys(self):
		'''
		'''
##		print '>>>', self._store_data.__getitem__('ttt')
##		print '!!!', self._store_data, id(self._store_data)
		for e in self._store_data.iterkeys():
			if self.isaccessible(e):
				yield e
	def itervalues(self):
		'''
		'''
		for e in self._store_data.iterkeys():
			if self.isaccessible(e):
				yield self._store_data[e]
	def iteritems(self):
		'''
		'''
		for n, o in self._store_data.iteritems():
			if self.isaccessible(n):
				yield n, o
	def keys(self):
		'''
		'''
		return list(self.iterkeys())
	def values(self):
		'''
		'''
		return list(self.itervalues())
	def get_object_data(self, key, *attrs):
		'''
		'''
		if not self.isaccessible(key):
			raise KeyError, key
		return super(GenericStaticStoreClient, self).get_object_data(self, key, *attrs)


#---------------------------------------------------StaticStoreClient---
# TODO move this into storeutils... (??)
class StaticStoreClient(GenericStaticStoreClient):
	'''
	'''

	__ignore_nonexistant_filter_attrs__ = False

	def __init__(self, filters={}):
		'''
		'''
		super(StaticStoreClient, self).__init__(filters)
	def isaccessible(self, key):
		'''
		'''
		obj = self._store_data[key]
##		obj = self[key]
		if hasattr(self, '__ignore_nonexistant_filter_attrs__') \
				and	self.__ignore_nonexistant_filter_attrs__:
			res = []
			for attr, val in self._store_filters.items():
				try:
					res += [getattr(obj, attr) == val]
				except AttributeError:
					pass
			if False not in res:
				return True
		else:
			if hasattr(obj, '__store_public__') and obj.__store_public__ or\
					False not in [getattr(obj, attr) == val for attr, val in self._store_filters.items()]:
				return True
		return False


#----------------------------------------StaticStoreClientConstructor---
class StaticStoreClientConstructor(StaticStoreClient):
	'''
	'''
	def __init__(self, source_store=None, filters={}):
		'''
		'''
		self.__source_store__ = source_store
		super(StaticStoreClientConstructor, self).__init__(filters)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
