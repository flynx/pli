#=======================================================================

__version__ = '''0.0.12'''
__sub_version__ = '''20040212114724'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

__doc__ = '''
General ACL Protocol:
	objects that want to use this protocol may define the following
	attributes:

	__public__			: if True will render the object accessible;
						  if False will prevent access to the object;
						  (default: True)
	__public_attrs__	: will define a list of attributes that are to be visible.
	__private_attrs__	: will define a list of attributes that are not to be visible.
	__writable_attrs__	: will define a list of attributes that are writable.
	__readonly_attrs__	: will define a list of attributes that are not writable.

	[not done]
	__global_methods_allowed__
						: will define the allowed global methods for the current object.
						  if True allow all...
	__global_methods_disallowed__
						: will define the disallowed global methods for the current object.
						  if True disallow all... (takes priority over __global_methods_allowed__)

	TODO do global method acl for attrs...

	__acl__				: ... (not yet done...)
						  the format is as follows:
						  { <obj_id> : {<prop>:<val>[, <prop>:<val>[...]]}[, ...]}
								<obj_id>	: this can be an object or a class (name or ref).
								<prop>		: this can be any of the above (except __acl__)
'''
# 
# ACL:
# 	qualifires:
# 		<qualifier-name>
# 	rules:
# 		<qualifier-name> : <action>[, <action>[...]]
# 		<action> : <qualifier-name>[, <qualifier-name>[...]]
# 	actions:
# 		default:
#	 		read
# 			write
# 			execute
# 		custon:
# 			<action-name> : <method-name>
#
# methods: (aspects)
# 	setacl(method, <acl>)
# 	
#
#


# TODO rename all attrs to __acl_<name>__ (???)


#-----------------------------------------------------------------------

import __builtin__
_hasattr = __builtin__.hasattr
_getattr = __builtin__.getattr
_setattr = __builtin__.setattr
##_delattr = __builtin__.delattr
import sys


#-----------------------------------------------------------------------
# TODO process __acl__
#-----------------------------------------------------------isvisible---
def isvisible(obj, uid=None):
	'''
	'''
	if _hasattr(obj, '__visible__') and not obj.__visible__:
		return False
	return True


#--------------------------------------------------------isaccessible---
def isaccessible(obj, uid=None):
	'''
	'''
	if _hasattr(obj, '__public__') and not obj.__public__:
		return False
	return True


#-----------------------------------------------isglobalmethodallowed---
def isglobalmethodallowed(obj, meth, uid=None):
	'''
	'''
	if isaccessible(obj) and \
		(not _hasattr(obj, '__global_methods_disallowed__') or meth not in obj.__global_methods_disallowed__) and \
		(not _hasattr(obj, '__global_methods_allowed__') or meth in obj.__global_methods_allowed__):
			return True
	return False


#-------------------------------------------------------------hasattr---
def hasattr(obj, name, uid=None):
	'''
	'''
	if isaccessible(obj) and \
			(not _hasattr(obj, '__private_attrs__') or name not in obj.__private_attrs__) and\
			(not _hasattr(obj, '__public_attrs__') or name in obj.__public_attrs__):
		if not _hasattr(obj, name):
			return False
		o_obj = _getattr(obj, name)
		if isaccessible(o_obj):
			return True
	return False


#-------------------------------------------------------------getattr---
def getattr(obj, name, uid=None):
	'''
	'''
	if isaccessible(obj) and \
			(not _hasattr(obj, '__private_attrs__') or name not in obj.__private_attrs__) and\
			(not _hasattr(obj, '__public_attrs__') or name in obj.__public_attrs__):
		o_obj = _getattr(obj, name)
		if isaccessible(o_obj):
			return o_obj
	raise AttributeError, '"%s" object has no attribute "%s".' % (obj, name)


#----------------------------------------------------------iswritable---
def iswritable(obj, name, uid=None):
	'''
	'''
	if isaccessible(obj) and \
			(not _hasattr(obj, '__private_attrs__') or name not in obj.__private_attrs__) and\
			(not _hasattr(obj, '__public_attrs__') or name in obj.__public_attrs__) and\
			(not _hasattr(obj, '__writable_attrs__') or name in obj.__writable_attrs__) and\
			(not _hasattr(obj, '__readonly_attrs__') or name not in obj.__readonly_attrs__):
		try:
			o_obj = _getattr(obj, name)
			if isaccessible(o_obj):
				return True
		except AttributeError:
			return True
	return False


#-------------------------------------------------------------setattr---
def setattr(obj, name, val, uid=None):
	'''
	'''
	if isaccessible(obj) and \
			(not _hasattr(obj, '__private_attrs__') or name not in obj.__private_attrs__) and\
			(not _hasattr(obj, '__public_attrs__') or name in obj.__public_attrs__) and\
			(not _hasattr(obj, '__writable_attrs__') or name in obj.__writable_attrs__) and\
			(not _hasattr(obj, '__readonly_attrs__') or name not in obj.__readonly_attrs__):
		return _setattr(obj, name, val)
	raise AttributeError, 'can\'t write attribute "%s" of object "%s".' % (name, obj)


###-------------------------------------------------------------delattr---
##def delattr(obj, name, uid=None):
##	'''
##	'''


###--------------------------------------------inheritclasssecuritylist---
##def inheritclasssecuritylist(prop):
##	'''
##	this will return a tuple which is the union of the security option 
##	given, set in the classes bases.
##	'''
##	cls = sys._getframe(1)
##	res = []
##	for c in cls.__bases__:
##		if _hasattr(c, prop):
##			res += _getattr(c, prop)
##	return tuple(dict([(i, None) for i in res]).keys())


#=======================================================================
#                                             vim:set ts=4 sw=4 nowrap:
