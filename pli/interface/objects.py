#=======================================================================

__version__ = '''0.0.09'''
__sub_version__ = '''20041016224637'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.logictypes as logictypes
##import pli.interface.interface as interface
import interface
##import pli.interface.utils as iutils



#-----------------------------------------------------------------------
#-------------------------------------------------------------strhelp---
##!!! ugly... revise!
def strhelp(obj):
	'''
	'''
	e_res = []
	res = []
	interf = interface.getinterfaces(obj)
	format = logictypes.DictUnion(*interf)
	for n, d in format.iteritems():
		if not d.get('readable', True) or n == '*':
			continue
		t = d.get('type', None)
		if t == None and 'predicate' in d:
			t = d['predicate'].__name__
		else:
			t = 'Any type'
		if d.get('essential', False):
			e_res += [ '    %s (%s):\t\t%s\n' % (n, t, d.get('doc', 'no doc.')) ]
		else:
			res += [ '    %s (%s):\t\t%s\n' % (n, t, d.get('doc', 'no doc.')) ]
	e_res.sort()
	res.sort()
	if '*' in format:
		d = format['*']
		t = d.get('type', None)
		if t == None and 'predicate' in d:
			t = d['predicate'].__name__
		else:
			t = 'Any type'
		res += [ '    %s (%s):\t\t%s\n' % ('*', t, d.get('doc', 'no doc.')) ]
	return 'Object of %s %s \n\nEssential Attributes:\n%s\nOptional Attributes:\n%s\n' \
				% (obj.__class__.__name__, interf, ''.join(e_res), ''.join(res))



#-----------------------------------------------------------------------
# TODO make it possible to change the __implemments__ attr name...
#-------------------------------------------------ObjectWithInterface---
class ObjectWithInterface(object):
	'''
	this is a basic object with inteface support.
	'''
	# this defines the objects' interface.
	# NOTE: if this is None interface support will be disabled.
	__implemments__ = None

	def __new__(cls, *p, **n):
		'''
		'''
		obj = object.__new__(cls, *p, **n)
		ogetattribute = object.__getattribute__
		_interface = obj.__implemments__
		if _interface != None:
##			ogetattribute(obj, '__dict__').update(dict([ (n, v['default']) \
			ogetattribute(obj, '__dict__').update(dict([ (n, interface.getvalue(obj, n, v['default'])) \
									for n, v \
										in type(_interface) is tuple \
											and logictypes.DictUnion(*[ i.__format__ for i in _interface ]).iteritems() \
											or _interface.__format__.iteritems() \
										if 'default' in v and n != '*' ]))
		return obj
	def __getattribute__(self, name):
		'''
		'''
		if name in ('__implemments__',) or \
				not hasattr(self, '__implemments__') or self.__implemments__ == None or \
				interface.isreadable(self, name):
			return super(ObjectWithInterface, self).__getattribute__(name)
		raise interface.InterfaceError, 'can\'t read attribute "%s".' % name
	def __setattr__(self, name, value):
		'''
		'''
##		if name in ('__implemments__',):
##			return super(ObjectWithInterface, self).__setattr__(name, value)
		if not hasattr(self, '__implemments__') or self.__implemments__ == None or \
				interface.iswritable(self, name) and interface.isvaluecompatible(self, name, value):
##			return super(ObjectWithInterface, self).__setattr__(name, value)
			return super(ObjectWithInterface, self).__setattr__(name, interface.getvalue(self, name, value))
		raise interface.InterfaceError, 'can\'t write value "%s" to attribute "%s".' % (value, name)
	def __delattr__(self, name):
		'''
		'''
		if not hasattr(self, '__implemments__') or self.__implemments__ == None or \
				interface.isdeletable(self, name):
			return super(ObjectWithInterface, self).__delattr__(name)
		raise interface.InterfaceError, 'can\'t delete attribute "%s".' % name
	# pli protocols...
	__help__ = strhelp



#--------------------------------------------------ProxyWithInterface---
# TODO move this to pli.pattern.proxy (???)
class ProxyWithInterface(object):
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
		if not hasattr(self, '__implemments__') or self.__implemments__ == None or \
				interface.isreadable(self, name):
			return getattr(self.__source__, name)
		raise interface.InterfaceError, 'can\'t read attribute "%s".' % name
	def __setattr__(self, name, value):
		'''
		'''
		if name in ('__source__', '__implemments__'):
			return super(ProxyWithInterface, self).__setattr__(name, value)
		if not hasattr(self, '__implemments__') or self.__implemments__ == None or \
				interface.iswritable(self, name) and interface.isvaluecompatible(self, name, value):
##			return setattr(self.__source__, name, value)
			source = self.__source__
			return setattr(source, name, interface.getvalue(source, name, value))
		raise interface.InterfaceError, 'can\'t write value "%s" to attribute "%s".' % (value, name)
	def __delattr__(self, name):
		'''
		'''
		if not hasattr(self, '__implemments__') or self.__implemments__ == None or \
				interface.isdeletable(self, name):
			delattr(self.__source__, name)
		raise interface.InterfaceError, 'can\'t delete attribute "%s".' % name
	# pli protocols...
	__help__ = strhelp


#------------------------------------------------------InterfaceProxy---
class InterfaceProxy(ProxyWithInterface):
	'''
	'''
	def __init__(self, source, interface=None):
		'''
		'''
##		super(InterfaceProxy, self).__init__(source)
		self.__source__ = source
		if interface != None:
			self.__implemments__ = interface
		elif hasattr(source, '__implemments__'):
			self.__implemments__ = source.__implemments__


###-------------------------------------------------InterfaceClassProxy---
##class InterfaceClassProxy(type, InterfaceObjectProxy):
##	'''
##	'''
##	__implemments__ = None
##
##	__source__ = None
##
##	def __init__(cls, name, bases, ns):
##		type.__init__(cls, name, bases, ns)

# TODO write a transparent metaclass interface generator/checker....
#      e.g. afetr the class is defined it is used as an interface
#      "example"....
#      possibley: its objects will obey this interface... (is this
#                 logical???)


#=======================================================================
if __name__ == '__main__':

	class O(ObjectWithInterface):
		def f(self):
			print '!!!'

	o = O()

	def f():
		print 'mooo!'

	o.f = f

	print '123'

	o.xxx = 123

	print o.xxx

	print hasattr(o, '__implemments__')
	print hasattr(O, '__implemments__')

	o.f()

	print o.__help__()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
