#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20050904055725'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.logictypes as logictypes
import pli.pattern.proxy as proxy
import pli.pattern.mixin.history as history


#-----------------------------------------------------------------------
#---------------------------------------------------StateHistoryProxy---
# XXX add cloning functionality (e.g. get me an object copy at that
#     time...)
class StateHistoryProxy(history.StateHistoryMixin, proxy.InheritAndOverrideProxy):
	'''
	this will add the basic history functionality to the proxied object.

	history interface complies to the one defined in pli.pattern.mixin.history.

	NOTE: this will not add any new data to the target object.
	NOTE: this WILL change the object state on history restore.
	'''
	def __init__(self, *p, **n):
		'''
		'''
		self.__class__._history_state = logictypes.DictUnion()
		self.hist_makesnapshot()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
