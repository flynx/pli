#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20050903013613'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.logictypes as logictypes
import pli.pattern.proxy as proxy
import pli.pattern.mixin.history as history


#-----------------------------------------------------------------------
#---------------------------------------------------StateHistoryProxy---
class StateHistoryProxy(history.StateHistoryMixin, proxy.InheritAndOverrideProxy):
	'''
	'''
	def __init__(self, *p, **n):
		'''
		'''
		self.__class__._history_state = logictypes.DictUnion()
		self.hist_makesnapshot()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
