#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20040909150818'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.pattern.mixin.mapping as mapping



#-----------------------------------------------------------------------
#-------------------------------------------------------DispatchError---
class DispatchError(Exception):
	pass



#-----------------------------------------------------------------------
class AbstractDispatch(object):
	'''
	'''
	pass


#-----------------------------------------------------------------------
#
# the most basic dispatch is a dict.
#
# 
#
#-------------------------------------------------------BasicDispatch---
class CallableDispatch(object):
	'''
	'''
	def __call__(self, obj):
		'''
		'''
		return self[obj]
	

#-------------------------------------------------------QueryDispatch---
# this will provide a query interface...
class QueryDispatch(object):
	'''
	'''
	pass


# this is a mapping mixin....
class MappingDispatch(object):
	'''
	'''
	# this is a 
	__targets__ = None

	def __getitem__(self, name):
		'''
		'''
		pass
	def __setitem__(self, name):
		'''
		'''
		pass
	def __delitem__(self, name):
		'''
		'''
		pass
	def __contains__(self, name):
		'''
		'''
		pass
	def __iter__(self):
		'''
		'''
		pass




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
