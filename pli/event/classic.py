#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20040421001657'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.event.event as event


#--------------------------------------------------------ClassicEvent---
class ClassicEvent(event.ClassEvent):
	'''
	this is a classic event class.
	each handler will get the event object as a single argument and all
	event data is contained in this object.

	NOTE: this is not a full fledged event, as one can not fire an object
	      of a ClassEvent... etc.
	NOTE: due to the fact that this event creates an object for each 
	      handler, it is not particularly memory efficient (plus this
		  introduces a certain overhead).
	'''
	# NOTE: for documentation on the following see the pli.event.event
	#       module...
	__eventhooks__ = None
	__inherit_source__ = False
	__strict_source__ = False
	
	def __init__(self, *p, **n):
		'''
		this will generally init the event objects' data.
		'''
		# setup default data...
		self._args = (p, n)
##		for name, val in n.iteritems():
##			setattr(self, name, val)
	def __callhook__(cls, hook, evt, *p, **n):
		'''
		this will create an event object and pass it to the handler.
		'''
		return hook(evt(*p, **n))
	__callhook__ = classmethod(__callhook__)



#=======================================================================
if __name__ == '__main__':
	# the event handler...
	def f(evt):
		print '***', evt

	# create a classic event...
	class TestEvent(ClassicEvent):
		pass

	# bind to a classic event...
	event.bind(TestEvent, f)

	# fire the test event...
	TestEvent.fire()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
