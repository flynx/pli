#=======================================================================

__version__ = '''0.0.09'''
__sub_version__ = '''20040514193254'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import types
import new

import pli.functional as func
import pli.pattern.proxy.utils as utils


#-----------------------------------------------------------------------
#-----------------------------------------------StaticObjectSelfProxy---
# 
# the goal of this is to wrap the object and shadow its namespace with
# another (this is somethong like inheriting from the object and
# defining aditional data).
# this is done by:
# 1) wraping of evry method on calls and replacing the self by the
#    proxy object (see __wrap__).
# 2) superimposing a new namespace over the original/proxied objects
#    namespace (shadowing by a proxy).
# the result is runtime namespace shadowing.
#
# TODO make this work for special methods... 
#      (e.g. __iter__, __call__, ...)
#
class StaticObjectSelfProxy(object):
	'''
	this will wrap/proxy self and pass it to original methods of a wrapped/proxied object.
	'''
	# this is the proxied object...
	__proxied_object__ = None
	# this is the wrapper constructor/class that will wrap self...
	# NOTE: this must handle all internal calls...
	# NOTE: it is recommended to subclass this from StaticObjectSelfProxy...
	# NOTE: if this is not set (e.g. None) the class its self will be
	#       used here...
	#__wrapper_class__ = None

##	__wrapper__ = staticmethod(utils.wrapmethodself)

	##!!! this might not work for a discriptor....
	def __getattr__(self, name):
		'''
		'''
		proxied = self.__proxied_object__
		##!!! do we need to permanently create a proxy...
		target = getattr(proxied, name)
		if type(target) is types.MethodType:
			# wrap the target....
			return self.__wrapper__(target)
		return target
	def __wrapper__(self, meth):
		'''
		'''
		if hasattr(self, '__wrapper_class__') and self.__wrapper_class__ != None:
			wrapper_class = self.__wrapper_class__
			wrapped = wrapper_class(meth.im_self) 
		else:
			# use self a sa wrapper...
			##!!! is this safe???
			wrapper_class = self.__class__
			wrapped = self
		return new.instancemethod(meth.im_func, wrapped, wrapper_class)


#---------------------------------------PedanticStaticObjectSelfProxy---
class PedanticStaticObjectSelfProxy(StaticObjectSelfProxy):
	'''
	'''
	def __call__(self, *p, **n):
		'''
		'''
		pass
	def __iter__(self):
		'''
		'''
		pass
	##!! add a long list of special methods here... !!##
	##!!!


#-----------------------------------------------------ObjectSelfProxy---
class ObjectSelfProxy(StaticObjectSelfProxy):
	'''
	'''
##	__wrapper_class__ = None

	def __init__(self, proxied_object, wrapper_class=None):
		'''
		'''
##		super(ObjectSelfProxy).__init__()
		self.__proxied_object__ = proxied_object
		if wrapper_class != None:
			self.__wrapper_class__ = wrapper_class



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
