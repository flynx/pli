#=======================================================================

__version__ = '''0.5.14'''
__sub_version__ = '''20050124064633'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

from __future__ import generators
import new

##import pli.pattern.proxy as proxy


#-----------------------------------------------------------------------
#---------------------------------------------------------------apply---
apply = lambda func, *pargs, **nargs: func(*pargs, **nargs)


#--------------------------------------------------------------lcurry---
lcurry = lambda func, *pargs, **nargs:\
			lambda *p, **n:\
				func(*pargs + p, **dict(nargs.items() + n.items()))


#---------------------------------------------------------------curry---
curry = lcurry


#--------------------------------------------------------------rcurry---
# NOTE: this adds the curried args to the tail...
rcurry = lambda func, *pargs, **nargs:\
			lambda *p, **n:\
				func(*p + pargs, **dict(nargs.items() + n.items()))


#-----------------------------------------------------------fastcurry---
# Originally written by Alex Martelli
# 	http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/229472
# NOTE: though this is faster, it is also less flexible than the above
#       variants.
# NOTE: here 'arg' can not be None.
fastcurry = lambda func, arg:\
				new.instancemethod(func, arg, object)


#-------------------------------------------------------AbstractCurry---
class AbstractCurry(object):
	'''
	'''
	pass


#--------------------------------------------------------------LCurry---
class LCurry(AbstractCurry):
	'''
	this is the left curry class.
	'''
	def __new__(cls, func, *args, **kw):
		obj = object.__new__(cls)
		if isinstance(func, AbstractCurry):
			obj._curry_func = func._curry_func
			obj._curry_args = (func._curry_args[0] + args, func._curry_args[1])
			obj._curry_kw = kw = kw.copy()
			kw.update(func._curry_kw)
		else:
			obj._curry_func = func
			obj._curry_args = (args, ())
			obj._curry_kw = kw.copy()
		return obj
	def __call__(self, *args, **kw):
		return self._curry_func(*self._curry_args[0] + args + self._curry_args[1], \
										**dict(self._curry_kw.items() + kw.items()))


#---------------------------------------------------------------Curry---
Curry = LCurry


#--------------------------------------------------------------RCurry---
class RCurry(AbstractCurry):
	'''
	this is the right curry class.
	'''
	def __new__(cls, func, *args, **kw):
		obj = object.__new__(cls)
		if isinstance(func, AbstractCurry):
			obj._curry_func = func._curry_func
			obj._curry_args = (func._curry_args[0], func._curry_args[1] + args)
			obj._curry_kw = kw = kw.copy()
			kw.update(func._curry_kw)
		else:
			obj._curry_func = func
			obj._curry_args = ((), args)
			obj._curry_kw = kw.copy()
		return obj
	def __call__(self, *args, **kw):
		return self._curry_func(*self._curry_args[0] + args + self._curry_args[1], 
										**dict(self._curry_kw.items() + kw.items()))


#---------------------------------------------------------LCurryProxy---
##!!! TEST !!!##
##class LCurryProxy(AbstractCurry, proxy.TranparentInheritAndOverrideProxy):
##	'''
##	'''
##	def __init__(self, target, *p, **n):
##		'''
##		'''
##		# handle recursive curry....
##		if hasattr(target, '_curry_pargs'):
##			p = p + target._curry_pargs
##		if hasattr(target, '_curry_kw'):
##			n = dict(n.items() + target._curry_kw.items())
##		# assign the args...
##		self._curry_pargs = p
##		# XXX do we need to copy the dict???
##		self._curry_kw = n
##	def __call__(self, *p, **n):
##		'''
##		'''
##		super(CurryProxy, self).__call__(*(p + self._curry_pargs), \
##											**dict(n.items() + self._curry_kw.items()))


#---------------------------------------------------------RCurryProxy---
##!!! TEST !!!##
##class RCurryProxy(AbstractCurry, proxy.TranparentInheritAndOverrideProxy):
##	'''
##	'''
##	def __init__(self, target, *p, **n):
##		'''
##		'''
##		# handle recursive curry....
##		if hasattr(target, '_curry_pargs'):
##			p = target._curry_pargs + p
##		if hasattr(target, '_curry_kw'):
##			n = dict(n.items() + target._curry_kw.items())
##		# assign the args...
##		self._curry_pargs = p
##		# XXX do we need to copy the dict???
##		self._curry_kw = n
##	def __call__(self, *p, **n):
##		'''
##		'''
##		super(CurryProxy, self).__call__(*(self._curry_pargs + p), \
##											**dict(n.items() + self._curry_kw.items()))


#--------------------------------------------------------------negate---
# this will return a function that will return the oposite result
# (boolean) to the original....
negate = lambda f:\
			lambda *p, **n: not f(*p, **n)


#------------------------------------------------------raise_on_false---
def raise_on_false(func, exception=Exception, name=None, msg=''):
	'''
	this will return a function wraping func so as to raise exception(msg) if it returns false.
	'''
	# sanity checks...
	if func == None:
		raise TypeError, 'func must not be None.'
	if hasattr(func, '_raise_on_false_wrapped') and func._raise_on_false_wrapped:
		raise TypeError, '%s is already wrapped, won\'t wrap agen.' % func

	# define the function code...
	func_txt = """def %(function_name)s(*p, **n):
	'''wrapper of %(function_object)s callable.'''
	res = func(*p, **n)
	if not res: 
		raise exception, msg
	return res"""
	# genreate a good name if one is not given...
	if name == None:
		name = hasattr(func, '__name__') and func.__name__ != '<lambda>' and func.__name__ or 'Unnamed'
	exec (func_txt % {'function_name':name, 'function_object':func}) in locals(), globals()
	f = eval(name)
	# marck the predicate returned... (to avoid repeated wrapping (see
	# above))...
	f._raise_on_false_wrapped = True
	return f


###------------------------------------------------------------iterator---
##class _iterator(object):
##	'''
##	'''
##	def __init__(self, iter_next, iter_init, *p, **n):
##		'''
##		'''
##		init(self, *p, **n)
##		self.next = new.instancemethod(iter_next, self, iterator)
##	def __iter__(self):
##		return self



#-----------------------------------------------------------------------
##!! THE FOLLOWING ARE EXPERIMENTAL !!##
#-----------------------------------------------------------------seq---
def seq(f0, *f):
	'''
	seq(f0[, f1[, ...]]) -> res
	seq(name, f0[, f1[, ...]]) -> res

	this will return a function that when called will sequence the functions given,
	passing its arguments into each one, and returning the list of their results.

	NOTE: in the second form the name is used as name for the resulting function.
	NOTE: atleast one function must be given.
	'''
	if type(f0) is str:
		if len(f) < 1:
			raise TypeError, 'need atleast one callable in the sequence (got: 0).'

		func_txt = """def %(function_name)s(*p, **n):
		'''sequence wrapper of %(functions)s.'''
		res = []
		for func in f:
			res += [func(*p, **n)]
		return res"""
		exec (func_txt % {'function_name':f0, 'functions':f}) in locals(), globals()
		_seq = eval(f0)
	else:
		def _seq(*p, **n):
			'''
			'''
			res = []
			for func in (f0,) + f:
				res += [func(*p, **n)]
			return res
	return _seq



#-----------------------------------------------------------------------
#--------------------------------------------------------getclasstree---
def getclasstree(cls, predicate=None):
	l = []
	for c in cls.__subclasses__():
		if predicate != None and predicate(c):
			l += [(c, getclasstree(c, predicate))]
		elif predicate == None:
			l += [(c, getclasstree(c))]
	return l


#---------------------------------------------------classtreeiterdown---
# this is my first recursive iterator... :)
def classtreeiterdown(cls, predicate=None):
	'''
	this will iterate the inheritance tree branch down.
	'''
	for c in cls.__subclasses__():
		if predicate != None and predicate(c):
			yield c
			for cls in classtreeiterdown(c, predicate):
				yield cls
		elif predicate == None:
			yield c
			for cls in classtreeiterdown(c):
				yield cls
	

#-----------------------------------------------------classtreeiterup---
def classtreeiterup(cls, predicate=None):
	'''
	this will iterate the inheritance tree up.

	NOTE: this will not remove duplicate classes.
	'''
	for c in cls.__bases__:
		if predicate != None and predicate(c):
			yield c
			for cls in classtreeiterup(c, predicate):
				yield cls
		elif predicate == None:
			yield c
			for cls in classtreeiterup(c):
				yield cls
	


#=======================================================================
#											 vim:set ts=4 sw=4 nowrap :
