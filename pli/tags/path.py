#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20080128022740'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------



#-----------------------------------------------------------------------
#----------------------------------------------RecursiveAttrPathProxy---
class RecursiveAttrPathProxy(object):
	'''
	'''
	_callback = None
	##!!! path must be a list...
	def __init__(self, root, path, callback=None, verify=None):
		'''
		'''
		self._root = root
		self._path = tuple(path)
		self._callback = callback
		self._verify = verify
	def __getattr__(self, name):
		'''
		cahe the attribute access.
		'''
		##!!!!!!
##		if name in ('__getstate__', '__setstate__', '__reduce__', '__reduce_ex__', '__slots__'):
##			##!!! what should we do here???
##			return object.__getattribute__(self._root, name)
		return self.__class__(self._root, self._path + (name,), self._callback, self._verify)
	# XXX I don't like this...
	def __call__(self, *p, **n):
		'''
		'''
		if self._callback != None:
			return self._callback(self._root, self._path, *p, **n)
		return self.__getattrpath__(self._root, self._path)(*p, **n)
	# XXX the bad thing here is that this will essentially call
	#     root.__getattr__ which most likely called us... this this
	#     may result in an infinite recursion...
	def __getattrpath__(self, root, path):
		'''
		'''
##		print path
##		res = root
##		for p in path:
##			res = getattr(res, p)
##		return res
		raise NotImplementedError
##		raise AttributeError, path[0]



#-----------------------------------------------------------------------
if __name__ == "__main__":
	
	class PPO(object):
		'''
		'''
		def __getattr__(self, name):
			'''
			'''
			return getattr(RecursiveAttrPathProxy(self, (), self._printpath), name)
		def _printpath(self, root, path, *p, **n):
			'''
			'''
			print path

	p = PPO()

	print p.a.b.c.d
	p.a.b.c.d()

	p.xxx = 1
	print p.xxx

	import pickle

	pp = pickle.dumps(p)

	ppp = pickle.loads(pp)
	print ppp.xxx

	print ppp.a.b.c.d
	ppp.a.b.c.d()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
