#=======================================================================

__version__ = '''0.0.11'''
__sub_version__ = '''20040916024825'''
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
# Q: does this section belong here, in this module???
#---------------------------------------------------------proxymethod---
def proxymethod(method_name, depth=1):
	'''
	this will create a proxy to the method name in the containing namespace.

	NOTE: this will add the method_name to the containing namespace.
	'''
	# text of the new function....
	txt = '''\
def %(method_name)s(self, *p, **n):
	"""
	this is the proxy to %(method_name)s method.
	"""
	return getattr(self, self.__proxy_target_attr_name__).%(method_name)s(*p, **n)
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
# TODO add weakref to target option!!!
#-------------------------------------------------------AbstractProxy---
class AbstractProxy(object):
	'''
	this is a base class for all proxies...
	'''
	__proxy_target_attr_name__ = 'proxy_target'


#----------------------------------------------------------BasicProxy---
class BasicProxy(AbstractProxy):
	##!! check !!##
	def __repr__(self):
		'''
		'''
		return '<%s proxy at %s to %s>' % (object.__getattribute__(self, '__class__').__name__, 
											hex(id(self)),
											repr(getattr(self, self.__proxy_target_attr_name__)))



#-----------------------------------------------------------------------
# this section defines component mix-ins...
#-----------------------------------------------------ComparibleProxy---
class ComparibleProxy(BasicProxy):
	'''
	proxy mixin. this will transfer the rich comparison calls directly 
	to the target...
	'''
	__proxy_target_attr_name__ = 'proxy_target'

	# these cant be avoided without eval...
	def __eq__(self, other):
		'''
		'''
		return getattr(self, self.__proxy_target_attr_name__) == other
	def __ne__(self, other):
		'''
		'''
		return self.proxy_target != other
	def __gt__(self, other):
		'''
		'''
		return getattr(self, self.__proxy_target_attr_name__) > other
	def __lt__(self, other):
		'''
		'''
		return getattr(self, self.__proxy_target_attr_name__) < other
	def __ge__(self, other):
		'''
		'''
		return getattr(self, self.__proxy_target_attr_name__) >= other
	def __le__(self, other):
		'''
		'''
		return getattr(self, self.__proxy_target_attr_name__) <= other


#---------------------------------------------------------CachedProxy---
# TODO write a more elaborate cache manager... (wee need to take into
#      consideration, input args... etc.)
#      might be good to make an "iscached" predicate...
#
class CachedProxy(BasicProxy):
	'''
	'''
	# this may either be None or a dict-like (usualy a weakref.WeakKeyDictionary)
	# if None the proxy caching will be disabled
	__proxy_cache__ = None

	def __new__(cls, source, *p, **n):
		'''
		'''
		if hasattr(cls, '__proxy_cache__') and cls.__proxy_cache__ != None:
			if source in cls.__proxy_cache__:
				return cls.__proxy_cache__[source]
			else:
				res = cls.__proxy_cache__[source] = super(CachedProxy, cls).__new__(cls, source, *p, **n)
				return res
		return super(CachedProxy, cls).__new__(cls, source, *p, **n)

		

#-----------------------------------------------------------------------
# this section defines ready to use base proxies...
#---------------------------------------------InheritAndOverrideProxy---
# this is the Proxy cache...
_InheritAndOverrideProxy_cache = weakref.WeakKeyDictionary()
#
# NOTE: the problem that might accur here is when we assign to
#       self.__class__.something
# TODO test module support (e.g. proxieng a module)...
# TODO make this a child of CachedProxy...
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
##class InheritAndOverrideProxy(CachedProxy):
class InheritAndOverrideProxy(BasicProxy):
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
##	__proxy_cache__ = None
	__proxy_cache__ = _InheritAndOverrideProxy_cache

	def __new__(cls, source, *p, **n):
		'''
		'''
		osetattr = object.__setattr__
		cls_name = cls.__name__
		try:
			# process proxy cache...
			if hasattr(cls, '__proxy_cache__') and cls.__proxy_cache__ != None:
				if source in cls.__proxy_cache__:
					return cls.__proxy_cache__[source]
			# create an object of a class (also just created) inherited
			# from cls and source.__class__
			_obj = object.__new__(new.classobj('',(cls, source.__class__), {}))
			# get the new class....
			cls = object.__getattribute__(_obj, '__class__')
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
		if hasattr(cls, '__proxy_cache__') and cls.__proxy_cache__ != None:
			cls.__proxy_cache__[source] = _obj
		return _obj
	# this is here to define the minimal __init__ format...
	def __init__(self, source, *p, **n):
		'''
		'''
		super(InheritAndOverrideProxy, self).__init__(source, *p, **n)
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
# Q: do we need any other magic methods???
class TranparentInheritAndOverrideProxy(InheritAndOverrideProxy, ComparibleProxy):
	'''
	this is a tranparent variant of InheritAndOverrideProxy. its' behavior 
	is in no way diferent from the proxied object.

	NOTE: due to the fact that this explicitly proxies the __getattribute__ 
	      and __setattr__ calls, it is slower then the semi-transparent 
		  variant.
	'''
	__proxy_target_attr_name__ = 'proxy_target'
	__proxy_count__ = 0
	__proxy_cache__ = _TranparentInheritAndOverrideProxy_cache
	# this defines the attributes that are resolved to the proxy itself
	# (not the target object)...
	__proxy_public_attrs__ = (
##				'proxy_target',
				'__proxy_call__',
				'__proxy_class__',
				'__proxy_target_attr_name__',
			)

	def __getattribute__(self, name):
		'''
		'''
		ogetattribute = object.__getattribute__
		if name in ogetattribute(self, '__proxy_public_attrs__') + (ogetattribute(self, '__proxy_target_attr_name__'),):
			return super(TranparentInheritAndOverrideProxy, self).__getattribute__(name)
		return self.proxy_target.__getattribute__(name)
	# directly proxy __setattr__ to the target...
	proxymethod('__setattr__')


#--------------------------------------RecursiveInheritNOverrideProxy---
##!! test...
class RecursiveInheritNOverrideProxy(InheritAndOverrideProxy):
	'''
	'''
	__wrapper__ = None

	__proxy_public_attrs__ = (
##				'proxy_target',
				'__proxy_call__',
				'__proxy_class__',
				'__proxy_target_attr_name__',
			)

	def __getattribute__(self, name):
		'''
		'''
		ogetattribute = object.__getattribute__
		obj = super(RecursiveInheritNOverrideProxy, self).__getattribute__(name)
		if name in ogetattribute(self, '__proxy_public_attrs__') + (ogetattribute(self, '__proxy_target_attr_name__'),):
			return obj
		wrapper = None
		try:
			wrapper = ogetattribute(self, '__wrapper__')
		except:
			pass
		if wrapper == None:
			return ogetattribute(self, '__class__')(obj)
		return wrapper(obj)



#=======================================================================
if __name__ == '__main__':
	
	class O(object):
		'''
		'''
		def __call__(self):
			'''
			'''
			print 'O object! (', self.__class__, hex(id(self)), ')',

	o = O()

	class Proxy(TranparentInheritAndOverrideProxy):
		'''
		'''
		def __call__(self, *p, **n):
			'''
			'''
			print 'Proxy:',
			self.proxy_target(*p, **n)
			print '.'

	p = Proxy(o)

	o()
	print '.'

	p()

	p.xxx = 0
	print o.xxx

	print o.__class__
	print p.__class__

	print o == p

	print isproxy(p), isproxy(o)

	print o
	print p

	p0 = Proxy(o)
	p1 = Proxy(o)

	print p is p0, p0 is p1




	class RProxy(RecursiveInheritNOverrideProxy):
		'''
		'''
		def __call__(self, *p, **n):
			'''
			'''
			print 'Proxy:',
			self.proxy_target(*p, **n)
			print '.'

	o = O()
	o.o = O()
	o.o.o = O()

	p = RProxy(o)

	print o
	print p

	o()
	print '.'

	p()
	p.o()
	p.o.o()
	p.o.o.__call__()
	

#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
