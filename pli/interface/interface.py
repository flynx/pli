#=======================================================================

__version__ = '''0.2.17'''
__sub_version__ = '''20040831004734'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

__doc__ = '''\
This module defines an interface definition and enforcement mechanism and
classes.
'''


#-----------------------------------------------------------------------

import inspect
import types

import pli.functional as func
import pli.logictypes as logictypes
import pli.pattern.mixin.mapping as mapping


#-----------------------------------------------------------------------
#------------------------------------------------------InterfaceError---
class InterfaceError(Exception):
	'''
	'''
	pass



#-----------------------------------------------------------------------
#----------------------------------------------------------_Interface---
class _Interface(type, mapping.Mapping):
	'''
	this is the interface metaclass.
	'''
	# this will define the interface format...
	__format__ = None
	# this if False will prevent the modification of the interface
	# after it's definition... (default: False)
	__interface_writable__ = False
	# this if True will enable element deletion from base interfaces if
	# it was not defined locally... (default: False)
	__contagious_delete__ = False

	# WARNING: do not change this unless you know what you are doing!
	__attribute_properties__ = (
				'type',
				'default',
				'predicate',
				'essential',
				'doc',
				'handler',
				'readable',
				'writable',
				'deleteable',
				# special options...
				'LIKE',
			)

	def __init__(cls, name, bases, ns):
		'''
		'''
		# sanity checks....
		if not hasattr(cls, '__format__'):
			raise InterfaceError, 'interface %s does not have a format defined.' % cls
		# check consistency...
		errs = []
		if not cls.__isconsistent__(errs):
			errs[:] = dict.fromkeys([ e.__class__.__name__ + ': '+ str(e) for e in errs ]).keys()
			raise InterfaceError, 'inconsistent interface definition for %s in:\n    %s.' % (cls, '\n    '.join(errs))
		super(_Interface, cls).__init__(name, bases, ns)
	# mapping specific:
	def __getitem__(cls, name):
		'''
		'''
		# sanity checks....
		if not hasattr(cls, '__format__'):
			raise InterfaceError, 'interface %s does not have a format defined.' % cls
		format = cls.__format__
		try:
			for c in cls.__mro__:
				if hasattr(c, '__format__') \
						and c.__format__ != None \
						and name in c.__format__:
					return c.__format__[name]
		except TypeError:
			# c was not a dict-like....
			pass
		try:
			##!!! is this correct ?
			return super(_Interface, cls).__getitem__(name)
##		except AttributeError:
		##!!!!
		except:
			raise KeyError, str(name)
	def __setitem__(cls, name, value):
		'''

		NOTE: this will only modify the current class (no base interface will change).
		'''
		if hasattr(cls, '__interface_writable__') and not cls.__interface_writable__:
			raise InterfaceError, 'the interface %s is not modifiable.' % cls
		if '__format__' in cls.__dict__ and cls.__format__ != None:
			cls.__format__[name] = value
			return
		cls.__format__ = {name: value}
	def __delitem__(cls, name):
		'''
		'''
		if hasattr(cls, '__interface_writable__') and not cls.__interface_writable__:
			raise InterfaceError, 'the interface %s is not modifiable.' % cls
		if name in cls:
			# if name is not local to this interface...
			if ('__format__' not in cls.__dict__ or name not in cls.__dict__['__format__']) \
					and (not hasattr(cls, '__contagious_delete__') or not cls.__contagious_delete__):
				raise InterfaceError, 'the interface %s is not modifiable.' % cls
			# delete... 
			# this is safe as-is as we get here in two cases: 
			# 	1. the name is local
			# 	2. we can delete the name form its container...
			try:
				del cls.__format__[name]
			except KeyError:
				for c in cls.__mro__[1:]:
					if hasattr(c, '__format__') \
							and c.__format__ != None \
							and name in c.__format__:
						del c.__format__[name]
						return 
		else:
			raise KeyError, str(name)
##	def __contains__(cls, name):
##		'''
##		'''
	def __iter__(cls):
		'''
		'''
		visited = []
		for c in cls.__mro__:
			if hasattr(c, '__format__') \
					and c.__format__ != None:
				for k in c.__format__.iterkeys():
					if k in visited:
						continue
					visited += [k]
					yield k

	def __isconsistent__(cls, errors=None):
		'''
		'''
		allowed_props = cls.__attribute_properties__
		for name in cls:
			try:
				props = cls.getattrproperty(name)
				for n in props:
					if n not in allowed_props:
						raise InterfaceError, 'unknown option "%s".' % prop
			except Exception, e:
				if errors != None:
					errors += [e]
		if errors in ([], None):
			return True
		return False
	# interface specific (1st generation):
	def getattrproperty(cls, name, prop=None):
		'''

		returns:
			None	: if prop is given but not found.
			val		: if prop is given and found (might also be None).
			dict	: if name is found and prop not given.

		NOTE: if a property is not defined for the attr None will be returned (this is the same as if its value was none).
		'''
		##!! REVISE !!##
		allowed_props = cls.__attribute_properties__ + (None,)
		if prop not in allowed_props:
			raise InterfaceError, 'unknown option "%s".' % prop
		if name not in cls:
			if '*' in cls:
				res = {}
			else:
				raise KeyError, str(name)
		else:
			res = cls[name].copy()
		# resolve the 'LIKE' prop...
		visited = [res]
		while 'LIKE' in res: 
			if type(res['LIKE']) is str:
				ext_format = cls[res['LIKE']].copy()
			elif type(res['LIKE']) is dict:
				ext_format = res['LIKE'].copy()
			else:
				raise TypeError, 'the argument of "LIKE" attribute option must '\
						 'either be of type str or dict (got: %s).' % type(res['LIKE'])
			if res['LIKE'] == name or ext_format in visited:
				# check for conflicts in the chain.... (a conflict is
				# when a name is present more than once with different
				# values).
				v = visited[0]
				# XXX is there a better way to do this??? (use sets???)
				for d in visited[1:]:
					for k in d:
						if k != 'LIKE' and k in v and d[k] != v[k]:
							raise InterfaceError, 'LIKE loop conflict in %s for attribute "%s".' % (cls, name)
						if k not in allowed_props:
							raise InterfaceError, 'unknown option "%s".' % k
						v[k] = d[k]
				del res['LIKE']
				break
			visited += [ext_format.copy()]
			del res['LIKE']
			ext_format.update(res)
			# revise...
##			res = ext_format
			res.update(ext_format)
		if prop != None:
			if prop in res:
				return res[prop]
			else:
##				raise InterfaceError, 'property "%s" is not defined for attr "%s".' % (prop, name)
				return None
		return res
	# interface methods (2nd generation):
	# TODO exception safe??????
	def isessential(cls, name):
		'''
		'''
		return cls.getattrproperty(name, 'essential') == True
	def isreadable(cls, name):
		'''
		'''
		return cls.getattrproperty(name, 'readable') in (True, None)
	def iswritable(cls, name):
		'''
		'''
		return cls.getattrproperty(name, 'writable') in (True, None)
	def isdeletable(cls, name):
		'''
		'''
		return cls.getattrproperty(name, 'deleteable') in (True, None) \
				and cls.getattrproperty(name, 'essential') != True


#-----------------------------------------------------------Interface---
class Interface(object):
	'''
	this is the basic interface class.
	this provides a basic mechanism to define object attribute format.

	NOTE: this only provides meens to define attribute format, as 
	      methods are also attributes they can be checked using the 
		  predicate mechanism.


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
					  existence in the created object.
	
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
	__metaclass__ = _Interface

	__format__ = None



#-----------------------------------------------------------------------
# utility functions
#-------------------------------------------------------getinterfaces---
def getinterfaces(obj):
	'''
	this will return a tuuple containing the supported by the object interfaces.
	'''
	if not hasattr(obj, '__implemments__') or obj.__implemments__ is None:
		return ()
	# get objects interface...
	if type(obj.__implemments__) in (list, tuple):
		return tuple(obj.__implemments__)
	else:
		return (obj.__implemments__,)


#----------------------------------------------------------checkvalue---
def checkvalue(obj, name, value, interface=None):
	'''
	this will check the correctness/compatibility of the obj, attr name 
	and value triplit.
	if all is well will return True else raise an exception.

	NOTE: if the inteface is not given, the objects interface(s) is used.
	'''
	if interface != None:
		format = (interface,)
	else:
		format = getinterfaces(obj)
	# get the effective inteface...
	star = None
	for i in format:
		# find explicit name definition...
		if name in i:
			format = i.getattrproperty(name)
			break
		# find first '*'...
		if star == None and '*' in i:
			star = i.getattrproperty('*')
	# if no explicit definition is found...
	if type(format) is not dict:
		# attr must be defined in interface (explicit or implicit)...
		if star == None:
			raise InterfaceError, 'no definition of attribute "%s" in %s.' % (name, obj)
		format = star
	# attr type...
	if 'type' in format and not issubclass(type(value), format['type']):
		raise InterfaceError, 'attribute type mismatch. "%s" attribute ' \
							'must be of type %s (got: %s).' % (name, type(value), format['type'])
	# attr predicate...
	if 'predicate' in format and not format['predicate'](value):
		raise InterfaceError, 'predicate failed for "%s" attribute.' % name
	return True
 

#-----------------------------------------------------------checkattr---
# XXX use a different getattr mechanism as this might be blocked by the
#     interface....
def checkattr(obj, name, interface=None):
	'''
	this will check the correctness/compatibility of the obj, attr name pair.
	if all is well will return True else raise an exception.

	NOTE: the value to be used is taken from the objects attribute.
	NOTE: if the inteface is not given, the objects interface(s) is used.
	'''
	return checkvalue(obj, name, getattr(obj, name), interface)



#-----------------------------------------------------------------------
# attribute level functions...
#---------------------------------------------------------isessential---
def isessential(obj, name, interface=None):
	'''
	this will return True if the name is essential, else False.

	NOTE: if the object does not support interfaces and no explicit 
	      interface was given this will return False.
	NOTE: if the interface is not given, the objects interface(s) is used.
	'''
	if interface != None:
		format = interface
	else:
		format = logictypes.DictUnion(*getinterfaces(obj)[::-1])
	if name in format:
		return format[name].get('essential', True)
	elif '*' in format:
		return format['*'].get('essential', True)
	return False


#----------------------------------------------------------isreadable---
def isreadable(obj, name, interface=None):
	'''
	this will return True if the name is readable, else False.

	NOTE: if the object does not support interfaces and no explicit 
	      interface was given this will return True.
	NOTE: if the interface is not given, the objects interface(s) is used.
	'''
	if interface != None:
		format = interface
	else:
		format = logictypes.DictUnion(*getinterfaces(obj)[::-1])
	if name in format:
		return format[name].get('readable', True)
	elif '*' in format:
		return format['*'].get('readable', True)
	return False


#----------------------------------------------------------iswritable---
def iswritable(obj, name, interface=None):
	'''
	this will return True if the name is writable, else False.

	NOTE: if the object does not support interfaces and no explicit 
	      interface was given this will return True.
	NOTE: if the interface is not given, the objects interface(s) is used.
	'''
	if interface != None:
		format = interface
	else:
		format = logictypes.DictUnion(*getinterfaces(obj)[::-1])
	if name in format:
		return format[name].get('writable', True)
	elif '*' in format:
		return format['*'].get('writable', True)
	return False


#---------------------------------------------------------isdeletable---
def isdeletable(obj, name, interface=None):
	'''
	this will return True if the name is deletable, else False.

	NOTE: if the object does not support interfaces and no explicit 
	      interface was given this will return True.
	NOTE: if the interface is not given, the objects interface(s) is used.
	'''
	if interface != None:
		format = interface
	else:
		format = logictypes.DictUnion(*getinterfaces(obj)[::-1])
	if name in format:
		return format[name].get('deletable', True) and not format[name].get('essential', False)
	elif '*' in format:
		return format['*'].get('deletable', True) and not format[name].get('essential', False)
	return False


#---------------------------------------------------isvaluecompatible---
def isvaluecompatible(obj, name, value, interface=None):
	'''
	this will return True if the obj, name and value triplet is valid, else False.

	NOTE: if the interface is not given, the objects interface(s) is used.
	'''
	try:
		return checkvalue(obj, name, value, interface)
	except:
		return False


#--------------------------------------------------------iscompatible---
# this will check all the applicable predicates...
# XXX use a different getattr mechanism as this might be blocked by the
#     interface....
def iscompatible(obj, name, interface=None):
	'''
	this will return True if the obj, name pair is valid, else False.

	NOTE: the value to be used is taken from the objects attribute.
	NOTE: if the inteface is not given, the objects interface(s) is used.
	'''
	try:
		return checkattr(obj, name, interface)
	except:
		return False



#-----------------------------------------------------------------------
# object level functions...
#-----------------------------------------------------checkessentials---
def checkessentials(obj, interface=None):
	'''
	this will check if obj contains all the essential attributes defined by the interface.

	NOTE: if the inteface is not given, the objects interface(s) is used.
	'''
	if interface != None:
		format = interface
	else:
		format = logictypes.DictUnion(*getinterfaces(obj)[::-1])
	res = {}
	for n in format:
		if n not in res:
			v = format[n].get('essential', False)
			if v not in (None, False):
				res[n] = v
	for n in res:
		if not hasattr(obj, n):
			raise InterfaceError, 'essential attribute "%s" missing from %s' % (n, obj)
		checkattr(obj, n)
	return True


#---------------------------------------------------------checkobject---
def checkobject(obj, interface=None):
	'''
	this will check if the object complies to the interface will return
	True if yes, else False.

	NOTE: if the inteface is not given, the objects interface(s) is used.
	'''
	if interface != None:
		format = interface
	else:
		format = logictypes.DictUnion(*getinterfaces(obj)[::-1])
	o_attrs = vars(obj).copy()
	for n in format:
		# Q: which one of the folowing is faster??
		if n not in o_attrs:
			if format[n].get('essential', False):
				raise InterfaceError, 'essential attribute "%s" missing from %s' % (n, obj)
		else:
			chackattr(obj, n)
		del o_attrs[n]
	if len(o_attrs) > 0:
		if '*' not in format:
			raise InterfaceError, 'excess attributes %s in object %s.' % (o_attrs.keys(), obj)
		for n in o_attrs:
			chackattr(obj, n)
	return True



#-----------------------------------------------------------------------
#--------------------------------------------------------------getdoc---
# Q: do we need type information here???
def getdoc(obj, name=None, interface=None):
	'''
	this will return a dict containing the attr name and the coresponding
	doc defined in the interface.

	NOTE: if name is not present this will return all the docs for each attr defined...
	NOTE: if the inteface is not given, the objects interface(s) is used.
	'''
	if interface != None:
		format = interface
	else:
		format = logictypes.DictUnion(*getinterfaces(obj)[::-1])
	# if name is present...
	if name != None:
		if name in format:
			return {name: format[name].get('doc', None)}
		raise InterfaceError, 'attribute "%s" is not defined in the interface for %s.' % (name, obj)
	# if name is not present...
	res = {}
	for n in format:
		if n not in res:
			res[n] = format[n].get('doc', None)
	return res



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :