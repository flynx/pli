#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20041009204038'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.interface as interface
import pli.misc.acl as acl


#-----------------------------------------------------------------------
# object oriented....
# isvisible
isvisible = acl.isvisible

# isaccesible
isaccessible = acl.isaccessible


# XXX this is here for compatibility resons only!! (remove!)
isglobalmethodallowed = acl.isglobalmethodallowed


#-----------------------------------------------------------------------
# attribute oriented...
#----------------------------------------------------------iswritable---
def iswritable(obj, name, uid=None):
	'''
	'''
	if isaccesible(obj) and interface.iswritable(obj, name):
		try:
			o_obj = getattr(obj, name)
			if isaccessible(o_obj):
				return True
		except AttributeError:
			return True
	return False



#-----------------------------------------------------------------------
import __builtin__
_hasattr = __builtin__.hasattr
_getattr = __builtin__.getattr
_setattr = __builtin__.setattr
##_delattr = __builtin__.delattr


#-------------------------------------------------------------hasattr---
def hasattr(obj, name, uid=None):
	'''
	'''
	if isaccesible(obj) and _hasattr(obj, name) and interface.isreadable(obj, name):
		o_obj = getattr(obj, name)
		if isaccessible(o_obj):
			return True
	return False


#-------------------------------------------------------------getattr---
def getattr(obj, name, uid=None):
	'''
	'''
	if isaccesible(obj) and _hasattr(obj, name) and interface.isreadable(obj, name):
		o_obj = getattr(obj, name)
		if isaccessible(o_obj):
			return o_obj
	raise AttributeError, '"%s" object has no attribute "%s".' % (obj, name)


#-------------------------------------------------------------setattr---
def setattr(obj, name, value, uid=None):
	'''
	'''
	if isaccesible(obj) and iswritable(obj, name):
		if not interface.isvaluecompatible(obj, name, value):
			raise interface.InterfaceErro, 'can\'t write value %s to attribute "%s" of object "%s".' % (value, name, obj)
		return _setattr(obj, name, value)
	raise AttributeError, 'can\'t write attribute "%s" of object "%s".' % (name, obj)


###-------------------------------------------------------------delattr---
##def delattr(obj, name, uid=None):
##	'''
##	'''
##	pass



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
