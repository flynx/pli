#=======================================================================

__version__ = '''0.0.04'''
__sub_version__ = '''20040927223921'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import inspect
import types

import pli.functional as func
import pli.interface.interface as interface



#-----------------------------------------------------------------------
#-------------------------------------------------callablescompatible---
# TODO find a better name and place....
def callablescompatible(c0, c1, method_aware=False):
	'''
	this will compare two callables by signature...
	'''
	argspec = [None, None]
	i = 0
	for c in (c0, c1):
		if type(c) is types.MethodType and method_aware == True:
			argspec[i] = inspect.getargspec(c)
			# check if bound...
			if c.im_self != None:
				argspec[i] = list(argspec[i])
				# bound --> instance
				# remove the first argument...
				argspec[i][0] = argspec[i][0][1:]
				if len(argspec[i][3]) > len(argspec[i][0]):
					# this is a rare but just in case.... (for methods
					# of the form: meth(self=<...>, ...) )
					argspec[i][3] = argspec[i][3][1:]
				argspec[i] = tuple(argspec[i])
		elif type(c) in (types.MethodType, types.FunctionType):
			argspec[i] = inspect.getargspec(c)
		else:
			argspec[i] = inspect.getargspec(c.__call__)
		i += 1
	return argspec[0] == argspec[1]



#-----------------------------------------------------------------------
#-----------------------------------------------------------likevalue---
##!!! revise !!!##
def likevalue(obj, method_writable=False):
	'''
	this will create an interface property dict that describes the argument.

	NOTE: this is usefull as it will create a predicate that will check 
	      function/method signature.
	'''
	res = {}
	# type or predicate...
	if callable(obj):
		# function signature...
		res['predicate'] = func.curry(callablescompatible, obj, method_aware=True)
		if not method_writable:
			res['writable'] = False
	else:
		res['type'] = type(obj)
	# doc...
	if hasattr(obj, '__doc__'):
		res['doc'] = obj.__doc__
	return res


#------------------------------------------------------dict2interface---
def dict2interface(dict, name=None, doc=None):
	'''
	'''
	ns = {'__format__': dict}
	if doc != None:
		ns['__doc__'] = doc
	return interface._Interface(name == None and 'unnamed' or name, (object,), ns)

###-------------------------------------------------------obj2interface---
##interface = dict2interface


#-------------------------------------------------------obj2interface---
##!!! revise !!!##
def obj2interface(obj, name=None, doc=None, methods_writable=False):
	'''
	this will generate an interface from an example object.
	'''
	if name == None:
		try:
			name = 'I' + hasattr(obj, '__name__') and obj.__name__ or obj.__class__.__name__
		except:
			name = 'IUnnamed'
	format = {}
	names = dir(obj)
	for n in names:
		format[n] = likevalue(getattr(obj, n), method_writable=methods_writable)
	class I(interface.Interface):
		if doc != None:
			__doc__ = doc
		__format__ = format
	I.__name__ = name
	return I
	


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
