#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20040831004640'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import inspect
import types

import pli.functional as func
import pli.interface.interface as interface



#-----------------------------------------------------------------------
#--------------------------------------------------_arecallablesalike---
# TODO find a better name and place....
# TODO make this more tolarant to methods (e.g. *hidden* self param)... 
def _arecallablesalike(c0, c1):
	'''
	this will compare two callables by signature...
	'''
	if type(c0) in (types.MethodType, types.FunctionType):
		argspec0 = inspect.getargspec(c0)
	else:
		argspec0 = inspect.getargspec(c0.__call__)
	if type(c1) in (types.MethodType, types.FunctionType):
		argspec1 = inspect.getargspec(c1)
	else:
		argspec1 = inspect.getargspec(c1.__call__)
	return argspec0 == argspec1



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
		res['predicate'] = func.curry(_arecallablesalike, obj)
		if not method_writable:
			res['writable'] = False
	else:
		res['type'] = type(obj)
	# doc...
	if hasattr(obj, '__doc__'):
		res['doc'] = obj.__doc__
	return res


#-----------------------------------------------------createinterface---
##!!! revise !!!##
def createinterface(obj, name=None, doc=None, methods_writable=False):
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
