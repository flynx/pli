#=======================================================================

__version__ = '''0.1.06'''
__sub_version__ = '''20030712221006'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------
__doc__ = '''
this module provides the multy dispatch functionality for pickling/unpickling
objects.

the functionality defined here includes:
	- base pickler class
	- general pickle function
	- base unpickler class
	- general unpickle finelize function

this provides the ability tu register custom picklers/unpicklers for objects.
the correct function is chosen by argument types in case of the pickle and
unpickled object type for the unpickle.

'''


#-----------------------------------------------------------------------
##import cPickle as _pickle
import pickle as _pickle
import gnosis.xml.pickle as XMLpickle
from gnosis.xml.pickle.util import setParanoia

# set dfl security for gnosis.xml.pickle...
PARANOIA = 0
setParanoia(PARANOIA)

import dispatch



#=======================================================================
#---------------------------------------------------------_SavePickle---
class _WritePickle(dispatch.StaticDispatch):
	'''
	pickle writer.

	NOTE: if explicit format is not given, this uses the file extention as format.
	'''
	def __call__(self, obj, filename, format=None):
		'''
		'''
		if format == None:
			format = filename.split('.')[-1]
		return dispatch.StaticDispatch.resolve(self, format)(obj, filename, format)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
write_pickle = _WritePickle()



#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - xml_pickle- -
def xml_pickle(obj, filename, format):
	'''
	gnosis xml pickle
	'''
	f = open(filename, 'w')
	s = XMLpickle.dumps(obj)
	f.write(s)
	f.close()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
write_pickle.add_rule('xml', xml_pickle)
	
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - pkl_pickle- -
def pkl_pickle(obj, filename, format=0):
	'''
	generic python pickle
	'''
	if format not in (-1, 0, 1, 2):
		format = 0
	f = open(filename, 'w')
	_pickle.dump(obj, f, format)
	f.close()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
write_pickle.add_rule('pkl', pkl_pickle)
write_pickle.add_rule(-1, pkl_pickle)
write_pickle.add_rule(0, pkl_pickle)
write_pickle.add_rule(1, pkl_pickle)
write_pickle.add_rule(2, pkl_pickle)



#-----------------------------------------------------------------------
#------------------------------------------------------------_Pickler---
class _Pickler(dispatch.DispatchByArg):
	'''
	this is the base dispatch pickler class.
	'''
	def __init__(self):
		'''
		'''
		dispatch.DispatchByArg.__init__(self)
	def __call__(self, arg, filename=None, proto=0):
		'''
		'''
		return dispatch.DispatchByArg.resolve(self, arg)(arg, filename, proto)
	def add_rule(self, arg, func, weight=0):
		'''
		'''
		dispatch.DispatchByArg.add_rule(self, (arg,), func, weight)
	def del_rule(self, arg):
		'''
		'''
		dispatch.DispatchByArg.del_rule(self, (arg,))

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# the pickler object
pickle = _Pickler()
# setup the default rule...
pickle.add_rule(object, write_pickle, -9999)



#-----------------------------------------------------------------------
#---------------------------------------------------------_ReadPickle---
class _ReadPickle(dispatch.StaticDispatch):
	'''
	pickle loader.

	NOTE: if explicit format is not given, this uses the file extention as format.
	'''
	def __call__(self, filename, format=None):
		'''
		'''
		if format == None:
			format = filename.split('.')[-1]
		return dispatch.StaticDispatch.resolve(self, format)(filename)
	# paranoia...
	def _get_paranoia(self):
		return PARANOIA
	def _set_paranoia(self, val):
		global PARANOIA
		PARANOIA = val
		setParanoia(val)
	def _del_paranoia(self):
		self._set_paranoia(0)
	paranoia = property(fget=_get_paranoia,\
						fset=_set_paranoia,\
						fdel=_del_paranoia,\
						doc='this is the gnosis paranoia value proxy.')


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# create loader instance...
# TIP: to load a raw/unfinelized object use load_pickle.
read_pickle = _ReadPickle() 


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - xml_unpickle- -
def xml_unpickle(filename):
	'''
	open gnosis xml pickle
	'''
	f = open(filename, 'r')
	obj = XMLpickle.load(f)
	f.close()
	return obj

read_pickle.add_rule('xml', xml_unpickle)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - pkl_unpickle- -
def pkl_unpickle(filename):
	'''
	open generic python pickle
	'''
	f = open(filename, 'r')
	obj = _pickle.load(f)
	f.close()
	return obj

read_pickle.add_rule('pkl', pkl_unpickle)

		

#-----------------------------------------------------------------------
#----------------------------------------------------------_unPickler---
# NOTE: this must only finalize the object
class _unPickler(dispatch.DispatchByArg):
	'''
	this is the base dispatch pickler class.

	NOTE: this uses 'load_pickle' dispatcher to process variose file 
	      formets (e.g. file-openner-processor).
	'''
	def __init__(self):
		'''
		'''
		dispatch.DispatchByArg.__init__(self)
	def __call__(self, filename=None):
		'''
		'''
		# first unpickle
		obj = read_pickle(filename)
		return dispatch.DispatchByArg.__call__(self, obj)
	def add_rule(self, arg, func, weight=0):
		'''
		'''
		dispatch.DispatchByArg.add_rule(self, (arg,), func, weight)
	def del_rule(self, arg):
		'''
		'''
		dispatch.DispatchByArg.del_rule(self, (arg,))


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# the unpickler object
unpickle = _unPickler()
# set the default rule...
unpickle.add_rule(object, lambda obj: obj, -9999)



#=======================================================================
#                                            vim:set sw=4 ts=4 nowrap :
