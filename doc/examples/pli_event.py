#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20060621181644'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.event as event


#-----------------------------------------------------------------------
#
# this example will illustrate the usage of the events (pli.event
# module).
#
#   here we will create a layered system in which each layer will
# register a handler for the onPing Event when it starts work, and
# unregister it when it is done.
#
#--------------------------------------------------------------onPing---
class onPing(event.ClassEvent):
	'''
	this is the event class.

	NOTE: this does not need to be instaciated.
	'''
	def fire(cls, *p, **n):
		'''
		'''
		print '\nping!!!'
##		super(cls.__metaclass__, cls).fire(*p, **n)
		super(cls.__class__, cls).fire(*p, **n)
		print


#--------------------------------------------------------------Layer---
class Layer(object):

	def handler(self, evt):
		'''
		this is the default event handler.
		'''
		print '###', evt.__name__, self.__class__.__name__

	def start(self):
		'''
		start work...
		'''
		print 'starting:', self
		event.bind(onPing, self.handler)

	def stop(self):
		'''
		stop work...
		'''
		print 'stopping:', self
		event.unbind(onPing, self.handler)


#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - Layer_A- -
class Layer_A(Layer):
	pass

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - Layer_B- -
class Layer_B(Layer):
	pass

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - Layer_C- -
class Layer_C(Layer):
	pass


#-----------------------------------------------------------------------
print 'initializing....'
layer_a = Layer_A()
layer_b = Layer_B()
layer_c = Layer_C()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

# fire the event (blank -- no handlers)
onPing.fire()


#-----------------------------------------------------------------------

print 'starting system layers...'
layer_a.start()
layer_b.start()
layer_c.start()

onPing.fire()

layer_c.stop()

onPing.fire()

layer_b.stop()

onPing.fire()

layer_a.stop()

onPing.fire()



print 'testing the count event handlers...'

def handler(evt):
	print 'handling:', evt

print 'registering handler for three fireings of event onPing.'
event.bindcount(onPing, handler, 3)
print 'registering handler for one fireing of event onPing.'
event.bindonce(onPing, handler)

onPing.fire()
onPing.fire()
onPing.fire()
onPing.fire()
onPing.fire()

print 'done.'



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
