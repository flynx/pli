#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20080127060119'''
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
#     C API instead of the py dict interface...
class Attr2MappingMixin(mapping.BasicMapping):
	'''
	'''
	# attrs that will always be accessed in the __dict__
	__attr2map_ignore_attrs__ = ()

	def __getattr__(self, name):
		'''
		'''
		try:
			if name not in self.__attr2map_ignore_attrs__:
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
		if name not in self.__attr2map_ignore_attrs__:
			self[name] = value
		else:
			super(Attr2MappingMixin, self).__setattr__(name, value)	
	def __delattr__(self, name):
		'''
		'''
		try:
			if name not in self.__attr2map_ignore_attrs__:
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
#-------------------------------------MappingWithItemConstructorMixin---
# TODO make a version/mixin where constructors are searched in
#      parents...
class MappingWithItemConstructorMixin(mapping.BasicMapping):
	'''
	'''
	# mapping containing item consturctos...
	# a constructor may take any arguments and must return the
	# constructed object...
	# NOTE: when the constructor is called form the object it must take
	#       the key for the object as the fist argument folowed bu
	#       normal constructor args...
	__item_constructors__ = None

	def __getattr__(self, name):
		'''
		'''
		if name in self.__item_constructors__:
			return new.instancemethod(self.__item_constructors__[name], self, self.__class__)
		# XXX do we need a try block here??? (may block some errors)
		try:
			return super(MappingWithItemConstructorMixin, self).__getattr__(name)
		except AttributeError:
			raise AttributeError, name
	
	# XXX this might not be pickle safe...
	@objutils.classinstancemethod
	def regconstructor(self, name, constructor):
		'''
		'''
		if self.__item_constructors__ == None:
			self.__item_constructors__ = logictypes.DictChain()
		# XXX vars might not work in all cases (when the ns interface is
		#     redefined)...
		elif '__item_constructors__' not in vars(self):
			p = self.__item_constructors__
			c = self.__item_constructors__ = logictypes.DictChain()
			c.chain_next = p
		# XXX is this approach pickle-safe???
		def prepare(constructor):
			def _construct(self, name, *p, **n):
				val = constructor(*p, **n)
				self[name] = val
				return val
			return _construct
		self.__item_constructors__[name] = prepare(constructor)



#-----------------------------------------------------------------------
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
		__attr2map_ignore_attrs__ = (
				'__item_constructors__',
				)

	C.regconstructor('str', str)
	C.regconstructor('set', set)

	c = C()

	c.str('a', 124)
	c.set('b', '124')

	c.regconstructor('int', int)

	c.str('c', 321)
	c.int('d', 124)

	print c

	cc = C()

	cc.str('a', 124)
##	cc.int('d', 124)

	print cc

	print cc.a
	del cc.a
	print cc




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
