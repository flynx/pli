#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20080128014715'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import new

import pli.pattern.mixin.mapping as mapping
import pli.pattern.proxy.utils as proxyutils
import pli.logictypes as logictypes
import pli.objutils as objutils


#-----------------------------------------------------------------------
#--------------------------------------------Mapping2AttrMinimalMixin---
class Mapping2AttrMinimalMixin(mapping.Mapping):
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


#---------------------------------------------------Mapping2AttrMixin---
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


#---------------------------------------------------Attr2MappingMixin---
# XXX this is a workaround pythons "bug" with __dict__ using the
#     C API only instead of the py dict interface and then C...
class Attr2MappingMixin(mapping.BasicMapping):
	'''
	a mixin adepter form the attr protocol to the mapping protocol.

	attributes listed in .__attr2mapping_ignore_attrs__ will be accessed
	using the attribute protocol.

	NOTE: this will call the object itself (not a proxy to an attr).
	'''
	# attrs that will always be accessed in the __dict__
	__attr2mapping_ignore_attrs__ = ()

	def __getattr__(self, name):
		'''
		'''
		try:
			if name not in self.__attr2mapping_ignore_attrs__:
				return self[name]
		except KeyError:
			pass
		# call the next get...
		try:
			return super(Attr2MappingMixin, self).__getattr__(name)	
		except KeyError:
			raise AttributeError, name
	def __setattr__(self, name, value):
		'''
		'''
		if name not in self.__attr2mapping_ignore_attrs__:
			self[name] = value
		else:
			super(Attr2MappingMixin, self).__setattr__(name, value)	
	def __delattr__(self, name):
		'''
		'''
		try:
			if name not in self.__attr2mapping_ignore_attrs__:
				del self[name]
				return
		except KeyError:
			pass
		# call the next del...
		try:
			del super(Attr2MappingMixin, self)[name]
		except KeyError:
			raise AttributeError, name



#-----------------------------------------------------------------------
#----------------------------------------ConstructorRegistrationMixin---
# XXX this is mot mapping specific... move someplace more logical...
# XXX might be a good idea to uncouple this from DictChain...
# XXX also, might be good to make chaining customizable...
# XXX this is generic.... might be a good idea to remove the
#     "constructor" suffix...
#     ...this change will need name modification policy so as to be
#     able to use this in several contexts...
class ConstructorRegistrationMixin(object):
	'''
	defines constructor registration mechanics.

	NOTE: this will populates .__constructor_store__ in it's class or object 
	      namespace (no other work needed).
	NOTE: .__constructor_wrapper__ need to be overloaded.
	'''
	# mapping containing consturctos...
	# a constructor may take any arguments and must return the
	# constructed object...
	# NOTE: DictChain object will be used as a container here.
	# XXX make this costomizable... (???)
	__constructor_store__ = None
	# callable. wrap or prepare the constructor.
	# this' return will be stored as the constructor in .__constructor_store__
	# NOTE: this is a good place to take care of object storing.
	# NOTE: if this is None, no wrapper will be used and the
	#       constructor will be stored as-is.
	# NOTE: what arguments the constructor will be passed depends on
	#       how it will be called... (what args it expects depends on
	#       how it is wrapped)
	__constructor_wrapper__ = None

	@objutils.classinstancemethod
	def regconstructor(self, name, constructor, *p, **n):
		'''
		'''
		if self.__constructor_store__ == None:
			# XXX might be good to make chaining optional...
			self.__constructor_store__ = logictypes.DictChain()
		# XXX vars might not work in all cases (when the ns interface is
		#     redefined)...
		elif '__constructor_store__' not in vars(self):
			p = self.__constructor_store__
			# XXX might be good to make chaining optional...
			c = self.__constructor_store__ = logictypes.DictChain()
			c.chain_next = p
		if self.__constructor_wrapper__ != None:
			self.__constructor_store__[name] = self.__constructor_wrapper__(constructor)
		else:
			self.__constructor_store__[name] = constructor
	@objutils.classinstancemethod
	def unregconstructor(self, name):
		'''

		NOTE: this will only remove the local constructor.
		'''
		if '__constructor_store__' in vars(self):
			# NOTE: this is a dict chain object...
			del self.__constructor_store__[name] 
		else:
			if name in self.__constructor_store__:
				raise KeyError, '"%s" (constructor not local)' % name
			raise KeyError, name
##	@objutils.classinstancemethod
##	def listconstructors(self):
##		'''
##		'''
##		return self.__constructor_store__ 


#-------------------------------AttrConstructorAccessWithSelfArgMixin---
# XXX this is mot mapping specific... move someplace more logical...
# XXX this is generic.... might be a good idea to remove the
#     "constructor" suffix...
# XXX do we need a version without self passing??
class AttrConstructorAccessWithSelfArgMixin(object):
	'''
	provides access to registred constructors via an attribute interface.

	NOTE: this needs a populated .__constructor_store__ in it's namespace.
	NOTE: when the constructor is called it will be passed self as the first
	      argument.
	'''
	__constructor_store__ = None

	def __getattr__(self, name):
		'''
		'''
		if name in self.__constructor_store__:
			# curry self into the constructor... 
			return new.instancemethod(self.__constructor_store__[name], self, self.__class__)
		# XXX do we need a try block here??? (may block some errors)
		try:
			return super(AttrConstructorAccessWithSelfArgMixin, self).__getattr__(name)
		except AttributeError:
			raise AttributeError, name


#-------------------------------------MappingWithItemConstructorMixin---
# TODO make a version/mixin where constructors are searched in
#      parents...
# XXX might be a good idea to seporate the store and the constructor
#     interfaces...
#     also, may be good to make this more generic (not just a mapping)
class MappingWithItemConstructorMixin(
						ConstructorRegistrationMixin,
						AttrConstructorAccessWithSelfArgMixin, 
						mapping.BasicMapping):
	'''
	provide a constructor interface.

	a constructor will create objects that will be stored in the mapping.

	the constructors are accessed by name as attributes/methods.

	input constructor signature:
		<cunstructor>(<args>) -> <obj>

	constructor signature when accessed form the mapping:
		<mapping>.<name>(<key>, <args>) -> <obj>


	NOTE: this provides class and instance constructors, each edited from
	      its' context only (class constructors form the class and the 
		  instance constructors from the instance).
	NOTE: instance constructors overshadow the class constructors.
	NOTE: this needs actual mapping mechanics...
	      (see: pli.pattern.mixin.mapping.Mapping)


	minimal example:

		class Mapping(MappingWithItemConstructorMixin, dict):
			pass

		# register class constructor (accessible from any instance)...
		Mapping.regconstructor('string', str)

		m = Mapping()

		# register instance constructor (access only via the
		# instance)...
		m.regconstructor('integer', int)

		# usage...
		m.string('a', 123)
		m.integer('b', 321)

		print m			# -> {'a': '123', 'b', 321}

	'''
	# XXX might be a good idea to warn if the constructed key overlaps
	#     with a constructor name...
	@staticmethod
	def __constructor_wrapper__(constructor):
		'''
		wrapper that will save the constructor return to self as an item.

		NOTE: this adds a key argument to the constructor method, used as 
		      key to store the result.
		'''
		def _construct(self, name, *p, **n):
			val = constructor(*p, **n)
			self[name] = val
			return val
		return _construct
	


#-----------------------------------------------------------------------
# XXX still thinking about these...
#----------------------------------MappingWithKeyTypeRestrictoinMixin---
class MappingWithKeyTypeRestrictoinMixin(mapping.BasicMapping):
	'''
	'''
	def __check_mapping_key_type__(self, key):
		'''
		'''
		raise NotImplementedError

	def __setitem__(self, name, value):
		'''
		'''
		self.__check_mapping_key_type__(value)
		super(MappingWithValueTypeRestrictoin, self).__setitem__(name, value)


#--------------------------------MappingWithValueTypeRestrictoinMixin---
class MappingWithValueTypeRestrictoinMixin(mapping.BasicMapping):
	'''
	'''
	def __check_mapping_value_type__(self, value):
		'''
		'''
		raise NotImplementedError

	def __setitem__(self, name, value):
		'''
		'''
		self.__check_mapping_value_type__(value)
		super(MappingWithValueTypeRestrictoin, self).__setitem__(name, value)



#-----------------------------------------------------------------------
if __name__ == '__main__':

##	class C(MappingWithItemConstructorMixin, dict):
	class C(Attr2MappingMixin, MappingWithItemConstructorMixin, dict):
		'''
		'''
		__attr2mapping_ignore_attrs__ = (
				'__constructor_store__',
				)

	C.regconstructor('str', str)
	C.regconstructor('set', set)
	C.regconstructor('C', C)

	c = C()

	c.str('a', 124)
	c.set('b', '124')

	c.regconstructor('int', int)

	c.str('c', 321)
	c.int('d', 124)

	print c

	c.C('c')

	c.c.str('a', 124)
##	c.c.int('d', 124)

	print c.c

	print c.c.a
	print c
	del c.c.a
	print c.c
	print c




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
