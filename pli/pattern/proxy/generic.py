#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20040906045211'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import new
import types
import weakref

import pli.pattern.proxy.utils as utils


#-----------------------------------------------------------------------

class AbstractProxy(object):
	'''
	'''
	# this is here to define the minimal __init__ format...
	def __init__(self, source, *p, **n):
		'''
		'''
		super(AbstractProxy, self).__init__(source, *p, **n)




#-----------------------------------------------------------------------
#---------------------------------------------InheritAndOverrideProxy---
# NOTE: the problem that might accur here is when we assign to
#       self.__class__.something
# this works as follows:
# 1) create a class that inherits from InheritAndOverrideProxy and the
#    proxiead objects class...
#    reference code:
#		class local_proxy(InheritAndOverrideProxy, proxied.__class__):
#			pass
# 2) creates an object from the above class, and sets its __dict__ to
#    reference the target objects __dict__. thus enabling setting and
#    referencing data to the proxied object....
class InheritAndOverrideProxy(AbstractProxy):
	'''
	this is a general (semi-transparent) proxy.
	'''
	def __new__(cls, source, *p, **n):
		'''
		'''
		try:
			# create an object of a class (also just created) inherited
			# from cls and source.__class__
			_obj = object.__new__(new.classobj('',(cls, source.__class__), {}))
			# get the new class....
			cls = object.__getattribute__(_obj, '__class__')
			# considering that the class we just created is unique we
			# can use it as a data store... (and we do not want to
			# polute the targets dict :) )
			cls.proxy_target = source
			# replace the dict so that the proxy behaves exactly like
			# the target...
			osetattr = object.__setattr__
			osetattr(_obj, '__dict__', source.__dict__)
		# we fall here in case we either are a class constructor, function or a callable....
		# WARNING: this is Python implementation specific!!
		except (TypeError, AttributeError):
			# function or callable
			if type(source) in (types.FunctionType, types.LambdaType, types.MethodType, weakref.CallableProxyType):
				# callable wrapper hook...
				if hasattr(self, '__proxy_call__') and self.__proxy_call__ != None:
					return self.__proxy_call__(source)
				return source
			# class (nested class constructors...)
			elif callable(source):
				# class wrapper hook...
				if hasattr(self, '__proxy_class__') and self.__proxy_class__ != None:
					return self.__proxy_class__(source)
				return source
		return _obj
##	def __proxy_call__(self, target):
##		'''
##		'''
##		return target
##	def __proxy_class__(self, target):
##		'''
##		'''
##		return target


#-----------------------------------TranparentInheritAndOverrideProxy---
class TranparentInheritAndOverrideProxy(InheritAndOverrideProxy):
	'''
	this is a tranparent variant of InheritAndOverrideProxy. its' behavior 
	is in no way diferent from the proxied object.

	NOTE: due to the fact that this explicitly proxies the __getattribute__ 
	      and __setattr__ calls, it is slower then the semi-transparent 
		  variant.
	'''
	__proxy_public_attrs__ = (
				'proxy_target',
				'__proxy_call__',
				'__proxy_class__',
			)

	def __getattribute__(self, name):
		'''
		'''
		if name in object.__getattribute__(self, '__proxy_public_attrs__'):
			return super(TranparentInheritAndOverrideProxy, self).__getattribute__(name)
		return self.proxy_target.__getattribute__(name)
	# directly proxy __setattr__ to the target...
	utils.proxymethods('__setattr__', 'proxy_target')

	# these can't be avoided without eval...
	def __eq__(self, other):
		'''
		'''
		return self.proxy_target == other
	def __ne__(self, other):
		'''
		'''
		return self.proxy_target != other
	def __gt__(self, other):
		'''
		'''
		return self.proxy_target > other
	def __lt__(self, other):
		'''
		'''
		return self.proxy_target < other
	def __ge__(self, other):
		'''
		'''
		return self.proxy_target >= other
	def __le__(self, other):
		'''
		'''
		return self.proxy_target <= other
	
	# Q: do we need any other magic methods???


#--------------------------------------RecursiveInheritNOverrideProxy---
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


#-----------------------------------------------------ComparibleProxy---
class ComparibleProxy(object):
	'''
	'''
##	# these cant be avoided without eval...
##	def __eq__(self, other):
##		'''
##		'''
##		return self.proxy_target == other
##	def __ne__(self, other):
##		'''
##		'''
##		return self.proxy_target != other
##	def __gt__(self, other):
##		'''
##		'''
##		return self.proxy_target > other
##	def __lt__(self, other):
##		'''
##		'''
##		return self.proxy_target < other
##	def __ge__(self, other):
##		'''
##		'''
##		return self.proxy_target >= other
##	def __le__(self, other):
##		'''
##		'''
##		return self.proxy_target <= other


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



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
