#=======================================================================

__version__ = '''0.0.04'''
__sub_version__ = '''20040911234403'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import types
import new
import sys


#-----------------------------------------------------------------------
#----------------------------------------createmethodwrappersinobject---
##!!! REVISE (rewrite or remove) !!!##
def createmethodwrappersinobject(source_obj, method_list, wrapper, target_obj):
	'''
	this will attach methods mentioned in method_list to the target object
	that will wrap methods of the source object.

	WARNING: this will render the target object unpicklable...
	NOTE: this can be used for classes...
	'''
	for meth in method_list:
		if hasattr(source_obj, meth):
			setattr(target_obj, meth, wrapper(getattr(source_dict, meth)))
	return target_obj


#------------------------------------------------createmethodwrappers---
##!!! REVISE (rewrite or remove) !!!##
def createmethodwrappers(source_dict, method_list, wrapper, target_dict=None):
	'''
	this will wrap methods mentioned in method_list from the source dict and
	will return a dict containing the wrappers (will update and return target_dict
	if given).
	'''
	if target_dict != None:
		res = target_dict
	else:
		res = {}
	for meth in method_list:
		if meth in source_dict:
			res[meth] = wrapper(source_dict[meth])
	return res



#-----------------------------------------------------------------------
#--------------------------------------------------genericproxymethod---
def proxymethod(method_name, source_attr, depth=1):
	'''
	this will create a proxy to the method name in the containing namespace.

	NOTE: this will add the method_name to the containing namespace.
	NOTE: source_attr is to be used as the attr name referencing the source object.
	'''
	# text of the new function....
	txt = '''\
def %(method_name)s(self, *p, **n):
	"""
	this is the proxy to %(method_name)s method.
	"""
	return self.%(source_attr)s.%(method_name)s(*p, **n)
proxy = %(method_name)s'''
	# execute the above code...
	exec (txt % {'method_name': method_name, 'source_attr': source_attr})
	# update the NS...
	sys._getframe(depth).f_locals[method_name] = proxy


#--------------------------------------------------------proxymethods---
def proxymethods(names, source_attr):
	'''
	this will generate a direct proxy for each name.
	'''
	for name in names:
		proxymethod(name, source_attr, depth=2)



#-----------------------------------------------------------------------
#------------------------------------------------------swapmethodself---
def swapmethodself(meth, wrapper, use_wrapper_as_class=True):
	'''
	'''
	return new.instancemethod(meth.im_func,
								wrapper, 
								use_wrapper_as_class and \
										wrapper or meth.im_class)
	

#------------------------------------------------------wrapmethodself---
def wrapmethodself(meth, wrapper, use_wrapper_as_class=True):
	'''
	'''
	return new.instancemethod(meth.im_func,
								wrapper(meth.im_self), 
								use_wrapper_as_class and \
										wrapper or meth.im_class)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
