#=======================================================================

__version__ = '''0.0.05'''
__sub_version__ = '''20040909163609'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.pattern.store as store


#-----------------------------------------------------------------------
#------------------------------------------------------BaseStoreProxy---
SAFE_TRNSFER=0
FORCE_OVERWRITE=1
# this stop the overwriting of data in the target backend...
IGNORE_OVERWRITE=2

class BaseStoreProxy(store.BaseStore):
	'''
	'''
##	def __init__(self, name, backend=None):
##		'''
##		'''
##		super(BaseStoreProxy, self).__init__(name)
##		if backend != None:
##			self._store_data = backend
	def _setbackend(self, backend):
		'''
		'''
		self._store_data = backend

	def getbackend(self):
		'''
		'''
		return self._store_data
	def changebackend(self, backend, flags=SAFE_TRNSFER):
		'''
		this will transfer data from the current backend to the new.
		'''
		# check for store intersections...
		from_keys = self.keys()
		to_keys = backend.keys()
		if len(from_keys) + len(to_keys) != len(dict.fromkeys(from_keys + to_keys)):
			if flags == 0:
				##!!!
				raise TypeError, 'both the curent store (%s) and the new backend (%s) have matching keys.' % (self, backend)
		for k, v in self.iteritems():
			if k in backend:
				# sanity check...
				if flags & SAFE_TRNSFER:
					##!!! fatal... (data changed during transfer)
					raise TypeError, 'data changed during transfer of store %s to %s.' % (self, backend)
				if flags & FORCE_OVERWRITE:
					pass
				elif flags & IGNORE_OVERWRITE:
					continue
			backend[k] = v
		self._setbackend(backend)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
