#=======================================================================

__version__ = '''0.0.15'''
__sub_version__ = '''20040731001951'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.logictypes as logictypes


#-----------------------------------------------------------------------

##!!! REVISE !!!##

# TODO write more docs...
# TODO add support for pure dict interface definitions...

#------------------------------------------------------InterfaceError---
class InterfaceError(Exception):
	'''
	'''
	pass



#-----------------------------------------------------------------------
#---------------------------------------------------------isessential---
def isessential(obj, name, interface=None):
	'''
	'''
	if interface == None \
			and (not hasattr(obj, '__implemments__') or obj.__implemments__ is None):
		return False

	format = (interface != None and interface or obj.__implemments__)
	format = type(format) is tuple \
				and logictypes.DictUnion(*[ f.__format__ for f in format ]) \
				or format.__format__

	return name in format and format[name].get('essential', False) or '*' not in format


#----------------------------------------------------------iswritable---
def iswritable(obj, name, interface=None):
	'''
	'''
	if interface == None \
			and (not hasattr(obj, '__implemments__') or obj.__implemments__ is None):
		return True

	format = (interface != None and interface or obj.__implemments__)
	format = type(format) is tuple \
				and logictypes.DictUnion(*[ f.__format__ for f in format ]) \
				or format.__format__

	return name in format and format[name].get('writable', True) or \
				('*' in format and format['*'].get('writable', True))


#----------------------------------------------------------isreadable---
def isreadable(obj, name, interface=None):
	'''
	'''
	if interface == None \
			and (not hasattr(obj, '__implemments__') or obj.__implemments__ is None):
		return True

	format = (interface != None and interface or obj.__implemments__)
	format = type(format) is tuple \
				and logictypes.DictUnion(*[ f.__format__ for f in format ]) \
				or format.__format__

	return name in format and format[name].get('readable', True) or \
				('*' in format and format['*'].get('readable', True))


#--------------------------------------------------------iscompatible---
def iscompatible(obj, name, value, interface=None):
	'''
	'''
	if interface == None \
			and (not hasattr(obj, '__implemments__') or obj.__implemments__ is None):
		return True

	interface = (interface != None and interface or obj.__implemments__)

	try:
		checkattr(interface, name, value)
	except InterfaceError:
		return False
	return True


#-----------------------------------------------------------checkattr---
def checkattr(interface, name, value):
	'''
	'''
	format = type(interface) is tuple \
				and logictypes.DictUnion(*[ f.__format__ for f in interface ]) \
				or interface.__format__
	# resolve the format source...
	if name not in format:
		if '*' in format:
			attr_format = format['*']
		else:
			raise InterfaceError, 'attribute "%s" is not defined in inteface %s' % (name, interface)
	else:
		attr_format = format[name].copy()
	# special options:
	# LIKE:
	if 'LIKE' in attr_format: 
		if type(attr_format['LIKE']) is str:
			ext_format = format[attr_format['LIKE']].copy()
		elif type(attr_format['LIKE']) is dict:
			ext_format = attr_format['LIKE'].copy()
		else:
			raise TypeError, 'the argument of "LIKE" attribute option must '\
					 'either be of type str or dict (got: %s).' % type(attr_format['LIKE'])
		ext_format.update(attr_format)
		attr_format = ext_format
	# static attribute options:
	# type:
	if 'type' in attr_format and not issubclass(type(value), attr_format['type']):
		raise InterfaceError, 'attribute type mismatch. "%s" attribute ' \
							'must be of type %s (got: %s).' % (name, type(value), attr_format['type'])
	# predicate:
	if 'predicate' in attr_format and not attr_format['predicate'](value):
		raise InterfaceError, 'predicate failed for "%s" attribute.' % name
	return True


#-----------------------------------------------------checkessentials---
def checkessentials(interface, obj):
	'''
	'''
	format = type(interface) is tuple \
				and logictypes.DictUnion(*[ f.__format__ for f in interface ]) \
				or interface.__format__
	obj_attrs = dir(obj)
	for attr in format:
		if format[attr].get('essential', False) and attr not in obj_attrs:
			raise InterfaceError, 'essential attribute "%s" missing.' % attr
	return True


#---------------------------------------------------------checkobject---
##!! REVISE !!##
def checkobject(interface, obj):
	'''
	this will test the object compatibility yith the interface.
	'''
	format = type(interface) is tuple \
				and logictypes.DictUnion(*[ f.__format__ for f in interface ]) \
				or interface.__format__
	obj_attrs = dir(obj)
	obj_data = vars(obj).copy()
	for name in obj_attrs:
		val = obj_data.pop(name)
		if not interface.checkattr(name, val):
			##!!! reason...
			return False 
	# check the star :)
	if len(obj_data) > 0 and '*' not in format:
##		##!!! reason...
##		return False
		raise InterfaceError, 'excess attributes (%s).' % obj_data.keys()
	# check if any essentials are left out...
	if not interface.checkessentials(obj):
		##!!! reason...
		return False
	return True



#-----------------------------------------------------------------------
#-----------------------------------------------------------getdocstr---
# NOTE: in the following two functions the obj can either be an
#       interface or an object with interface...
def getdocstr(obj, attr=None, interface=None):
	'''
	'''
	##!!!
	pass


#----------------------------------------------------------getdocdict---
def getdocdict(obj, attr=None, interface=None):
	'''
	'''
	##!!!
	pass


#-----------------------------------------------------------------------
#
# Ways to define an interface:
# 	a) dict-like object or dict magic attr
# 		+ simple
# 		+ no format constraints
# 		- ugly syntax (??)
# 	b) attributes with special value formats
# 		+ good syntax
# 		- not all attrs may be set (???)
# 	c) attributes by example value
# 		+ simple, prototype like
# 		- limited control
#
#
#-----------------------------------------------------------Interface---
# TODO default templates...
# TODO attribute name wildcards...
# TODO regexp name matching...
#
# TODO interface mathematics... (inheritance, combinations, ...)
#
# TODO add tests and paranoya!!!
#
# TODO make this a dict-like object...
#
# Q: does this need to be a class??? ....it might be good to create an
#    interface object factory...
#
class Interface(object):
	'''
	XXX write more docs...

	the attribute definition format is as follows:
		{
			<attr-name> : 
			{
				<opt-name>: <opt-value>
				[...]
			}
			[...]
		}
	

	supported options:
		type		- value type or superclass.
		default		- this is the default value of the option.
		predicate	- this will get the option value as argument and
					  test its compliance (if the will return False
					  InterfaceError will be raised).
		essential	- this if true will guarantee the options'
					  existance in the created object.
	
		doc			- this is the attr documentation
	
		handler		- this is the alternative attribute handler.
					  this will take the option value and its old value
					  as arguments and its' return will replace the 
					  original value.
	
		readable	- this if False will prevent the attr from being
					  read.
		writable	- this if False will prevent the attr from being
					  written.
		deleteable	- this if False will prevent the attr from being
					  removed.
	
	special options:
		LIKE		- this states the attribute template. if this is
					  given all options not declared for this attribute
					  will be taken from the template.
					  the value is either the name of the attribute in
					  the current interface or a dict of the interface
					  attr definition format.
	
	special attribute names:
		'*'			- this matches any attribute not explicitly given.
	
	
	'''

	__format__ = None

	def __init__(*p, **n):
		'''
		'''
		raise TypeError, 'can\'t create an interface instance.'
	checkattr = classmethod(checkattr)
	checkessentials = classmethod(checkessentials)
	checkobject = classmethod(checkobject)


#-------------------------------------------------ObjectWithInterface---
# TODO add tests and paranoya!!!
class ObjectWithInterface(object):
	'''
	this is an object with interface support.
	'''
	# this defines the objects' interface.
	# NOTE: if this is None interface support will be disabled.
	__implemments__ = None

	def __new__(cls, *p, **n):
		'''
		'''
		obj = object.__new__(cls, *p, **n)
		interface = obj.__implemments__
		if interface != None:
			obj.__dict__.update(dict([ (n, v['default']) \
									for n, v \
										in type(interface) is tuple \
											and logictypes.DictUnion(*[ i.__format__ for i in interface ]).iteritems() \
											or interface.__format__.iteritems() \
										if 'default' in v and n != '*' ]))
		return obj
	def __getattribute__(self, name):
		'''
		'''
		if name == '__implemments__' \
				or object.__getattribute__(self, '__implemments__') == None \
				or isreadable(self, name):
			return super(ObjectWithInterface, self).__getattribute__(name)
		raise InterfaceError, 'can\'t read attribute "%s".' % name
	def __setattr__(self, name, value):
		'''
		'''
		if object.__getattribute__(self, '__implemments__') == None \
				or (iswritable(self, name) and iscompatible(self, name, value)):
			return super(ObjectWithInterface, self).__setattr__(name, value)
		raise InterfaceError, 'can\'t write value "%s" to attribute "%s".' % (value, name)
	def __delattr__(self, name):
		'''
		'''
		if object.__getattribute__(self, '__implemments__') != None \
				and isessential(self, name):
			raise InterfaceError, 'can\'t delete an essential attribute "%s".' % name
		super(ObjectWithInterface, self).__delattr__(name)


#------------------------------------------------------InterfaceProxy---
# TODO add tests and paranoya!!!
class InterfaceProxy(object):
	'''
	'''
	__implemments__ = None

	__source__ = None

	def __init__(self, source):
		'''
		'''
		self.__source__ = source
	def __getattr__(self, name):
		'''
		'''
		if self.__implemments__ == None \
				or name == '__implemments__' or isreadable(self, name):
			return getattr(self.__source__, name)
		raise InterfaceError, 'can\'t read attribute "%s".' % name
	def __setattr__(self, name, value):
		'''
		'''
		if name in ('__source__', '__implemments__'):
			return super(InterfaceProxy, self).__setattr__(name, value)
		if self.__implemments__ == None \
				or (iswritable(self, name) and iscompatible(self, name, value)):
			return setattr(self.__source__, name, value)
		raise InterfaceError, 'can\'t write value "%s" to attribute "%s".' % (value, name)
	def __delattr__(self, name):
		'''
		'''
		if self.__implemments__ != None and isessential(self, name):
			raise InterfaceError, 'can\'t delete an essential attribute "%s".' % name
		delattr(self.__source__, name)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
