#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20050902233636'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

__doc__ = '''\


this was in part inspired by: http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/302742
'''


#-----------------------------------------------------------------------

import time
import copy

import pli.logictypes as logictypes


#-----------------------------------------------------------------------
#---------------------------------------------------StateHistoryMixin---
# NOTE: might be good to exclude the '_history_state' attr from
#       comparisons...
class StateHistoryMixin(object):
	'''
	'''
	__copy_snapshot_valuse__ = False
	__deepcopy_snapshots__ = False


	# TODO add timesamp.....
	def hist_makesnapshot(self):
		'''
		this will save the current state to object history.
		'''
		self._history_state.unite(self.hist_diff())
	def hist_diff(self):
		'''
		generate the difference dict between the current state and the last snapshot.
		'''
		res = {}
		if not hasattr(self, '_history_state'):
			##!!!!
			raise 'no snapshot!'
		snapshot = self._history_state
		for k, v in self.__dict__.iteritems():
			if k == '_history_state':
				continue
			if k not in snapshot or snapshot[k] != v:
				if hasattr(self, '__copy_snapshot_valuse__') and not self.__copy_snapshot_valuse__:
					res[k] = v
				elif hasattr(self, '__deepcopy_snapshots__') and self.__deepcopy_snapshots__:
					res[copy.deepcopy(k)] = copy.deepcopy(v)
				else:
					res[k] = copy.copy(v)
		return res
	# XXX make this faster...
	def ismodified(self):
		'''
		retrurn True if the object is modified since the last snapshot was taken else False.
		'''
		if not hasattr(self, '_history_state'):
			##!!!!
			raise 'no snapshot!'
		snapshot = self._history_state
		return False in [ ( k in snapshot and v == snapshot[k] ) \
								for k, v in self.__dict__.iteritems() \
								if k != '_history_state']
	def hist_compact(self):
		'''
		this will flatten the history...
		'''
		if not hasattr(self, '_history_state'):
			##!!!!
			raise 'no snapshot!'
		self._history_state = logictypes.DictUnion(self._history_state.todict())
	# XXX check for depth...
	def hist_revert(self, level=0):
		'''
		will revert the state of the object to a given layer in it's history (default 0).
		'''
		snapshot = self._history_state
##		l = snapshot.members() 
##		if level < len(l):
##			level = l
		for i in xrange(level):
			snapshot.popmember()
		dct = self.__dict__
		dct.clear()
		dct.update(snapshot.todict())
		self._history_state = snapshot
		


#--------------------------------------------------StateHistoryObject---
class StateHistoryObject(StateHistoryMixin):
	'''
	'''
	def __init__(self, *p, **n):
		'''
		'''
		super(StateHistoryMixin, self).__init__(*p, **n)
		self._history_state = logictypes.DictUnion()
		self.hist_makesnapshot()



#=======================================================================
if __name__ == '__main__':


	a = StateHistoryObject()
	print a.ismodified()

	print 'raw:', a.__dict__.keys()

	a.a = 1
	a.b = 2
	print a.ismodified()

	a.hist_makesnapshot()

	print a.ismodified()

	print 'on snapshot:', a.__dict__.keys()

	a.c = 3

	print a.ismodified()

	print 'new state:', a.__dict__.keys()

	a.hist_revert()

	print a.ismodified()

	print 'hist_reverted:', a.__dict__.keys()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
