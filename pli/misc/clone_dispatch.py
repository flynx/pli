#=======================================================================

__version__ = '''0.0.01a'''
__sub_version__ = '''20030616152331'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import copy
import dispatch



#-----------------------------------------------------------------------
# TODO do a shallow/deep versions....
#--------------------------------------------------------------_Clone---
class _Clone(dispatch.DispatchByArg):
	'''
	'''
	def __init__(self):
		'''
		'''
		dispatch.DispatchByArg.__init__(self)
	def __call__(self, arg, *pargs, **nargs):
		'''
		'''
		return dispatch.DispatchByArg.resolve(self, arg)(arg, *pargs, **nargs)
	def add_rule(self, arg, func, weight=0):
		'''
		'''
		dispatch.DispatchByArg.add_rule(self, (arg,), func, weight)
	def del_rule(self, arg):
		'''
		'''
		dispatch.DispatchByArg.del_rule(self, (arg,))


#----------------------------------------------------------_dfl_clone---
def _dfl_deepclone(obj):
	return copy.deepcopy(obj)

#=======================================================================
# setup the picklers...

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# the pickler object
clone = _Clone()
# set the default rule...
clone.add_rule(object, _dfl_deepclone, -9999)


#=======================================================================
#                                            vim:set sw=4 ts=4 nowrap :
