#=======================================================================
'''
this packege contains basic callback aspects.
'''

#-----------------------------------------------------------------------

__version__ = '''0.1.00'''
__sub_version__ = '''20040212153720'''
__copyright__ = '''(c) Alex A. Naanou 2003'''



import aspect

#-----------------------------------------------------------------------
#---------------------------------------------------------PreCallback---
class PreCallback(aspect.Aspect):
	'''
	'''
	def __init__(self, callback=None):
		'''
		'''
		self.as_pre_callback = callback
	def pre(self, obj, meth, *pargs, **nargs):
		self.as_pre_callback(obj, meth, *pargs, **nargs)


#--------------------------------------------------------PostCallback---
class PostCallback(aspect.Aspect):
	'''
	'''
	def __init__(self, callback=None):
		'''
		'''
		self.as_post_callback = callback
	def post(self, obj, meth, ret, rexcept, *pargs, **nargs):
		self.as_post_callback(obj, meth, ret, rexcept, *pargs, **nargs)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
