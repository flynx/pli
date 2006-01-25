#=======================================================================

__version__ = '''0.0.07'''
__sub_version__ = '''20051210041342'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

__doc__ = '''\
this module will define a set of mixins providing the abbility to store and 
archive object state history, as well as basic operations with this history.

all of the classes bellow use the _history_state attribute to store the 
history, thus, this attribute must be provided by the context using the mixin(s).


NOTE: care must be taken with this set of objects as they will prevent the deletion
	  of referenced objects even if those objects or references to them are explicitly
	  deleted. this is due to that the references to them are stored in history.

	  this problem can be dealt with regular archiving and deletion or pickling.


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
# XXX add better, more pedantic error handling...
class BasicStateHistoryMixin(object):
	'''
	this mixin provides basic object history functionality.

	NOTE: the attribute read/write speed will not be affected.
	NOTE: this depends on an externaly defined _history_state attribute that 
	      is compatible with the dict union object.
	NOTE: by default this will not add any new state to the object.

	NOTE: care must be taken with this object as it will prevent the deletion
	      of referenced objects.
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
##			if k == '_history_state':
##				continue
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
	# XXX check for depth...
	# XXX should this be renamed to hist_stepback???
	def hist_revert(self, level=1):
		'''
		will revert the state of the object to a given layer in it's history.

		NOTE: if level is 0 then the object will be reverted only to the last snapshot.
		NOTE: this will not revert beyond the first snapshot of the object made.
		'''
		snapshot = self._history_state
		if level > 0 and self.hist_diff() != {}:
			level -= 1
		if len(snapshot.members()) > 1:
			for i in xrange(level):
				snapshot.popmember()
		dct = self.__dict__
		dct.clear()
		dct.update(snapshot.todict())


#---------------------------------------------------StateHistoryMixin---
##!!! REVISE !!!##
# XXX add better, more pedantic error handling...
class StateHistoryMixin(BasicStateHistoryMixin):
	'''
	this mixin extends the BasicStateHistoryMixin (see its docs for moreinfo).
	'''
	# XXX add level support...
	def hist_compact(self, level=0):
		'''
		this will flatten the history...
		'''
		if not hasattr(self, '_history_state'):
			##!!!!
			raise 'no snapshot!'
		snapshot = self._history_state
		dct = snapshot.todict()
		# XXX this might not be safe...
		snapshot.clearmembers()
		snapshot.unite(dct)
	# XXX it might be good to move this to BasicStateHistoryMixin and
	#     rewrite hist_revert to use it... (???)
	def hist_getstate(self, level=1):
		'''
		this will return a dict representing the state of the object at a given level.
		'''
		snapshot = self._history_state
		if level > 0 and self.hist_diff() != {}:
			level -= 1
		members = snapshot.members()
		snapshot = logictypes.DictUnion(*members)
		if len(members) > 1:
			for i in xrange(level):
				snapshot.popmember()
		return snapshot.todict()
			

#----------------------------------------StateHistoryWithArchiveMixin---
# XXX add better, more pedantic error handling...
class StateHistoryWithArchiveMixin(BasicStateHistoryMixin):
	'''
	this mixin provides support for archiving of history (full or partial).

	NOTE: archive restore is checked for consistency, thus, incompatible 
	      archive restore is avoided. 
	'''
	def hist_archive(self, level=0):
		'''
		this will compact the object history to the given level (default: 0) and 
		retrurn the truncated list of dicts.

		NOTE: the returned list is usable in hist_restorearchive.
		'''
		snapshot = self._history_state
		levels = snapshot.members()

		# split the history into a tail and a head :)
		head = levels[:level]
		tail = levels[level:]
		# collapse the tail...
		tail_elem = logictypes.DictUnion(*tail[::-1]).todict()
		# form a new history...
		# XXX is there a better way to do this??
		snapshot.clearmembers()
		snapshot.tailunite(*head + (tail_elem,))
		# return the archive history (list of dicts usable in
		# tailunite...)
		return tail
	def hist_restorearchive(self, archive):
		'''
		this will restore the objects' history using the archive (returned by
		the hist_archive method).

		NOTE: this will fail if the archives state differs from the first state
		      stored in the curent history.
		NOTE: this will remove the first state in history and replace it with
		      an expanded version from the archive.
		'''
		snapshot = self._history_state
		levels = snapshot.members()
		# sanity check...
		if logictypes.DictUnion(*archive[::-1]).todict() != levels[-1]:
			raise TypeError, 'inconsistent archive.'
		snapshot.clearmembers()
		snapshot.tailunite(*levels[:-1] + archive)
		


#-----------------------------------------------------------------------
# XXX might be good to move this elsware... (not exactly a mixin!)
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

	from pli.pattern.proxy.history import StateHistoryProxy

	class O(object):
		pass

	o = O()

	o.x = 123
	o.y = 321

	a = StateHistoryProxy(o)


##	a = StateHistoryObject()


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

	del a.x

	print o.__dict__.keys()


	a.hist_revert()
	a.hist_revert()
	a.hist_revert()
	a.hist_revert()
	print o.__dict__.keys()

	print '---'
	
	# test the archive...
	class HistArchProxy(StateHistoryProxy, StateHistoryWithArchiveMixin):
		'''
		'''
		pass

	a = HistArchProxy(o)
	a.x = 0
	a.hist_makesnapshot()
	a.x = 1
	a.hist_makesnapshot()
	a.x = 2
	a.hist_makesnapshot()
	a.x = 3
	a.hist_makesnapshot()
	a.x = 4
	a.hist_makesnapshot()

	print a._history_state.members()

	arch = a.hist_archive(2)

	print arch
	print a._history_state.members()

	a.hist_restorearchive(arch)

	print a._history_state.members()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
