#=======================================================================

__version__ = '''0.0.02'''
__sub_version__ = '''20040307231653'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import types
import new


#-----------------------------------------------------------------------
#----------------------------------------createmethodwrappersinobject---
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
