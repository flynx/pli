#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20040307234752'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.pattern.proxy.utils as utils



#-----------------------------------------------------------------------
#-----------------------------------------------GenericMetaClassProxy---
class _GenericProxy(type):
	'''
	'''
	__proxied_class__ = None
	__proxied_methods__ = [
							'__call__',
							##!!!
						  ]

	def __init__(cls, name, bases, ns):
		'''
		'''
		obj = super(_GenericProxy, cls).__init__(name, bases, ns)
		if hasattr(obj, '__proxied_class__') and obj.__proxied_class__ != None:
			wrapper = obj.__generic_wrapper__
			utils.createmethodwrappersinobject(obj.__proxied_class__, obj.__proxied_methods__, wrapper, obj)
		return obj
	def __generic_wrapper__(meth):
		'''
		'''
		return meth
	__generic_wrapper__ = staticmethod(__generic_wrapper__)
		

#--------------------------------------------------------GenericProxy---
class StaricGenericProxy(object):
	'''
	'''
	__metaclass__ = _GenericProxy
	__proxied_class__ = None



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
