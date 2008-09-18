#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20071005164813'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.interface as interface


#-----------------------------------------------------------------------
# the first example is rather simple and straight forward...

# first we create an interface...
class IExample(interface.Interface):
	__format__ = {
	#	attr-name	props
		'aaa'		: {
						'readable'	: True,
						'writable'	: False,
						'essential'	: True,
						'doc'		: 'this is an example attr doc...',
					  },
		'bbb'		: {
						'type'		: str,
						'writable'	: True,
						# BTW even LIKE loops are supported as long as
						# they create no conflicts (a typical conflict
						# is inconsistent data declorations across
						# several nodes in a loop, thus making it
						# impossible to determine the correct value for
						# a property...)
						'LIKE'		: 'aaa',
					  },
		'*'			: {
						'predicate'	: lambda value: value is not None,
					  },
	}

# second we create an interface proxy...
class IExampleProxy(interface.InterfaceProxy):
	# we say what interface we comply to....
##	__implemments__ = IExample
	interface.implements(IExample)


# now we just create some class and object.... (in this use-case it
# this class and objec actually do not even need to know a thing about
# interfaces...)
# NOTE: the resemblance to the interface here is not important..
class A(object):
	aaa = 123
	bbb = 321
	ccc = None

a = A()

# here we create a proxy...
proxy2a = IExampleProxy(a)

# now we play with the data... :)
print 'the proxy docs:'
print '\n'.join([ '  %s: %s' % (n, d) for n, d in interface.getdoc(proxy2a).items() ])

print 

proxy2a.bbb = 'some stirng...'
print 'the value of a.bbb is now', a.bbb


try:
	print 'writing 123 to proxy2a.bbb:',
	proxy2a.bbb = 123
	print 'done.'
except Exception, e:
	print 'oops! could not write int to proxy2a.bbb!! :)'
	print '              got error:', e

print 

print 'now we write the value directly to a.bbb:',
a.bbb = 0
print 'done ( a.bbb =', a.bbb, ').'
print '                  and just in case... proxy2a.bbb =', proxy2a.bbb

print 

print 'an atempt to write to proxy2a.xxx:',
proxy2a.xxx = 'some value...'
print 'done ( a.xxx is', a.xxx, ').'

print 

try:
	print 'writing None to proxy2a.yyy:',
	proxy2a.yyy = None
	print 'done.'
except Exception, e:
	print 'oops! could not write None to proxy2a.yyy!!'
	print '              got error:', e


print 
print 


#-----------------------------------------------------------------------
# in this case we will generate the interface by example...
# NOTE: some aspects of this section might change...

import pli.interface.constructor as constructor

# create/get some class...
class SomeClass(object):
	'''
	'''
	def __init__(self):
		'''
		'''
		self.b = 123
	def meth(self, a=0):
		'''
		'''
		print '>>> a =', a
		print '>>> self.b =', self.b

# there are actually two approaches here:
# 1) create an interface from the class.
# 	 NOTE: this will prevent access to all instance data not defined in
# 	 	   the class its self...
# 2) create an interface from the object.
#
# NOTE: due to the nature of python we could create both an interface
#       for a class and an object, thus controling any level of
#       definition....
o = SomeClass()

# create the inteface...
ISomeObject = constructor.obj2interface(o, methods_writable=True)

# now we create an interface proxy...
class ISomeObjectProxy(interface.InterfaceProxy):
	# we say what interface we comply to....
	__implements__ = ISomeObject

# and it is usable... :)
p = ISomeObjectProxy(o)

p.b = 321
p.meth()

def f(self, a=0):
	'''
	'''
	pass

def ff(a=0):
	'''
	'''
	print '!!!', a

p.meth = ff

p.meth(123)
o.meth(321)


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
