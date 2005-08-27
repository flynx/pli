#=======================================================================

__version__ = '''0.2.37'''
__sub_version__ = '''20050827172432'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

__doc__ = '''\
This module defines an interface definition and enforcement mechanism and
classes.
'''


#-----------------------------------------------------------------------

import inspect
import types
import sys

import pli.functional as func
import pli.logictypes as logictypes
import pli.pattern.mixin.mapping as mapping


#-----------------------------------------------------------------------
# TODO make it possible to change the __implemments__ attr name...
# TODO write an InterfaceUnion class.... (e.g. an interface composed of
#      several interfaces, that will support the "interface" interface)
#
#
#------------------------------------------------------InterfaceError---
# TODO docs!!
class InterfaceError(Exception):
	'''
	'''
	pass



#-----------------------------------------------------------------------
#-----------------------------------------------------_BasicInterface---
class _BasicInterface(type, mapping.Mapping):
	'''
	the interface metaclass.

	this defines the basic functionality:
		- dict-like class interface.
		- 'LIKE' special prop handling.
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
		super(_BasicInterface, cls).__init__(name, bases, ns)
	# mapping specific:
	def __getitem__(cls, name):
		'''
		'''
		try:
			return cls.getattrproperty(name)
		except TypeError:
##			##!! is this needed???
##			try:
##				return super(_BasicInterface, cls).__getitem__(name)
##			except:
##				raise KeyError, str(name)
			raise KeyError, str(name)
	def __setitem__(cls, name, value):
		'''

		NOTE: this will only modify the current class (no base interface will change).
		'''
		if hasattr(cls, '__interface_writable__') and not cls.__interface_writable__:
			raise InterfaceError, 'the interface %s is not modifiable.' % cls
		if value == None and cls._isdependedon(name):
			raise InterfaceError, 'can\'t shadow attr %s due to "LIKE" dependencies.' % name
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
			#
			if cls._isdependedon(name):
				raise InterfaceError, 'can\'t remove attr %s due to "LIKE" dependencies.' % name
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
						if hasattr(c, '__interface_writable__') and not c.__interface_writable__:
							raise InterfaceError, 'the interface %s is not modifiable.' % c
						del c.__format__[name]
						return 
		else:
			raise KeyError, str(name)
	def __contains__(cls, name):
		'''
		'''
		try:
			if cls._getrealprops(name) == None:
				return False
			return True
		except:
##			##!! is this needed???
##			try:
##				return super(_BasicInterface, cls).__contains__(name)
##			except:
##				raise KeyError, str(name)
			return False
	def __iter__(cls):
		'''
		'''
		visited = []
		for c in cls.__mro__:
			if hasattr(c, '__format__') \
					and c.__format__ != None:
				for k, v in c.__format__.iteritems():
					# ignore visited or hidden items...
					if k in visited:
						continue
					if v == None:
						visited += [k]
						continue
					visited += [k]
					yield k
	# interface specific (1st generation):
	def __isconsistent__(cls, errors=None):
		'''
		'''
		err = None
		if errors != None:
			err = []
		allowed_props = cls.__attribute_properties__
		for name in cls:
			try:
				props = cls.getattrproperty(name)
				for n in props:
					if n not in allowed_props:
						raise InterfaceError, 'unknown option "%s".' % n
			except KeyError, e:
				if cls._getrealprops(name) != None:
					if err != None:
						err += [e]
					else:
						return False
			except Exception, e:
				if err != None:
					err += [e]
				else:
					return False
		if err in ([], None):
			return True
		errors.extend(err)
		return False
	def _isdependedon(cls, name):
		'''
		this will return true if the name is single occuring (not None) and at least 
		one "LIKE" prop points at it.

		NOTE: the result this returns is relative to the first occurance of name.
		'''
		lst = list(cls._realpropiter(name))
		# check if we have a LIKE prop depending on this name...
		if name in cls and len([ i for i in lst if i != None ]) < 2:
			if len(lst) > 1 and lst[0] == None:
				return False
			# we need to search... (this might be slow!)
			for c in cls.__mro__:
				try:
					for d in c.__format__.itervalues():
						if d != None and 'LIKE' in d and d['LIKE'] == name:
							return True
				except AttributeError:
					pass
		return False
	def _realpropiter(cls, name):
		'''
		'''
		if not hasattr(cls, '__format__'):
			raise InterfaceError, 'interface %s does not have a format defined.' % cls
		format = cls.__format__
		for c in cls.__mro__:
			if hasattr(c, '__format__') \
					and c.__format__ != None \
					and name in c.__format__:
				##!!! process the 'LIKE' option...
				yield c.__format__[name]
	def _getrealprops(cls, name):
		'''
		this will return the real option dict for the attr (as defined in the __format__).

		NOTE: if the attr is nod defined in the current class it will be searched in the mro.
		'''
		try:
			return cls._realpropiter(name).next()
		except StopIteration:
			raise KeyError, name
	def getattrproperty(cls, name, prop=None):
		'''

		returns:
			None	: if prop is given but not found.
			val		: if prop is given and found (might also be None).
			dict	: if name is found and prop not given.

		NOTE: if a property is not defined for the attr None will be 
		      returned (this is the same as if its value was None).
		'''
		##!! REVISE !!##
		allowed_props = cls.__attribute_properties__ + (None,)
		if prop not in allowed_props:
			raise InterfaceError, 'unknown option "%s".' % prop
		if name not in cls:
			if '*' in cls and cls['*'] != None:
				res = {}
			else:
				raise KeyError, name
		else:
			res = cls._getrealprops(name)
		res = res.copy()
		# resolve the 'LIKE' prop...
		visited = [res]
		while 'LIKE' in res: 
			if type(res['LIKE']) is str:
##				ext_format = cls._getrealprops(res['LIKE']).copy()
				for fmt in cls._realpropiter(res['LIKE']):
					if fmt != None:
						ext_format = fmt.copy()
						break
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


#----------------------------------------------------------_Interface---
# TODO docs!!
class _Interface(_BasicInterface):
	'''
	'''
	# WARNING: do not change this unless you know what you are doing!
	__attribute_properties__ = _BasicInterface.__attribute_properties__ + (
				'type',
				'default',
				'predicate',
				'essential',
				'doc',
				'handler',
				'readable',
				'writable',
				'deleteable',
			)
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
# Q: how wil the user based ACL be added??
class Interface(object):
	'''
	this is the basic interface class.
	this provides a basic mechanism to define object attribute format.

	NOTE: this only provides meens to define attribute format, as 
	      methods are also attributes they can be checked using the 
		  predicate mechanism.
	NOTE: if the value of the attr key is None, the attr will be 
	      invisible.


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
					  this will take the object, attr name and attr 
					  value as arguments and its' return will replace 
					  the original value.
					  NOTE: if the 'default' option is set it WILL get 
					        filtered through the handler.
					  NOTE: this can be called when the object is not 
					        fully initialized, thus no assumptions about
							object state should be made.
							for instance this will happen for 
							pli.interface.objects.ObjectWithInterface if
							both the handler and the default value are 
							defined.
					  NOTE: it is not recommended for this to have side 
					        effects as the handler call is not garaneed 
							to precede an attribute write (for instance,
							this should not modify the object in any 
							way).
	
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


#-------------------------------------------------------------getdata---
# XXX should types be checked here???
# TODO write a dict version of this...
def getdata(obj, interface=None):
	'''
	this will return a dict containing the data taken from the object in compliance 
	to the interface.
	'''
	if interface != None:
		format = interface
	else:
		format = logictypes.DictUnion(*getinterfaces(obj)[::-1])
	res = {}
	for k in format:
		if not hasattr(obj, k):
			if k == '*':
				continue
			format_k = format[k]
			if 'default' in format_k:
				res[k] = format_k['default']
			elif format_k.get('essential', False):
				raise InterfaceError, 'object %s does not have an essential attribute "%s".' % (obj, k)
		else:
			res[k] = getattr(obj, k)
	if '*' in format:
		##!!! HACK !!!##
		for k in [ n for n in object.__getattribute__(obj, '__dict__') if n not in format ]:
			res[k] = getattr(obj, k)
	return res


#----------------------------------------------------------checkvalue---
def checkvalue(obj, name, value, interface=None):
	'''
	this will check the correctness/compatibility of the obj, attr name 
	and value triplit.
	if all is well will return True else raise an exception.

	NOTE: if the inteface is not given, the objects interface(s) is used.
	NOTE: if neither an interface is geven nor the object has one, this will
	      allways return True.
	'''
	if interface != None:
		format = (interface,)
	else:
		format = getinterfaces(obj)
	if format == ():
		return True
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
#------------------------------------------------------------_setattr---
def getvalue(obj, name, value, interface=None):
	'''
	this will create an attribute value...
	'''
	if interface != None:
		format = interface
	else:
		format = logictypes.DictUnion(*getinterfaces(obj)[::-1])
	handler = format.get(name, {}).get('handler', False)
	if handler != False:
		return handler(obj, name, value)
	return value
	


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
	NOTE: if neither an interface is geven nor the object has one, this will
	      function as hasattr(obj, name).
	'''
	if interface != None:
		format = interface
	else:
		format = getinterfaces(obj)
		# if there is no interface defined...
		if format == ():
			return hasattr(obj, name)
		format = logictypes.DictUnion(*format[::-1])
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
	NOTE: if neither an interface is geven nor the object has one, this will
	      allways return True.
	'''
	if interface != None:
		format = interface
	else:
##		format = logictypes.DictUnion(*getinterfaces(obj)[::-1])
		format = getinterfaces(obj)
		# if there is no interface defined...
		if format == ():
			return True
		format = logictypes.DictUnion(*format[::-1])
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
	NOTE: if neither an interface is geven nor the object has one, this will
	      function as hasattr(obj, name).
	'''
	if interface != None:
		format = interface
	else:
##		format = logictypes.DictUnion(*getinterfaces(obj)[::-1])
		format = getinterfaces(obj)
		# if there is no interface defined...
		if format == ():
			return hasattr(obj, name)
		format = logictypes.DictUnion(*format[::-1])
	if name in format:
		return format[name].get('deletable', True) and not format[name].get('essential', False)
	elif '*' in format:
		return format['*'].get('deletable', True)
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
# utility functions...
#-----------------------------------------------------createdictusing---
def createdictusing(obj, interface=None):
	'''
	this will create a dict populated by values created usin the interface given.

	NOTE: the interface can either be a tuple of interfaces or a single interface.
	NOTE: the object is needed in case there is a handler defined for an 
	      attribute (if it is known that there are no handlers, it is quite safe 
		  to pass None instead of the obj). 
	'''
	res = {}
	if interface == None:
		interface = interface.getinterfaces(obj)
	for n, v in type(interface) is tuple \
							and logictypes.DictUnion(*interface).iteritems() \
							or interface.iteritems():
		if 'default' in v and n != '*':
			res[n] = getvalue(obj, n, v['default'], interface=interface)
	return res



#-----------------------------------------------------------------------
# object level functions...
#-----------------------------------------------------checkessentials---
# TODO write a dict version of this...
# TODO add multible err sideffect...
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
# TODO write a dict version of this...
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
			checkattr(obj, n)
		# remove the attr...
		o_attrs.pop(n, None)
	if len(o_attrs) > 0:
		if '*' not in format:
			raise InterfaceError, 'excess attributes %s in object %s.' % (o_attrs.keys(), obj)
		for n in o_attrs:
			checkattr(obj, n)
	return True


#-------------------------------------------------populateobjectusing---
def populateobjectusing(obj, interface=None):
	'''
	'''
	if interface == None:
		interface = interface.getinterfaces(obj)
	for n, v in createdictusing(interfaces).iteritems():
		setattr(obj, n, v)
	return obj



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



#-----------------------------------------------------------------------
#---------------------------------------------------------implemments---
def implemments(interface, depth=1):
	'''
	this will add an interface to the object.

	this function is accumulative, thus it can be called many times, and
	the interfaces will be combined in order reverse to the calls (
	maximum prcidence/priority is the last added), this also could be called 
	head addition.
	Example:
		implemments(IA)
		implemments(IB)
		implemments(IC)		# maximum priority

		is equivalent to:

		__implemments__ = (IC, IB, IA)


	NOTE: this is a (almost) shorthand for: 
			__implemments__ = interface + __implemments__
		  ...it differs in that it handles existane checks for the 
		  __implemments__ name.
	NOTE: this does not see inherited interfaces, thus they shold 
	      be *passed on* by hand before this is used.
		  Example:
		  	---cut---
			class A(object):
				implemments(IA)

			class B(A):
				# this must be done if we want the A's interface to be 
				# combined with B's...
				__implemments__ = A.__implemments__
				implemments(IA)

			--uncut--
		  but this should not be an issue as one should combine interfaces
		  by inheritance instead of combining them explicitly in the object.
	'''
	f_locals = sys._getframe(depth).f_locals
	res = f_locals.get('__implemments__', None)
	if res == None:
		f_locals['__implemments__'] = interface
		return
	# some sort of interface already exists...
	if type(res) is tuple:
		if type(interface) is tuple:
			res = interface + res
		else:
			res = (interface,) + res
	else:
		if type(interface) is tuple:
			res = interface + (res,)
		else:
			res = (interface, res) 
	f_locals['__implemments__'] = res


#-------------------------------------------------------------inherit---
def inherit(*classes, **options):
	'''
	create an interface that is a combination of the given classes 
	interfaces.

	NOTE: if there are no parent interfaces, a new and empty interface will be created.

	supported options:
		iname		- the name of the new interface (default: 'Unnamed')
	
	other options:
		depth		- do not use this unless you know what you are doing.
	'''
	name = options.pop('iname', 'Unnamed')
	depth = options.pop('depth', 1)
	# create a class...
	inter = _Interface(name, classes, {'__interface_writable__': True})
	implemments(inter, depth+1)
	


#-----------------------------------------------------------------------
# the next several functions will modify the current interface...
# NOTE: these work form inside the object itself! (ont the interface
#       object...)
#-----------------------------------------------------------------add---
# TODO add a batch variant of add...
def add(name, **options):
	'''

	NOTE: if the name is already present in the interface this will update it.

	add specific options:
		force_addition
					- this will force the modification of the interface.
		depth		- do not use this unless you know what you are doing.
	'''
	depth = options.pop('depth', 1)
	force = options.pop('force_addition', False)
	f_locals = sys._getframe(depth).f_locals
	if '__implemments__' not in f_locals:
		raise InterfaceError, 'can\'t add name %s, no interface is defined.' % name
	interface = f_locals['__implemments__']
	if type(interface) is tuple:
		raise InterfaceError, 'can\'t add name %s to an interface combination. '\
					'(use pli.interface.inherit(...) instead of __implemments__ = (...)).' % name
##	if not interface.__interface_writable__:
##		raise interface.InterfaceError, 'can\'t write value "%s" to attribute "%s".' % (value, name)
	d = interface.get(name, {})
	d.update(options)
	if force:
		interface.__format__[name] = d
	else:
		interface[name] = d


#----------------------------------------------------------------hide---
##!!! revise !!!##
def hide(name, **options):
	'''
	this will hide an attribute from an interface (e.g. it will not be visible).

	WARNING: if the attr is defined in the current interface, then this will erase its data.
	'''
	depth = options.pop('depth', 1)
	f_locals = sys._getframe(depth).f_locals
	if '__implemments__' not in f_locals:
		raise InterfaceError, 'can\'t hide name %s, no interface is defined.' % name
	interface = f_locals['__implemments__']
	if type(interface) is tuple:
		raise InterfaceError, 'can\'t hide name %s from an interface combination. '\
					'(use pli.interface.inherit(...) instead of __implemments__ = (...)).' % name
	interface[name] = None


#------------------------------------------------------------addusing---
def addusing(name, template, depth=1):
	'''
	this will add a name to the current interface using anothor name as a tmplate.
	'''
	add(name, LIKE=template, depth=depth+1)


#-------------------------------------------------------------private---
def private(name, depth=1):
	'''
	this will add name as private to the current interface (e.g. not readable and not writable).
	'''
	add(name, readable=False, writable=False, depth=depth+1)


#-----------------------------------------------------------essential---
def essential(name, depth=1):
	'''
	this will add an essential name to the current interface.
	'''
	add(name, essential, depth=depth+1)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
