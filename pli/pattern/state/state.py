#=======================================================================

__version__ = '''0.1.07'''
__sub_version__ = '''20040729032326'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

__doc__ = '''\
'''


#-----------------------------------------------------------------------
#---------------------------------------------------------isstatefull---
def isstatefull(obj):
	'''
	return true if object is statefull.
	'''
	try:
		return issubclass(obj, State)
	except:
		return isinstance(obj, State)


#-------------------------------------------------------------stateof---
def stateof(obj):
	'''
	return the objects state.
	'''
	if isstatefull(obj):
		return obj.__class__
	else:
		raise TypeError, 'the object given is not statefull.'

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# legacy support...
getobjectstate = stateof


#---------------------------------------------------------------State---
# TODO make a state constructor..... (like property)
# TODO might be good to define different usage patterns for statefull
#      systems...
#
class State(object):
	'''
	this is the generic cooperative state class.

	  the general idea behind this is to provide a building block for
	creation of cooperative/linked state machines.

	  this provides the functionality for an object to change state 
	logic (not the state data), and to communicate with other *statefull*
	objects	via callbacks on state change events.

	there are two utility methods that can be defined:
		__runonce__       : this will be run only once per state, this is
		                    done to mainly register callbacks.
							NOTE: when this is run not all state objects
							      might be present, to avoid this it is 
								  recommended to use a seporate blank init
								  state first, and only after the system is
								  created to move to a valid state.
		__onstatechange__ : this is run once per state change, right after
		                    the change.
	    NOTE: both of the above methods receive no arguments but the object
		      reference.


	NOTE: this is not intended to be used directly.
	'''
	def __init__(self, *p, **n):
		'''

		this init method needs to get accessed only once per statefull object.
		'''
		self._state_callbacks = {}
		self._states = []
##		if nowait:
##			self.init()
		super(State, self).__init__(*p, **n)
	def init(self):
		'''
		this should init the system...
		
		NOTE: this is contagious, that is, it will init all dependencies.
		NOTE: this functionality is achieved through the "notify_on" protocol, 
		      thus other dependencies will not get checked.
		'''
		# this may need to get called later... (as there may be
		# unresolved dependency issues before all objects are created).
		if self.__class__ not in self._states and hasattr(self, '__runonce__'):
			self._states += [self.__class__]
			try:
				self.__runonce__()
			except (NameError, AttributeError):
				# there was an unresolved dep. (try to run this later)
				##!!!
				pass
	# the following two methods are here for documentation reasons...
	#                                   (see the classes doc string...)
	# TODO remane to "__initstate__"...
##	def __runonce__(self):
##		'''
##
##		this method is run once per state.
##		    (each unique state will run this method only once per object).
##
##		this may generally be used to setup notifications...
##		'''
##		pass
##	def __onstatechange__(self):
##		'''
##
##		this method is to be run once per state change (just after the change).
##		'''
##		pass
	def _callback(self, obj, fromstate, tostate):
		'''
		this is the default callback.
		'''
		pass
	def changestate(self, tostate):
		'''
		change state and notify all registered of changes.
		'''
		fromstate = self.__class__
		# change state...
		self.__class__ = tostate
		# run util methods...
		self.init() # this might be a bit slow....
		if hasattr(self, '__onstatechange__'):
			self.__onstatechange__()
		# notify others... 
		calls = []
		for state in (fromstate, tostate), (None, tostate), (fromstate, None), (None, None):
			# check for issubclass (might use dispatch...)
			if state in self._state_callbacks:
				calls += self._state_callbacks[state]
		for call in calls:
			# call only if we ignore the targets state or it matches
			# its state on notify registration.
			if call[1] in (call[2].__class__, None) and (call[3] == None or call[3](self)):
				call[0](self, fromstate, tostate)
	# TODO move this to a seporate class.... (???)
	def notify_on(self, obj, fromstate=None, tostate=None, ignore_self_state=1, callback=None, predicate=None):
		'''
		register for notification.

		the default is monitor all state changes of the obj.

		if ignore_self_state is not set the notification will execute only if the
		object that waiting for notification is in the same state as when it registered.
		'''
		# init the obj...
		obj.init()
		if callback == None:
			callback = self._callback
		if ignore_self_state:
			self_state = None
		else:
			self_state = self.__class__
		if (fromstate, tostate) not in obj._state_callbacks:
			obj._state_callbacks[(fromstate, tostate)] = ((callback, self_state, self, predicate),)
		else:
			obj._state_callbacks[(fromstate, tostate)] += ((callback, self_state, self, predicate),)



#=======================================================================
#                                            vim:set sw=4 ts=4 nowrap :
