#=======================================================================

__version__ = '''0.0.05'''
__sub_version__ = '''20040910153526'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.logictypes as logictypes
##import pli.interface.interface as interface
import interface



#-----------------------------------------------------------------------
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
			ogetattribute(obj, '__dict__').update(dict([ (n, v['default']) \
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
##			return super(InterfaceProxy, self).__setattr__(name, value)
		if not hasattr(self, '__implemments__') or self.__implemments__ == None or \
				interface.iswritable(self, name) and interface.isvaluecompatible(self, name, value):
			return super(ObjectWithInterface, self).__setattr__(name, value)
		raise interface.InterfaceError, 'can\'t write value "%s" to attribute "%s".' % (value, name)
	def __delattr__(self, name):
		'''
		'''
		if not hasattr(self, '__implemments__') or self.__implemments__ == None or \
				interface.isdeletable(self, name):
			return super(ObjectWithInterface, self).__delattr__(name)
		raise interface.InterfaceError, 'can\'t delete attribute "%s".' % name


#------------------------------------------------------InterfaceProxy---
# TODO move this to pli.pattern.proxy (???)
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
		if not hasattr(self, '__implemments__') or self.__implemments__ == None or \
				interface.isreadable(self, name):
			return getattr(self.__source__, name)
		raise interface.InterfaceError, 'can\'t read attribute "%s".' % name
	def __setattr__(self, name, value):
		'''
		'''
		if name in ('__source__', '__implemments__'):
			return super(InterfaceProxy, self).__setattr__(name, value)
		if not hasattr(self, '__implemments__') or self.__implemments__ == None or \
				interface.iswritable(self, name) and interface.isvaluecompatible(self, name, value):
			return setattr(self.__source__, name, value)
		raise interface.InterfaceError, 'can\'t write value "%s" to attribute "%s".' % (value, name)
	def __delattr__(self, name):
		'''
		'''
		if not hasattr(self, '__implemments__') or self.__implemments__ == None or \
				interface.isdeletable(self, name):
			delattr(self.__source__, name)
		raise interface.InterfaceError, 'can\'t delete attribute "%s".' % name


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


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
