#=======================================================================

__version__ = '''0.1.47'''
__sub_version__ = '''20040323153531'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

from __future__ import generators
import types

import pli.functional as func 
from pli.functional import curry
##!!! this might change in the future...
import pli.objutils as objutils

import selector
import store
import stored
import storeclient

##import acl



#-----------------------------------------------------------------------
#-----------------------------------------------------------isinstore---
def isinstore(store):
	'''
	this function will return a predicate that will check if an object
	exists in a given store (to be used mainly for auto type checking).
	'''
	return lambda oid: oid in store


#---------------------------------------------------------r_isinstore---
def r_isinstore(store, excep=None, msg=None):
	'''
	this will cunstruct a test function that will test if an object exists
	in a given store or raise an exception.
	'''
	name = hasattr(store, '__name__') and store.__name__ or store.__class__.__name__
	return func.raise_on_false(isinstore(store), 'r_isin' + name,\
								excep != None and NameError \
											or excep, \
								msg != None and ('object not found in store %s.' % store) \
											or msg)


#----------------------------------------------isinstore_and_isoftype---
def isinstore_and_isoftype(store):
	'''
	this will generate a function (takes store as argument) that will in turn
	construct a function (takes object type as argument) that will test if 
	obj (key) is in store and is (value) of a given type...


	NOTE: sorry, but this might not be the most obvios of functions (atleast 
	      at the first sight!) :)
	'''
	return lambda otype: \
				lambda obj: isinstore(store)(obj) and type(store[obj]) == otype



#-----------------------------------------------------------------------
# TODO rework this into mixins....
#------------------------------------------StaticStoreClientWithOwner---
SHOW_ALL = 1
class OwnedStaticStoreClient(storeclient.StaticStoreClient):
	'''
	'''

	__ignore_nonexistant_filter_attrs__ = True

	def __init__(self, owner, flags=0):
		'''
		'''
		self._store_flags = flags
		self.__owner__ = owner
		store.StaticStoreClient.__init__(self, filters={'__owner__':owner})
	def __getattr__(self, name):
		'''
		'''
		# deligate the call to the original store object
		# constructors...
		##!! revise !!##
		cls = store.StaticStoreClient.__getattr__(self, name)
		if issubclass(cls, OwnedStoredObjectWithAttrs):
			return curry(cls, owner=self.__owner__)	
		return cls
	def isaccessible(self, key):
		'''
		'''
		obj = self._store_data[key]
##		obj = self[key]
		if self._store_flags & SHOW_ALL:
			return True
##		if hasattr(obj, '__store_public__') and obj.__store_public__:
##			return True
		##!!! is this needed...
		if not hasattr(self, '__owner__') or self.__owner__ in ('', None):
			return True
		# this might be a litle slower, but it is more flexible...
		return super(OwnedStaticStoreClient, self).isaccessible(key)
##		res = []
##		for attr, val in self._store_filters.items():
##			try:
##				res += [getattr(obj, attr) == val]
##			except AttributeError:
##				pass
##		if False not in res:
##			return True
##		return False
			


#-----------------------------------------------------------------------
#-----------------------------------------------StoredObjectWithAttrs---
class StoredObjectWithAttrs(objutils.ObjectWithAttrs, stored.StoredObject):
	'''
	a generic stored object class with attribute creation an update automation.

	this class checks attribute format.
	'''
##	__acl__ = acl
	# this will restrict the attribute that can be created for this
	# object to the ones mentioned in the list (DO NOT SET HERE!).
##	__attr_format__ = ()
	# this defines a list of attributes that must be defined on object
	# init.
##	__essential_attrs__ = ()
	# this defines the callbacks for attr update... (RPC only at the
	# moment...)
##	__attr_update_callbacks__ = {}
	# this will enable attribute type checking...
	__check_attr_types__ = True
	# this defines the values to be considered as no-vals...
	__none_values__ = ('', 'None', None)

	##!! temporary...
	__readonly_attrs__ = ()

	##!! temporary -- this is a fix to allow zodbs special attrs... !!##
	def __setattr__(self, name, val):
		'''
		'''
		return object.__setattr__(self, name, val)


#------------------------------------------OwnedStoredObjectWithAttrs---
class OwnedStoredObjectWithAttrs(StoredObjectWithAttrs):
	'''
	'''
	__store_public__ = False

	def __init__(self, name, attrs={}, owner=''):
		'''
		'''
		super(OwnedStoredObjectWithAttrs, self).__init__(name, attrs)
		if not hasattr(self, '__owner__'):
			self.__owner__ = owner



#-----------------------------------------------------------------------
#-----------------------------------------------------------TreeStore---
class TreeStore(store.BaseStore):
	'''
	'''
	def __delitem__(self, key):
		'''
		'''
		obj = self[key]
		if hasattr(obj, 'children') and len(obj.children) != 0:
			raise TypeError, 'can\'t remove, not empty object "%s"' % key
		if obj.parent != None:
			self[obj.parent].children.remove(key)
		super(TreeStore, self).__delitem__(key)
	# TODO make this non-recursive...
	def get_tree_dict(self, node_id=None):
		'''
		this will return a nested dict of the form:
			{<node_id>: <children>[, ...]}
			where <children> is a dict of the same format.
		'''
		if node_id != None:
			if node_id not in self:
				raise KeyError, 'object "%s" is not in store "%s".' % (node_id, self.__name__)
			root = node_id
		else:
			root = 'root'
		root_obj = self[root]
		# recursive...
		return dict([(n, self.get_tree_dict(n)) for n in (hasattr(root_obj, 'children') and root_obj.children or [])])
	def get_tree(self, node_id=None):
		'''
		this will return a nested tuple of the form:
			((<node_id>, <children>)[, ...])
			where <children> is a dict of the same format.
		'''
		if node_id != None:
			if node_id not in self:
				raise KeyError, 'object "%s" is not in store "%s".' % (node_id, self.__name__)
			root = node_id
		else:
			root = 'root'
		root_obj = self[root]
		# recursive...
		return [[n, self.get_tree(n)] for n in (hasattr(root_obj, 'children') and root_obj.children or ())]


#------------------------------------------------------------TreeNode---
# Q: is it posible to make this store.StoredObject subclass???
class TreeNode(StoredObjectWithAttrs):
	'''
	'''
	__store__ = None
	# this will automatcly register the class as a store type...
	__auto_register_type__ = False

	__essential_attrs__ = (
							'parent',			# str (parent folder id)
						  )
##	__attr_format__ = __essential_attrs__ + \
##						  (
##						  )

	__readonly_attrs__ = StoredObjectWithAttrs.__readonly_attrs__ + \
						  (
							'children',
						  )

	def __init__(self, *p, **n):
		'''
		'''
		super(TreeNode, self).__init__(*p, **n)
		# check parent...
##		if self.parent not in ('None', None):
##			if self.parent not in self.__store__:
##				raise TypeError, 'can\'t attach to a non-existant object "%s".' % self.parent
		self.children = []
		self.__readonly_attrs__ = self.__readonly_attrs__ + ('parent',)
	def update(self, data):
		'''
		'''
		if 'parent' in data:
			parent = data['parent']
			del data['parent']
			if parent not in ('None', None):
				if parent not in self.__store__:
					raise TypeError, 'can\'t attach to a non-existant object "%s".' % parent
				if hasattr(self, 'parent'):
					# detach from old parent... (on move)
					self.__store__[self.parent].children.remove(self.__name__)
				self.parent = parent
				res = super(TreeNode, self).update(data)
				# atach to new parent...
				self.__store__[parent].children += [self.__name__]
				return res
			else:
				self.parent = parent
		return super(TreeNode, self).update(data)



###-----------------------------------------------------------------------
##class CallproxyWrapper(object):
##	'''
##	'''
##	__proxy__ = None
##
##	def __getattr__(self, name):
##		'''
##		'''
##		return self.__proxy__(super(Wrapper, self).__getattr__(name))
##
##
##class CallproxyWrapperStore(store.BaseStore):
##	'''
##	'''
##
##	__wrapper__ = Wrapper
##
##	def __getitem__(self, name):
##		'''
##		'''
##		return super(CallproxyWrapperStore, self).__getitem__(name)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
