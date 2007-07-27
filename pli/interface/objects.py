#=======================================================================

__version__ = '''0.0.09'''
__sub_version__ = '''20070725023041'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.logictypes as logictypes
##import pli.interface.interface as interface
import interface
##import pli.interface.utils as iutils
import pli.pattern.proxy.generic as proxy



#-----------------------------------------------------------------------
#-------------------------------------------------------------strhelp---
##!!! ugly... revise!
# Q: should this be in this module??
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
		if t == None:
			if 'predicate' in d:
				t = d['predicate'].__name__
			else:
				t = 'Any type'
		elif hasattr(t, '__name__'):
			t = t.__name__
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
	return 'Object of %s %s \n%s\n\nEssential Attributes:\n%s\nOptional Attributes:\n%s\n' \
				% (obj.__class__.__name__, interf, obj.__doc__, ''.join(e_res), ''.join(res))




#-----------------------------------------------------------------------
# TODO make it possible to change the __implements__ attr name...
#---------------------------------------------ObjectWithInterfaceInit---
class ObjectWithInterfaceInit(object):
	'''
	this will setup the object according to the interface.
	'''
	# this defines the objects' interface.
	# NOTE: if this is None interface support will be disabled.
	__implements__ = None

	def __new__(cls, *p, **n):
		'''
		'''
		obj = object.__new__(cls, *p, **n)
		ogetattribute = object.__getattribute__
		_interface = obj.__implements__
		if _interface != None:
			ogetattribute(obj, '__dict__').update(interface.createdictusing(obj, _interface))
		return obj
	# pli protocols...
	__help__ = classmethod(strhelp)


#-------------------------------------------------ObjectWithInterface---
class ObjectWithInterface(ObjectWithInterfaceInit):
	'''
	this is a basic object with interface support.
	'''
	# this defines the objects' interface.
	# NOTE: if this is None interface support will be disabled.
	__implements__ = None

	def __getattribute__(self, name):
		'''
		'''
		if name in ('__implements__',) or \
				not hasattr(self, '__implements__') or self.__implements__ == None or \
				interface.isreadable(self, name):
			return super(ObjectWithInterface, self).__getattribute__(name)
		raise interface.InterfaceError, 'can\'t read attribute "%s".' % name
	def __setattr__(self, name, value):
		'''
		'''
##		if name in ('__implements__',):
##			return super(ObjectWithInterface, self).__setattr__(name, value)
		if not hasattr(self, '__implements__') or self.__implements__ == None or \
				interface.iswritable(self, name) and interface.isvaluecompatible(self, name, value):
##			return super(ObjectWithInterface, self).__setattr__(name, value)
			return super(ObjectWithInterface, self).__setattr__(name, interface.getvalue(self, name, value))
		raise interface.InterfaceError, 'can\'t write value "%s" to attribute "%s".' % (value, name)
	def __delattr__(self, name):
		'''
		'''
		if not hasattr(self, '__implements__') or self.__implements__ == None or \
				interface.isdeletable(self, name):
			return super(ObjectWithInterface, self).__delattr__(name)
		raise interface.InterfaceError, 'can\'t delete attribute "%s".' % name



#----------------------------------------------AbstractInterfaceProxy---
class AbstractInterfaceProxy(proxy.AbstractProxy):
	'''

	NOTE: this was not intended for direct use...
	'''
	# NOTE: this is hardcoded in the derived classes, thus changing this
	#       is not recommended.
	# XXX is the fact of this being hardcoded good???
	__proxy_target_attr_name__ = '__source__'


#--------------------------------------------------ProxyWithInterface---
# TODO move this to pli.pattern.proxy (???)
class ProxyWithInterface(AbstractInterfaceProxy):
	'''
	'''
	__implements__ = None

	__source__ = None

	def __init__(self, source):
		'''
		'''
		self.__source__ = source
	def __getattr__(self, name):
		'''
		'''
		if not hasattr(self, '__implements__') or self.__implements__ == None or \
				interface.isreadable(self, name):
			return getattr(self.__source__, name)
		raise interface.InterfaceError, 'can\'t read attribute "%s".' % name
	def __setattr__(self, name, value):
		'''
		'''
		if name in ('__source__', '__implements__'):
			return super(ProxyWithInterface, self).__setattr__(name, value)
		if not hasattr(self, '__implements__') or self.__implements__ == None or \
				interface.iswritable(self, name) and interface.isvaluecompatible(self, name, value):
##			return setattr(self.__source__, name, value)
			source = self.__source__
			return setattr(source, name, interface.getvalue(source, name, value))
		raise interface.InterfaceError, 'can\'t write value "%s" to attribute "%s".' % (value, name)
	def __delattr__(self, name):
		'''
		'''
		if not hasattr(self, '__implements__') or self.__implements__ == None or \
				interface.isdeletable(self, name):
			delattr(self.__source__, name)
		raise interface.InterfaceError, 'can\'t delete attribute "%s".' % name
	# pli protocols...
	__help__ = classmethod(strhelp)


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
			self.__implements__ = interface
		elif hasattr(source, '__implements__'):
			self.__implements__ = source.__implements__


#---------------------------------------------RecursiveInterfaceProxy---
##!!! test...
class RecursiveInterfaceProxy(proxy.GetattrRecursiveProxyMixin, InterfaceProxy):
	'''
	'''
##	def __call__():
##		'''
##		'''
##		pass



#=======================================================================
if __name__ == '__main__':

	class O(ObjectWithInterface):
		interface.inherit(iname='IO')
		interface.add('xxx', type=int, default=0)
		interface.add('xx0', type=int, default=0)
		interface.add('xx1', type=int, default=0)
		interface.add('xx2', type=int, default=0)
		interface.add('xx3', type=int, default=0)
		interface.add('xx4', type=int, default=0)
		interface.add('xx5', type=int, default=0)
		interface.add('xx6', type=int, default=0)
		interface.add('xx7', type=int, default=0)
		interface.add('xx8', type=int, default=0)
		interface.add('xx9', type=int, default=0)

##		interface.hide('xxx')
		interface.hide('xx0')

		interface.add('*')

		def f(self):
			print '!!!'

	o = O()

	def f():
		print 'mooo!'

	o.f = f

	print '123'

	print o.xxx

	o.xxx = 123

	print o.xxx

	print hasattr(o, '__implements__')
	print hasattr(O, '__implements__')

	o.f()

	print o.__help__()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
