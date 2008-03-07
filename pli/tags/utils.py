#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20071106153539'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------
#-----------------------------------------------------------taggerfor---
def taggerfor(tagset):
	'''
	this will create a decorator for tagging objects within a given tagset.

	usage:
		tag = taggerfor(sometagset)

		@tag('a', 'b', 'c')
		def func():
			pass

		# this is sugar for:
		def func():
			pass
		soemtagset.tag(func, 'a', 'b', 'c')
	'''
	def tag(*tags):
		def _tag(func):
			tagset.tag(func, *tags)
			return func
		return _tag
	tag.__doc__ = 'decorator, will tag the function with tags within tagset (%s).' % (tagset,)
	return tag


#--------------------------------------------------TagByPathDecorator---
class TagByPathDecorator(object):
	'''
	path tagging decorator generator.

	usage:
		tags = TagByPathDecorator(soemtagset)

		@tags.a.b.c
		def func():
			pass

		# the above is the same as...
		@tags.a
		@tags.b
		@tags.c
		def func():
			pass

		# this is sugar for:
		def func():
			pass
		soemtagset.tag(func, 'a', 'b', 'c')
	'''
	def __init__(self, tagset, path=()):
		'''
		'''
		self._tagset = tagset
		self._path = path
	def __getattr__(self, name):
		'''
		'''
		return self.__class__(self._tagset, self._path + (name,))	
	def __call__(self, func):
		'''
		'''
		self._tagset.tag(func, *self._path)
		return func
		


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
