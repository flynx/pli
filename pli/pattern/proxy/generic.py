#=======================================================================

__version__ = '''0.0.07'''
__sub_version__ = '''20040906053350'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

__doc__ = '''\
this module will define a set of utilities and classes to be used to build
various proxies...
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
def proxymethods(names, source_attr):
	'''
	this will generate a direct proxy for each name in names.
	'''
	for name in names:
		proxymethod(name, source_attr, depth=2)



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
class AbstractProxy(object):
	'''
	this is a base class for all proxies...
	'''



#-----------------------------------------------------------------------
#-----------------------------------------------------ComparibleProxy---
class ComparibleProxy(AbstractProxy):
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


#---------------------------------------------InheritAndOverrideProxy---
# NOTE: the problem that might accur here is when we assign to
#       self.__class__.something
# TODO test module support (e.g. proxieng a module)...
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
class InheritAndOverrideProxy(AbstractProxy):
	'''
	this is a general (semi-transparent) proxy.
	'''
	__proxy_target_attr_name__ = 'proxy_target'

	def __new__(cls, source, *p, **n):
		'''
		'''
		osetattr = object.__setattr__
		try:
			# create an object of a class (also just created) inherited
			# from cls and source.__class__
			_obj = object.__new__(new.classobj('',(cls, source.__class__), {}))
			# get the new class....
			cls = object.__getattribute__(_obj, '__class__')
			# considering that the class we just created is unique we
			# can use it as a data store... (and we do not want to
			# polute the targets dict :) )
			setattr(cls, cls.__proxy_target_attr_name__, source)
			# replace the dict so that the proxy behaves exactly like
			# the target...
			osetattr(_obj, '__dict__', source.__dict__)
		# we fall here in case we either are a class constructor, function or a callable....
		# WARNING: this is Python implementation specific!!
		except (TypeError, AttributeError):
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
	__proxy_public_attrs__ = (
				'proxy_target',
				'__proxy_call__',
				'__proxy_class__',
				'__proxy_target_attr_name__',
			)

	def __getattribute__(self, name):
		'''
		'''
		if name in object.__getattribute__(self, '__proxy_public_attrs__'):
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


	def __getattribute__(self, name):
		'''
		'''
		ogetattribute = object.__getattribute__
		try:
			wrapper = ogetattribute(self, '__wrapper__')
			return wrapper(super(TranparentInheritAndOverrideProxy, self).__getattribute__(name))
		except:
			return ogetattribute(self, '__class__')(super(TranparentInheritAndOverrideProxy, self).__getattribute__(name))



#=======================================================================
if __name__ == '__main__':
	
	class O(object):
		'''
		'''
		def __call__(self):
			'''
			'''
			print 'O object! (', self.__class__, ')',

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



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
