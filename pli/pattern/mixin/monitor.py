#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20050902173342'''
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

class IsChanged(object):
	'''
	'''
	pass

# NOTE: might be good to exclude the '_history_state' attr from
#       comparisons...
class StateHistoryMixin(object):
	'''
	'''
	__copy_snapshot_valuse__ = False
	__deepcopy_snapshots__ = False


	def __init__(self, *p, **n):
		'''
		'''
		super(StateHistoryMixin, self).__init__(*p, **n)
		self.makesnapshot()
	def makesnapshot(self):
		'''
		'''
		if not hasattr(self, '_history_state'):
			self._history_state = logictypes.DictUnion()
		# TODO add timesamp.....
		self._history_state.unite(self._diff())
	# TODO split this to a seporate function.....
	#      diff(obj1, obj2, ...) -> res
	#      res format:
	#      {
	#      		obj1_id: {
	#      					???
	#      				 }
	#      }
	#
	def _diff(self):
		'''
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
		'''
		if not hasattr(self, '_history_state'):
			##!!!!
			raise 'no snapshot!'
		snapshot = self._history_state
		return False in [ ( k in snapshot and v == snapshot[k] ) \
								for k, v in self.__dict__.iteritems() \
								if k != '_history_state']
	def compact(self):
		'''
		this will flatten the history...
		'''
		if not hasattr(self, '_history_state'):
			##!!!!
			raise 'no snapshot!'
		self._history_state = logictypes.DictUnion(self._history_state.todict())
	# TODO add mutable state restore.... (not clone...)
	#      e.g. take ref from current and use the state of the snapshot
	#      to modify current....
	# XXX check for depth...
	def revert(self, level=0):
		'''
		'''
		snapshot = self._history_state
		for i in xrange(level):
			snapshot.popmember()
		self.__dict__ = snapshot.todict() 
		self._history_state = snapshot
		



if __name__ == '__main__':

	class A(StateHistoryMixin):
		pass

	a = A()
	print a.ismodified()

	print 'raw:', a.__dict__.keys()

	a.a = 1
	a.b = 2
	print a.ismodified()

	a.makesnapshot()

	print a.ismodified()

	print 'on snapshot:', a.__dict__.keys()

	a.c = 3

	print a.ismodified()

	print 'new state:', a.__dict__.keys()

	a.revert()

	print a.ismodified()

	print 'reverted:', a.__dict__.keys()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
