#=======================================================================

__version__ = '''0.1.08'''
__sub_version__ = '''20050111050358'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

__doc__ = '''\
this module will define a set of utilities and classes to be used to build
various proxies...

NOTE: currently most proxy object do not use weak refs to reference the 
      objcet, thus deleting the object alone will not cause its total
	  removal...
'''


#-----------------------------------------------------------------------

import sys
import new
import types
import weakref



#-----------------------------------------------------------------------
# NOTE: the folowing two functions are *Evil*... :)
#---------------------------------------------------------proxymethod---
def proxymethod(method_name, depth=1):
	'''
	this will create a proxy to the method name in the containing namespace.

	NOTE: this will add the method_name to the *containing namespace* [evil laugh].
	'''
	# text of the new function....
	txt = '''\
def %(method_name)s(self, *p, **n):
	"""
	this is the proxy to %(method_name)s method.
	"""
	return getproxytarget(self).%(method_name)s(*p, **n)
proxy = %(method_name)s'''
	# execute the above code...
	exec (txt % {'method_name': method_name})
	# update the NS...
	sys._getframe(depth).f_locals[method_name] = proxy


#--------------------------------------------------------proxymethods---
def proxymethods(names, depth=1):
	'''
	this will generate a direct proxy for each name in names.
	'''
	for name in names:
		proxymethod(name, depth+1)


#------------------------------------------------------getproxytarget---
def getproxytarget(obj):
	'''
	this will return the unproxied target object.
	'''
	ogetattribute = object.__getattribute__
	try:
		return ogetattribute(obj, ogetattribute(obj, '__proxy_target_attr_name__'))
	except:
		if not isproxy(obj):
			raise TypeError, 'obj must be a proxy (got: %s).' % obj
		raise



#-----------------------------------------------------------------------
#-------------------------------------------------------------isproxy---
def isproxy(obj):
	'''
	this will return True if obj is a proxy object (relative to AbstractProxy).

	NOTE: this will work only for the pli framework proxies that inherit 
	      from AbstractProxy.
	'''
	return isinstance(obj, AbstractProxy)



#-----------------------------------------------------------------------
#-------------------------------------------------------AbstractProxy---
# this is here for:
# 	1) use of isproxy.
# 	   it is helpful if all *similar* classes be a subclass of one
# 	   parent class for easy identification...
# 	2) define the default configuration for use with the 'proxymethod'
# 	   and 'proxymethods' helper functions...
class AbstractProxy(object):
	'''
	this is a base class for all proxies...

	NOTE: this is not to be used directly.
	'''
	# this defines the attr name used to store the proxied object.
	__proxy_target_attr_name__ = 'proxy_target'



#-----------------------------------------------------------------------
# this section defines component mix-ins...
#--------------------------------------------------ProxyWithReprMixin---
class ProxyWithReprMixin(AbstractProxy):
	'''
	proxy mixin. this defines a nice proxy repr method.
	'''
	def __repr__(self):
		'''
		'''
		ogetattribute = object.__getattribute__
		return '<%s proxy at %s to %s>' % (ogetattribute(self, '__class__').__name__, 
											hex(id(self)),
											repr(getproxytarget(self)))


#------------------------------------------------ComparibleProxyMixin---
class ComparibleProxyMixin(AbstractProxy):
	'''
	proxy mixin. this will transfer the rich comparison calls directly 
	to the target...
	'''
	__proxy_target_attr_name__ = 'proxy_target'

	# these cant be avoided without eval...
	def __eq__(self, other):
		'''
		'''
		return getproxytarget(self) == other	
	def __ne__(self, other):
		'''
		'''
		return getproxytarget(self) != other
	def __gt__(self, other):
		'''
		'''
		return getproxytarget(self) > other	
	def __lt__(self, other):
		'''
		'''
		return getproxytarget(self) < other	
	def __ge__(self, other):
		'''
		'''
		return getproxytarget(self) >= other	
	def __le__(self, other):
		'''
		'''
		return getproxytarget(self) <= other	


#----------------------------------------------------CachedProxyMixin---
# TODO write a more elaborate cache manager... (wee need to take into
#      consideration, input args... etc.)
#      might be good to make an "iscached" predicate...
# NOTE: from here on all proxies are by default cached...
class CachedProxyMixin(AbstractProxy):
	'''
	proxy mixin. this defines basic cacheing mechanisms and cache
	manipulation routines.
	'''
	# this may either be None or a dict-like (usualy a weakref.WeakKeyDictionary)
	# if None the proxy caching will be disabled
	__proxy_cache__ = None

	def __new__(cls, source, *p, **n):
		'''
		'''
		res = cls._getcached(source)
		if res == None and hasattr(cls, '__proxy_cache__') and cls.__proxy_cache__ != None:
			obj = super(CachedProxyMixin, cls).__new__(cls, source, *p, **n)
			cls._setcache(source, obj)
			return obj
		return super(CachedProxyMixin, cls).__new__(cls, source, *p, **n)
##	@classmethod
	def _getcached(cls, source):
		'''
		'''
		if hasattr(cls, '__proxy_cache__') and cls.__proxy_cache__ != None \
				and source in cls.__proxy_cache__:
			return cls.__proxy_cache__[source]
		return None
	_getcached = classmethod(_getcached)
##	@classmethod
	def _setcache(cls, source, obj):
		'''
		'''
		if hasattr(cls, '__proxy_cache__') and cls.__proxy_cache__ != None:
			cls.__proxy_cache__[source] = obj
	_setcache = classmethod(_setcache)


##!!! rewrite the folowing three.... (or create inherit specific options/variants)
#----------------------------------------------GetattributeProxyMixin---
class GetattributeProxyMixin(AbstractProxy):
	'''
	proxy mixin. this defines a basic __getattribute__ method that supports 
	      the __proxy_public_attrs__ protocol...

	NOTE: if this protocol is not needed use proxymethod('__getattribute__') instead...
	'''
	# this defines the attributes that are resolved to the proxy itself
	# (not the target object)...
	__proxy_public_attrs__ = ()

	def __getattribute__(self, name):
		'''
		'''
		ogetattribute = object.__getattribute__
		proxy_target_attr = ogetattribute(self, '__proxy_target_attr_name__')
		if name in ogetattribute(self, '__proxy_public_attrs__') + (proxy_target_attr,):
			return super(GetattributeProxyMixin, self).__getattribute__(name)
##		return ogetattribute(self, proxy_target_attr).__getattribute__(name)
		# here the reason we use getattribute is to go through the full
		# *get attribute* dance in the proxied object...
		return getattr(ogetattribute(self, proxy_target_attr), name)


#------------------------------------------GetattrRecursiveProxyMixin---
class GetattrRecursiveProxyMixin(AbstractProxy):
	'''
	proxy mixin. this provides recursion e.g. will wrap the attrs using 
	the __wrapper__.
	this overloads __getattr__.

	NOTE: if __wrapper__ is None this will use self.__class__ as a wrapper.
	'''
	# this will define the callable used to wrap the attributes
	# returned by __getattr__.
	__wrapper__ = None
	
	def __getattr__(self, name):
		'''
		'''
		obj = super(GetattrRecursiveProxyMixin, self).__getattr__(name)
		wrapper = None
		try:
			wrapper = self.__wrapper__
		except:
			pass
		if wrapper == None:
			wrapper = self.__class__
			if hasattr(wrapper, '__proxy__'):
				wrapper = wrapper.__proxy__
		return wrapper(obj)
		

#-------------------------------------GetattributeRecursiveProxyMixin---
class GetattributeRecursiveProxyMixin(AbstractProxy):
	'''
	proxy mixin. this provides recursion e.g. will wrap the attrs using 
	the __wrapper__.
	this overloads __getattribute__.

	NOTE: if __wrapper__ is None this will use self.__class__ as a wrapper.
	'''
	# this will define the callable used to wrap the attributes
	# returned by __getattribute__.
	__wrapper__ = None
	# this defines the attributes that are resolved to the proxy itself
	# (not the target object)...
	# NOTE: this is here for TranparentInheritAndOverrideProxy
	#       compatibility...
	# NOTE: the attrs defined here will not get wrapped.
	__proxy_public_attrs__ = ()
	
	def __getattribute__(self, name):
		'''
		'''
		ogetattribute = object.__getattribute__
		obj = super(GetattributeRecursiveProxyMixin, self).__getattribute__(name)
		if name in ogetattribute(self, '__proxy_public_attrs__') + (ogetattribute(self, '__proxy_target_attr_name__'),):
			return obj
		wrapper = None
		try:
			wrapper = ogetattribute(self, '__wrapper__')
		except:
			pass
		if wrapper == None:
			##!!! rewrite as this will work with anything but the InheritAndOverrideProxy !!!##
			wrapper = ogetattribute(self, '__class__')
			if hasattr(wrapper, '__proxy__'):
				wrapper = wrapper.__proxy__
		return wrapper(obj)


###-------------------------------------------MappingRecursiveProxyMixin---
####!!! NOT TESTED !!!##
##class MappingRecursiveProxyMixin(AbstractProxy):
##	'''
##	proxy mixin. this provides recursion e.g. will wrap the attrs using 
##	the __wrapper__.
##	this overloads __getattribute__.
##
##	NOTE: if __wrapper__ is None this will use self.__class__ as a wrapper.
##	'''
##	# this will define the callable used to wrap the attributes
##	# returned by __getattribute__.
##	__wrapper__ = None
##	# this defines the attributes that are resolved to the proxy itself
##	# (not the target object)...
##	# NOTE: this is here for TranparentInheritAndOverrideProxy
##	#       compatibility...
##	# NOTE: the attrs defined here will not get wrapped.
##	__proxy_public_attrs__ = ()
##	
##	def __getitem__(self, name):
##		'''
##		'''
##		ogetattribute = object.__getattribute__
##		obj = super(MappingRecursiveProxyMixin, self).__getitem__(name)
##		wrapper = None
##		try:
##			wrapper = ogetattribute(self, '__wrapper__')
##		except:
##			pass
##		if wrapper == None:
##			##!!! rewrite as this will work with anything but the InheritAndOverrideProxy !!!##
##			cls = ogetattribute(self, '__class__')
##			if hasattr(cls, '__proxy__'):
##				cls = cls.__proxy__
##			return cls(obj)
##		return wrapper(obj)



#-----------------------------------------------------------------------
# this section defines ready to use base proxies...
#---------------------------------------------InheritAndOverrideProxy---
# this is the Proxy cache...
_InheritAndOverrideProxy_cache = weakref.WeakKeyDictionary()
#
# NOTE: the problem that might accur here is when we assign to
#       self.__class__.something
# TODO test module support (e.g. proxieng a module)...
# XXX there is a problem with the targets __new__ and __init__
#     methods...
#     they can get called on proxy init...
#
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# this works as follows:
# 1) create a class that inherits from InheritAndOverrideProxy and the
#    proxiead objects class...
#    reference code:
#		class local_proxy(InheritAndOverrideProxy, proxied.__class__):
#			pass
# 2) creates an object from the above class, and sets its __dict__ to
#    reference the target objects __dict__. thus enabling setting and
#    referencing data to the proxied object....
#
class InheritAndOverrideProxy(CachedProxyMixin, ProxyWithReprMixin):
	'''
	this is a general (semi-transparent) proxy.
	'''
	# this defines the attribute name where the proxy target is
	# stored...
	__proxy_target_attr_name__ = 'proxy_target'
	# this is used to generate unique proxy class names...
	__proxy_count__ = 0
	# this may either be None or a dict-like (usualy a weakref.WeakKeyDictionary)
	# if None the proxy caching will be disabled
##	__proxy_cache__ = _InheritAndOverrideProxy_cache

	def __new__(cls, source, *p, **n):
		'''
		'''
		osetattr = object.__setattr__
		cls_name = cls.__name__
		proxy = cls
		try:
			# process proxy cache...
			_obj = cls._getcached(source)
			if _obj != None:
				return _obj
			# create an object of a class (also just created) inherited
			# from cls and source.__class__
			_obj = object.__new__(new.classobj('',(cls, source.__class__), {}))
			# get the new class....
			cls = object.__getattribute__(_obj, '__class__')
			cls.__proxy__ = proxy
			# name the new class... 
			# NOTE: the name may not be unique!
			cls.__name__ = cls_name + '_' + str(cls.__proxy_count__)
			cls.__proxy_count__ += 1
			# considering that the class we just created is unique we
			# can use it as a data store... (and we do not want to
			# polute the targets dict :) )
			setattr(cls, cls.__proxy_target_attr_name__, source)
			# replace the dict so that the proxy behaves exactly like
			# the target...
			osetattr(_obj, '__dict__', source.__dict__)
		# we fall here in case we either are a class constructor, function or a callable....
		# WARNING: this is Python implementation specific!!
		except (TypeError, AttributeError), e:
			# function or callable
			if type(source) in (types.FunctionType, types.LambdaType, types.MethodType, weakref.CallableProxyType):
				# callable wrapper hook...
				if hasattr(cls, '__proxy_call__') and cls.__proxy_call__ != None:
					return cls.__proxy_call__(source)
				return source
			# class (nested class constructors...)
			elif callable(source):
				# class wrapper hook...
				if hasattr(cls, '__proxy_class__') and cls.__proxy_class__ != None:
					return cls.__proxy_class__(source)
				return source
			##!!!!!! is this correct???
			return source
		# process proxy cache...
		cls._setcache(source, _obj)
		return _obj
	# this is here to define the minimal __init__ format...
	# WARNING: there is a danger to call the targets __init__ so
	#          keep this empty!!!
	def __init__(self, source, *p, **n):
		'''
		'''
##		super(InheritAndOverrideProxy, self).__init__(source, *p, **n)
##	def __proxy_call__(self, target):
##		'''
##		'''
##		return target
##	def __proxy_class__(self, target):
##		'''
##		'''
##		return target


#-----------------------------------TranparentInheritAndOverrideProxy---
# this is the Proxy cache...
_TranparentInheritAndOverrideProxy_cache = weakref.WeakKeyDictionary() 
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# TODO test if we need any other magic methods???
class TranparentInheritAndOverrideProxy(InheritAndOverrideProxy, 
											GetattributeProxyMixin, 
											ComparibleProxyMixin, 
											ProxyWithReprMixin):
	'''
	this is a tranparent variant of InheritAndOverrideProxy. its' behavior 
	is in no way diferent from the proxied object.

	NOTE: due to the fact that this explicitly proxies the __getattribute__ 
	      and __setattr__ calls, it is slower then the semi-transparent 
		  variant.
	'''
	__proxy_target_attr_name__ = 'proxy_target'
	__proxy_count__ = 0
##	__proxy_cache__ = _TranparentInheritAndOverrideProxy_cache
	# this defines the attributes that are resolved to the proxy itself
	# (not the target object)...
	__proxy_public_attrs__ = (
				'__proxy_call__',
				'__proxy_class__',
			)

	# directly proxy __setattr__ to the target...
##	proxymethod('__setattr__')


#--------------------------------------RecursiveInheritNOverrideProxy---
# this is the Proxy cache...
_RecursiveInheritNOverrideProxy_cache = weakref.WeakKeyDictionary() 
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
class RecursiveInheritNOverrideProxy(GetattributeRecursiveProxyMixin,
										GetattrRecursiveProxyMixin,
										InheritAndOverrideProxy, 
										ProxyWithReprMixin):
	'''
	this is a general (semi-transparent) recursive proxy. e.g. it will wrap each
	attribute before it is returned.
	'''
	__wrapper__ = None
	__proxy_count__ = 0
##	__proxy_cache__ = _RecursiveInheritNOverrideProxy_cache

	__proxy_public_attrs__ = (
				'__proxy_call__',
				'__proxy_class__',
			)



#=======================================================================
if __name__ == '__main__':
	#
	# here we creaate a class we will use as a terget for our proxy...
	# this will define seme special methods, normal methods and
	# attributes (both class and object)...
	class O(object):
		class_attr = 'some value...'
##		def __new__(cls):
##			return super(O, cls).__new__(cls)
		def __init__(self):
			self.obj_attr = 1234567
		def __call__(self):
			print 'O object (__call__)! (', self.__class__, hex(id(self)), ').'
		def meth(self, arg):
			print 'O object (meth)! (', self.__class__, hex(id(self)), ').'
		def __getattr__(self, name):
			'''
			'''
			if name == 'zzz':
				return O()
			else:
				return super(O, self).__getattr__(name)
	# create an instance of the above...
	o = O()
	# now the fun starts..
	# we define a proxy that will intercept calls to the target object.
	class Proxy(TranparentInheritAndOverrideProxy):
		def __call__(self, *p, **n):
			print 'Proxy:\n\t',
			self.proxy_target(*p, **n)
	# bind a proxy to the target...
	p = Proxy(o)
	# call the original...
	o()
	# call the proxy...
	p()
	# raw access attributes...
	print p.obj_attr
	print p.class_attr
	# set attributes via the proxy...
	p.xxx = 'xxx value...'
	p.obj_attr = 7654321
	# access new values attributes...
	print o.xxx
	print o.obj_attr
	print o.class_attr
	# print the class of the proxy and the target...
	print 'o.__class__ is', o.__class__
	print 'p.__class__ is', p.__class__
	# compare the two...
	print 'o == p ->', o == p
	# isproxy tests...
	print 'p is a proxy test ->', isproxy(p)
	print 'o is a proxy test ->', isproxy(o)
	# print a nice repr...
	print 'o is', o
	print 'p is', p
	# now we test the cache...
	# create several proxies to the same object....
	p0 = Proxy(o)
	p1 = Proxy(o)
	# test if they are the same...
	print p is p0, p0 is p1


	# and here we will create a diferent kind of proxy...
	# this as in the example above will wrap the __call__ method...
	# also this is recursive in it's nature. e.g. it will wrap each 
	# attr with it self...
	class RProxy(RecursiveInheritNOverrideProxy):
		def __call__(self, *p, **n):
			print 'Proxy:\n\t',
			self.proxy_target(*p, **n)
##		def __getattribute__(self, name):
##			'''
##			'''
##			print 'Proxy.__getattribute__(', name, ')'
##			return super(RProxy, self).__getattribute__(name)
##		def __getattr__(self, name):
##			'''
##			'''
##			print 'Proxy.__getattr__(', name, ')'
##			return super(RProxy, self).__getattr__(name)
	# here we will create a tree of objects....
	o = O()
	o.o = O()
	o.o.o = O()
	o.o.c = 'mmm'
	# now create a proxy...
	p = RProxy(o)
	# print a nice repr...
	print 'o is', o
	print 'p is', p
	print
	# do a direct call...
	o()
	# call the proxy...
	p()
	p.o()
	p.o.o()
	print
	print o.o.c
	print p.o.c
	print p.o.zzz
	o.o.zzz()
	p.o.zzz()
	p.o.zzz.zzz()
	print
	p.o.o.__call__()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
