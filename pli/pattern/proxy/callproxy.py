#=======================================================================
#=======================================================================

__version__ = '''0.4.00'''
__sub_version__ = '''20040223152213'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import new
import types
import weakref
from pli.functional import *


#-----------------------------------------------------------callproxy---
# NOTE: the following code might need a little cleaning-up...
#
# the problem here is that we either have to make custom class for each 
# instance, define  ALL the special  methods or do a  *magical* lookup 
# into the proxied object...
#       (neither of the three methods seems practical in current python)
#
# NOTE: to keep the obj.__dict__ intact the classes' namespace is used for
#       all instance data (this is not a problem as a new class is constructed
#       for each callproxy instance).
# NOTE: this is a good candidate for being rewritten in C or Psyco (TODO)
# NOTE: this will most likely fail with LL extensions that do not expose
#       all their data to python... (see the code)
# NOTE: some name caching is done in the following class to speed things 
#       up a bit...
#
# WARNING: this might still be week in the "return a curried __queuecall__" section,
#          as the returned object will not reflect all the original functions'/methods'
#          data & attrs, thus something like:
#                           pobj.some_meth.some_attr
#                                             will fail...
#          there appears no way around this (none that I see anyway...)
#
# NOTE: this uses a dict as the cache see utill_l.py for a list
#       version (might be good to combine the two).
#
# TODO rewrite for py2.3 (types)
# TODO try to wrap a function... (see the warning above)
# TODO add proxy filter support to proxy specific methods/attributes.
# TODO attribute callback (i.e. external post-getattr (interface: 
#         "return post_callback(obj, name, val)" and "pre_callback(obj, name)"))
#      this might be pre-getattr "pre_attr_callback" or post-getattr   
#      "post_attr_callback", in the later case the callback is to be   
#      called before/instead (?) the attr search where as in the later 
#      it gets a ready reference to the searched object.               
class callproxy(object):
	'''
	proxy to the object, intercept and curry all calls to a queue.
	'''
	def __new__(cls, obj, queue=None, cache=None, drop_refs=0, callback=None, safe=1):
		'''
		construct an appropriate class and return its object, the class is to be a
		subclass of callproxy and the objs' class, if this is to prove impossible return
		the original obj or a curried __queuecall__ if the obj is callable.

		Parameters:
			obj				: the proxied object.
			queue			: list to be used as external queue.
			cache			: optional dict to be used as proxy cache 
							  NOTE: no cache management is currently done in this class.
			drop_refs		: if true raise TypeError if trying to get a proxied objects' value.
							  NOTE: this does not prevent setting the proxied objects' value.
			callback		: a callable that gets called on proxy call.
							  NOTE: this will receive the called object as the first argument,
									and all the arguments (if any).

		if the callback is set, the call return will be the callbacks' return.
		if the queue is omitted and callback given, only the callback is to be called, so if
		a call to the proxied callable is desired it is the callbacks responsibility.
		NOTE: either one or both queue or callback must be specified.
		NOTE: the use of both queue and a callback will result in a called object slowdown.
		'''
		## do input tests (rework)
		if safe:
			# callback test
			if callback != None:
				if not callable(callback):
					raise TypeError, 'callback object must be callable.'
			elif queue == None:
				raise TypeError, 'one of either callback or queue objects must be specified.'
			# test if queue supports append
			elif not hasattr(queue, 'append'):
				raise TypeError, 'queue object must have an "append" method.'
			# test if this supports dict interface
			if cache != None and (not hasattr(cache, '__setitem__') or not hasattr(cache, '__getitem__') or not hasattr(cache, 'keys')):
				raise TypeError, 'cache object must support "__setitem__", "__getitem__" and "keys" methods'
		## see if obj is in cache
		if cache != None and obj in cache.keys():
			proxy = object.__getattribute__(cache[obj], '__class__')
			try:
				if drop_refs and proxy.__drop_refs != drop_refs:
					raise TypeError, 'proxy cache type mismatch (drop_refs option inconsistent)'
				if callback and object.__getattribute__(proxy, '_callproxy__callback') != callback:
					raise TypeError, 'proxy cache type mismatch (callback option inconsistent)'
			except AttributeError:
				pass
			if queue != None and type(obj) in (types.FunctionType, types.LambdaType, types.MethodType, weakref.CallableProxyType):
				if callback != None:
					return lambda *p, **n: (cls.__queuecall__(obj, queue, *p, **n), cache[obj](*p, **n))[1]
				else:
					return curry(cls.__queuecall__, obj, queue)
			return cache[obj]
		## start work...
		try:
			# this is quite explicit to avoid errors from misuse
			_obj = object.__new__(new.classobj('',(callproxy, obj.__class__), {}))
			cls = object.__getattribute__(_obj, '__class__')
			# we have a hungry __setattr__ lurking...  :)
			osetattr = object.__setattr__
			osetattr(_obj, '__dict__', obj.__dict__)
			cls._callproxy__obj = obj
			cls._callproxy__queue = queue
			cls._callproxy__cache = cache
			cls._callproxy__drop_refs = drop_refs
			cls._callproxy__callback = callback
			if cache != None:
				cache[obj] = _obj
		except (TypeError, AttributeError):
			# function or callable
			if type(obj) in (types.FunctionType, types.LambdaType, types.MethodType, weakref.CallableProxyType):
				if callback != None:
					if cache != None:
						cache[obj] = curry(callback, obj)
						return queue == None and cache[obj]\
								or (lambda *p, **n: (cls.__queuecall__(obj, queue, *p, **n), callback(obj, *p, **n))[1])
					return queue == None and curry(callback, obj)\
							or (lambda *p, **n: (cls.__queuecall__(obj, queue, *p, **n), callback(obj, *p, **n))[1])
				if cache != None:
					cache[obj] = curry(cls.__queuecall__, obj, queue)
					return cache[obj]
				return curry(cls.__queuecall__, obj, queue)
			# class (nested class constructors...)
			elif callable(obj):
				return obj
			# not callable and drop_refs is set
			elif drop_refs != 0:
				raise TypeError, 'can not reference a proxied object! (drop_refs option is set).'
			return obj
		return _obj
	def __init__(self, *p, **n):
		'''
		dummy init....
		this is here so as to not call the proxied objects' __init__
		'''
		pass
	def __getattribute__(self, name):
		'''
		return a proxy to self.name
		'''
		if name == '__queuecall__':
			return object.__getattribute__(self, '__queuecall__')
		# NOTE: do not use "self.__class__" as a constructor as this will result in namespace/inheritance pile-up!!
		# do a little name caching
		ogetattr = object.__getattribute__
		cls = ogetattr(self, '__class__')
		return callproxy(getattr(cls._callproxy__obj, name),\
							cls._callproxy__queue,\
							cls._callproxy__cache,\
							cls._callproxy__drop_refs,\
							ogetattr(cls, '_callproxy__callback'))
	def __setattr__(self, name, val):
		'''

		nothing special here... the usual __setattr__ semantics.
		'''
		cls = object.__getattribute__(self, '__class__')
		setattr(cls._callproxy__obj, name, val)
	def __delattr__(self, name):
		'''

		nothing special here... the usual __delattr__ semantics.
		'''
		cls = object.__getattribute__(self, '__class__')
		delattr(cls._callproxy__obj, name)
	def __queuecall__(obj, queue, *pargs, **nargs):
		'''
		enqueue an obj call to queue.
		'''
		# capture the args...
		queue.append(lambda:obj(*pargs, **nargs))
	__queuecall__ = staticmethod(__queuecall__)
	def __call__(self, *pargs, **nargs):
		'''
		call proxy.
		'''
		ogetattr = object.__getattribute__
		cls = ogetattr(self, '__class__')
		obj = ogetattr(cls, '_callproxy__obj')
		# sanity check!
		if not callable(obj):
			# raise an error (disguised as the original!! :) )
			obj(pargs, nargs)
		# NOTE: it is not forbidden to have a queue and a callback at the same time
		queue = cls._callproxy__queue
		if queue != None:
			#__doc__ = self.__class__.__obj.__call__.__doc__
			cls.__queuecall__(*(obj, queue) + pargs, **nargs)
		callback = ogetattr(cls, '_callproxy__callback')
		if callback != None:
			return callback(*(obj,) + pargs, **nargs)
		return
##	def __del__(self):
##		pass


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
