#=======================================================================

__version__ = '''0.0.11'''
__sub_version__ = '''20040313225846'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

##from store import *


#-----------------------------------------------------------------------
#--------------------------------------------------------_StoredClass---
class _StoredClass(type):
	'''
	'''
	# this will define the name of the attribute to define the class
	# store...
	__class_store_attr_name__ = '__store__'
	# if this is set the type will auto register on class creation.
	# NOTE: this is inherited.
	__auto_register_type__ = True
	# if this is True the *current class* will not be registred in
	# store.
	# NOTE: this is not inherited.
	__ignore_registration__ = False

	def __init__(cls, name, bases, ns):
		'''
		this will add the object type to the store.
		'''
		super(_StoredClass, cls).__init__(name, bases, ns)
		store_attr_name = cls.__class_store_attr_name__
##		if '__auto_register_type__' in ns and ns['__auto_register_type__']:
		if ('__ignore_registration__' not in ns or not ns['__ignore_registration__']) and \
				hasattr(cls, '__auto_register_type__') and cls.__auto_register_type__:
			if not hasattr(cls, store_attr_name) or getattr(cls, store_attr_name) == None:
				# might be good to do this in __init__ ... (?)
				raise TypeError, 'a store object must be defined for type "%s" for auto registration.' % cls.__name__
			cls.storeclass(name, cls)
	def storeclass(cls, name, obj):
		'''
		this will store the object.
		'''
##		# set name information...
##		obj.__name__ = name
##		# set type information...
##		if not hasattr(obj, '__type_name__'):
##			obj.__type_name__ = obj.__class__.__name__
		# store the object...
		getattr(cls, cls.__class_store_attr_name__)[name] = obj


#-------------------------------------------------------_StoredObject---
class _StoredObject(_StoredClass):
	'''
	'''
	# this will define the name of the attribute to define the object
	# store...
	__object_store_attr_name__ = '__store__'
	# if this is set the type will auto register on class creation.
	__auto_register_type__ = False
	# this if set must define a name generator function.
	__auto_name__ = False

	def __call__(cls, *p, **n):
		'''
		'''
		store_attr_name = cls.__object_store_attr_name__
		# create an object...
		obj = cls.__new__(cls, *p, **n)
		# init the object...
		obj.__init__(*p, **n)
		# check if a store is defined...
		if not hasattr(cls, store_attr_name) or getattr(cls,store_attr_name) == None:
			raise TypeError, 'a store object must be defined for type "%s".' % cls.__name__
		store = getattr(cls, cls.__object_store_attr_name__)
		# check if object is in store... (this should be done as soon
		# as posible!)
		if hasattr(store, '__strictnames__') and store.__strictnames__ and p[0] in store:
			raise TypeError, 'an object with the id "%s" already exists.' % p[0]
##		# create an object...
##		obj = cls.__new__(cls, *p, **n)
		# create/get an object name...
		if hasattr(obj, '__auto_name__') and obj.__auto_name__ != False:
			auto_name = obj.__auto_name__
			if callable(auto_name):
				# NOTE: the __auto_name__ method must match the
				#       signiture of __init__
				name = auto_name(*p, **n)
			elif type(auto_name) is str:
				name = auto_name % time.time()
			else:
				raise TypeError, 'incompatible type of cls.__auto_name__.'
		else:
			name = p[0]
##		# init the object...
##		obj.__init__(*p, **n)
		# register object in store....
		##!!! REVIZE !!!##
		cls.storeobject(name, obj)
		return obj
	##!!! REVIZE !!!##
	def storeobject(cls, name, obj):
		'''
		this will store the object.
		'''
##		# set name information...
##		obj.__name__ = name
##		# set type information...
##		if not hasattr(obj, '__type_name__'):
##			obj.__type_name__ = obj.__class__.__name__
		# store the object...
		getattr(cls, cls.__object_store_attr_name__)[name] = obj


#--------------------------------------------------------StoredObject---
# TODO add onStoredObjectLoad, onStoredObjectSave, 
#      onStoredObjectReload, .... events...
#
class StoredObject(object):
	'''
	'''
	__metaclass__ = _StoredObject
	def __init__(self, name):
		pass



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
