#=======================================================================

__version__ = '''0.0.09'''
__sub_version__ = '''20080907045542'''
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
# XXX attempt to get the class name form the context...
##!!! TEST !!!##
def superproxymethod(methodname, source_attr, class_name, exceptions=Exception, depth=1, decorators=()):
	'''
	create a proxy to the method name in the containing namespace.
	
	the constructed proxy will attempt to call an existing method, and
	in case it fails with exceptions, it will call the alternative from 
	the source_attr.
	
	NOTE: this will add the method_name to the containing namespace.
	NOTE: source_attr is to be used as the attr name referencing the source object.
	'''
	# text of the new function....
	txt = '''\
def %(method_name)s(self, *p, **n):
	"""
	this is the proxy to %(method_name)s method.
	"""
	try:
		return super(%(class_name)s, self).%(method_name)s(*p, **n)
	except (%(exceptions)s):
		return self.%(source_attr)s.%(method_name)s(*p, **n)
proxy = %(method_name)s'''
	# execute the above code...
	exec (txt % {
			'method_name': method_name, 
			'source_attr': source_attr,
			'class_name': class_name,
			'exceptions': type(exceptions) in (tuple, list) \
								and ', '.join([ e.__name__ for e in exceptions ]) \
								or exceptions.__name__,
			})
	# run the decorators...
	for d in decorators:
		proxy = d(proxy)
	# update the NS...
	sys._getframe(depth).f_locals[method_name] = proxy


#---------------------------------------------------------proxymethod---
# NOTE: the interface changed, so if you used something like this:
# 			proxymethod('some_method', 'attr', target_method_name='method', ...)
# 		you should now do it like this:
# 			proxymethod(('some_method', 'method'), 'attr', ...)
# TODO create a version of this with super call...
# XXX as soon as we can construct a function in pure python this will
#     need to be rewritten...
def proxymethod(method_name, source_attr, doc='', depth=1, decorators=(), explicit_self=False):
	'''
	create a proxy to the method name in the containing namespace.

	arguments:
		method_name			- the name of the method to proxy or a tuple of two strings first
							  is the name of the local method and the second is the name of the 
							  target method.
		source_attr			- attribute to which to proxy the method call.
		doc					- the doc string to use for the constructed function.
		decorators			- sequence of decorators to apply to the constructed function.
		explicit_self		- if true, pass the self to the target explicitly.

		depth				- frame depth, used for name setting (use at your own risk).

	NOTE: this will add the method_name to the containing namespace.
	NOTE: source_attr is to be used as the attr name referencing the source object.
	'''
	# text of the new function....
	txt = '''\
def %(method_name)s(self, *p, **n):
	"""%(doc)s
	this is a proxy to self.%(source_attr)s.%(target_method_name)s method.
	"""
	return self.%(source_attr)s.%(target_method_name)s(%(self_arg)s*p, **n)

# add the result to a predictable name in the NS.
proxy = %(method_name)s'''

	# get the method name and target name...
	if type(method_name) in (tuple, list):
		if len(method_name) != 2:
			raise TypeError, 'name must either be a string or a sequence of two (got: %s).' % method_name
		method_name, target_method_name = method_name[0], method_name[-1]
	else:
		target_method_name = method_name
	# doc...
	if doc == None:
		doc = ''
	else:
		doc += '\n\n'
	# explicit self passing...
	if explicit_self is True:
		self_arg = 'self, '
	else:
		self_arg = ''
	# execute the above code...
	exec (txt % {
			'doc': doc,
			'method_name': method_name, 
			'target_method_name': target_method_name, 
			'source_attr': source_attr,
			'self_arg': self_arg})
	# run the decorators...
	for d in decorators:
		proxy = d(proxy)
	# update the NS...
	sys._getframe(depth).f_locals[method_name] = proxy


#--------------------------------------------------------proxymethods---
def proxymethods(names, source_attr, decorators=(), explicit_self=False, depth=1):
	'''
	generate a direct proxy for each name.

	for more details see docs for proxymethod(...)
	'''
	for name in names:
		proxymethod(name, source_attr, depth=depth+1,
						decorators=decorators, explicit_self=explicit_self)



#-----------------------------------------------------------------------
#-------------------------------------------------------proxyproperty---
def proxyproperty(name, source_attr, depth=1, local_attr_tpl='_%s'):
	'''
	create a property that will fetch the attr name form an object 
	referenced by .source_attr if no local value is defined, otherwise
	get the local data.

	NOTE: this will shadow inherited or overwrite local existing attributes 
	      by the same name.
	NOTE: this supports local data stored in ._<name> attr (default)
	NOTE: local_attr_tpl controls the attribute name to store the data 
	      in the local namespace (must contain a string containing exactly
		  one '%s').
	'''
	local_attr = local_attr_tpl % name
	def getter(self):
		if hasattr(self, local_attr):
			return getattr(self, local_attr)
		return getattr(getattr(self, source_attr), name)
	def setter(self, val):
		setattr(self, local_attr, val)
	def remover(self):
		if hasattr(self, local_attr):
			delattr(self, local_attr)
	# define the prop...
	sys._getframe(depth).f_locals[name] \
			= property(
					fget=getter,
					fset=setter,
					fdel=remover)


#-----------------------------------------------------proxyproperties---
def proxyproperties(names, source_attr, local_attr_tpl='_%s'):
	'''
	shorthad for multiple proxyproperty use with the same source_attr.
	'''
	for name in names:
		proxyproperty(name, source_attr, depth=2, local_attr_tpl=local_attr_tpl)



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
