#=======================================================================


__version__ = '''0.1.08a'''
__sub_version__ = '''20040214003402'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import sys
import types
from pli.functional import curry

##import inspect



#-----------------------------------------------------------------------
#-------------------------------------------------------weavefunction---
def weavefunction(func, aspect, *pargs, **nargs):
	'''
	'''
	if isinstance(func, AspectWrapper):
		raise TypeError, 'can\'t aspect an already aspected object.'
	return AspectFunctionWrapper(func, aspect, *pargs, **nargs)


#---------------------------------------------------------weavemethod---
def weavemethod(obj, aspect, *pargs, **nargs):
	'''
	'''
	if isinstance(obj, AspectWrapper):
		raise TypeError, 'can\'t aspect an already aspected object.'
	return AspectMethodWrapper(obj, aspect, *pargs, **nargs)


#-------------------------------------------------------------unweave---
def unweave(obj):
	'''
	'''
	if isinstance(obj, AspectWrapper):
		return obj.as_obj
	else:
		raise TypeError, 'can\'t unweave, not an aspected object.'



#-----------------------------------------------------------------------
# aspect flow control.
#-------------------------------------------------------AspectControl---
class AspectControl(Exception):
	'''
	abstract aspect exception.
	'''


#----------------------------------------------------------AspectStop---
class AspectStop(AspectControl):
	'''
	this will stop the aspect and the arguments of the exception
	will be returned.
	'''


#---------------------------------------------------------AspectBreak---
class AspectBreak(AspectControl):
	'''
	this will cause an unconditional stop.
	'''


#---------------------------------------------------------AspectError---
class AspectError(AspectControl):
	'''
	general aspect error exception.
	'''



#-----------------------------------------------------------------------
#-------------------------------------------------------AspectWrapper---
class AspectWrapper(object):
	'''
	abstract aspect wrapper.
	'''
	def __init__(self, obj, aspect, *pargs, **nargs):
		self.as_obj = obj
		if pargs != () or nargs != {}:
			self.as_aspect = aspect(*pargs, **nargs)
		elif pargs == () and nargs == {} and isinstance(aspect, StaticAspect):
			# the static aspect needn't be instantiated...
			self.as_aspect = aspect
		else:
			self.as_aspect = aspect
	def run(self, obj, *pargs, **nargs):
		'''
		'''
		res = None
		try:
			if hasattr(self.as_aspect, 'pre'):
				self.as_aspect.pre(obj, self.as_obj, *pargs, **nargs) 
			try:
				res = self.call(obj, *pargs, **nargs)
			except:
				if hasattr(self.as_aspect, 'post'):
					self.as_aspect.post(obj, self.as_obj, res, sys.exc_info()[1], *pargs, **nargs)
				# get exception...
				raise
			if hasattr(self.as_aspect, 'post'):
				self.as_aspect.post(obj, self.as_obj, res, None, *pargs, **nargs)
		except AspectBreak:
			return
		except AspectStop, res:
			# might be good to return run state here...
			return res 
		return res
##	def aspect(self, obj, *pargs, **nargs):
##		'''
##		this is the aspect run generator...
##		'''
##		res = None
##		try:
##			if hasattr(self.as_aspect, 'pre'):
##				self.as_aspect.pre(obj, self.as_obj, *pargs, **nargs) 
##			try:
##				res = self.call(self.as_obj, *pargs, **nargs)
##			except:
##				if hasattr(self.as_aspect, 'post'):
##					self.as_aspect.post(obj, self.as_obj, res, sys.exc_info()[1], *pargs, **nargs)
##				# get exception...
##				raise
##			if hasattr(self.as_aspect, 'post'):
##				self.as_aspect.post(obj, self.as_obj, res, None, *pargs, **nargs)
##		except AspectBreak:
##			pass
##		except AspectStop, res:
##			yield res 
##		return res
	def call(self, obj, *pargs, **nargs):
		'''
		this is a general stub.
		'''
		return self.as_obj(obj, *pargs, **nargs)
	def __repr__(self):
		return '<aspect wrapper of' + repr(self.as_obj) + '>'


#-----------------------------------------------AspectFunctionWrapper---
class AspectFunctionWrapper(AspectWrapper):
	'''
	'''
	def __init__(self, func, aspect, *pargs, **nargs):
		super(AspectFunctionWrapper, self).__init__(func, aspect, *pargs, **nargs)
	def __call__(self, *pargs, **nargs):
		return self.run(self.as_obj, *pargs, **nargs)
	def call(self, obj, *pargs, **nargs):
		return self.as_obj(*pargs, **nargs)


#-------------------------------------------------AspectMethodWrapper---
class AspectMethodWrapper(AspectWrapper):
	'''
	'''
	def __get__(self, obj, type=None):
		'''
		'''
		return curry(self.run, obj)
	def call(self, obj, *pargs, **nargs):
		return self.as_obj(obj, *pargs, **nargs)


#--------------------------------------------------AspectClassWrapper---
class AspectClassWrapper(AspectWrapper):
	'''
	'''
	def __init__(self, func, aspect, *pargs, **nargs):
		raise NotImplementedError


#-------------------------------------------------AspectModuleWrapper---
class AspectModuleWrapper(AspectWrapper):
	'''
	'''
	def __init__(self, func, aspect, *pargs, **nargs):
		raise NotImplementedError



#=======================================================================
#-------------------------------------------------------_StaticAspect---
class _StaticAspect(type):
	'''
	'''
	def __init__(cls, name, bases, ns):
		super(_StaticAspect, cls).__init__(name, bases, ns)
		if 'pre' in ns and not isinstance(ns['pre'], classmethod):
			cls.pre = classmethod(ns['pre'])
		if 'call' in ns and not isinstance(ns['call'], classmethod):
			cls.call = classmethod(ns['call'])
		if 'post' in ns and not isinstance(ns['post'], classmethod):
			cls.post = classmethod(ns['post'])


#--------------------------------------------------------------Aspect---
class Aspect(object):
	'''
	the abstract aspect
	'''
##	def pre(self, obj, meth, *pargs, **nargs):
##		'''
##		'''
##		pass
##	def call(self, obj, *pargs, **nargs):
##		'''
##		'''
##		pass
##	def post(self, obj, meth, ret, rexcept, *pargs, **nargs):
##		'''
##		'''
##		pass

#--------------------------------------------------------StaticAspect---
# Q: do we need instance state??
class StaticAspect(Aspect):
	'''
	the abstract singleton aspect.
	'''
	__metaclass__ = _StaticAspect



#=======================================================================
if __name__ == '__main__':

	class A(StaticAspect):
		def pre(self, obj, m, *pargs, **nargs):
			print 'pre:', obj, m
		def post(self, obj, m, res, ex, *pargs, **nargs):
			print 'post:', obj

	def pp(data):
		print data
		return 'ret data'

	class X(object):
		def f(self, data='GOOOO...'):
			print data
			return 'ret data'
		ff = weavemethod(f, A)


	x=X()
	x.fff = weavefunction(x.f, A)

	print x.f('clean run...')
	print
	print x.ff('aspected run...')
	print x.ff()
	print
	print x.fff('aspected run...')
	print




	print pp('clean run...')
	print

	pp = weavefunction(pp, A)

	print pp('aspected run...')
	print

	pp = unweave(pp)

	print pp('clean run.')
	print



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
