#=======================================================================

__version__ = '''0.3.17'''
__sub_version__ = '''20040802180146'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

__doc__ = '''\
This module defines a Finite State Machine framework.
'''


#-----------------------------------------------------------------------

import pli.pattern.store.stored as stored
import pli.event as event
##import pli.event.instanceevent as instanceevent

import state


#-----------------------------------------------------------------------
#---------------------------------------------FiniteStateMachineError---
# TODO write more docs...
class FiniteStateMachineError(Exception):
	'''
	'''


#----------------------------------------------FiniteStateMachineStop---
class FiniteStateMachineStop(Exception):
	'''
	'''


#-----------------------------------------------------TransitionError---
# TODO write more docs...
class TransitionError(FiniteStateMachineError):
	'''
	'''



#-----------------------------------------------------------------------
# TODO consistency checks...
# TODO more thorough documentation...
#-----------------------------------------------------------------------
# predicates based on transitions:
#-----------------------------------------------------------isinitial---
def isinitial(s):
	'''
	return True is s is the initial state of an FSM.
	'''
	return hasattr(s, '__is_initial_state__') and s.__is_initial_state__


#----------------------------------------------------------isterminal---
def isterminal(s):
	'''
	return True is s is a terminal state in an FSM.
	'''
	return hasattr(s, '__is_terminal_state__') and s.__is_terminal_state__


#--------------------------------------------------------------isnext---
def isnext(s1, s2):
	'''
	return True if there is a direct transition from s1 to s2.
	'''
	return s2 in s1.iternextstates()


#--------------------------------------------------------------isprev---
def isprev(s1, s2):
	'''
	return True if there is a direct transition from s2 to s1.
	'''
	return isnext(s2, s1)


#------------------------------------------------------------isbefore---
# TODO make an iterative version...
# TODO might be good to make a breadth-first version...
def isbefore(s1, s2, exclude=None):
	'''
	return True if s2 is reachable from s1.
	'''
	if exclude == None:
		exclude = []
	# this is depth first...
	for n in [s1] + list(s1.iternextstates()):
		if n not in exclude and (isnext(n, s2) or isbefore(n, s2, exclude=exclude+[n])):
			return True
	return False


#-------------------------------------------------------------isafter---
def isafter(s1, s2):
	'''
	return True if s1 is reachable from s2.
	'''
	return isbefore(s2, s1)


#-----------------------------------------------------------isbetween---
def isbetween(s1, s2, s3):
	'''
	return True if s1 is reachable from s2 and s3 is reachable from s1 (e.g. s1 is between s2 and s3).
	'''
	return isbefore(s2, s1) and isbefore(s1, s3)


#------------------------------------------------------------isonpath---
def isonpath(s1, s2, s3, *p):
	'''
	return True if s2 is reachable from s1 and s3 from s2 ... sN from sN-1.
	'''
	r = (s1, s2, s3) + p
	for i, n in enumerate(p[1:-1]):
		if not isbetween(n, p[i], p[i+2]):
			return False
	return True


#------------------------------------------------------------isinloop---
def isinloop(s):
	'''
	return true if s is inside a loop (e.g. s is reachable from s)
	'''
	return isbefore(s, s)



#----------------------------------------------------------transition---
# TODO add support for string state names... (+ check consistency... (?))
# TODO add doc paramiter to transitions...
def transition(s1, s2, condition=None):
	'''
	create a transition from s1 to s2.
	'''
	if not isterminal(s1):
		s1.transition(s2, condition)
	else:
		raise FiniteStateMachineError, 'can\'t add transition to a terminal state %s.' % s1


#-----------------------------------------------------------------------
#--------------------------------------------------------onEnterState---
# TODO write more docs...
class onEnterState(event.InstanceEvent):
	'''
	'''
	__suppress_exceptions__ = False

	def __init__(self, state_name):
		'''
		'''
		self.state_name = state_name
		super(onEnterState, self).__init__()


#---------------------------------------------------------onExitState---
# TODO write more docs...
class onExitState(event.InstanceEvent):
	'''
	'''
	__suppress_exceptions__ = False

	def __init__(self, state_name):
		'''
		'''
		self.state_name = state_name
		super(onExitState, self).__init__()


#--------------------------------------------onFiniteStateMachineStop---
class onFiniteStateMachineStop(event.InstanceEvent):
	'''
	'''
	__suppress_exceptions__ = False

	def __init__(self, state_name=None, fsm=None):
		'''
		'''
		self.state_name = state_name
		# XXX this is a cyclic reference....
		if fsm != None:
			self.fsm= fsm
		super(onFiniteStateMachineStop, self).__init__()


#--------------------------------------------------FiniteStateMachine---
# WARNING: this has not been tested for being thread-safe...
# NOTE: whole FSMs can not (yet) be reproduced by deep copying... (not
#       tested)
# TODO test for safety of parallel execution of two fsm instances...
# TODO write more docs...
# TODO error state handler...
# TODO "Sub-FSMs"
#
# TODO name resolution through the fsm.... (as a default to the startup
#      state...)
#      this should look like the FSM subclass is mixed-in (or a
#      superclass of every state) to the originil FSM, yet not touching
#      the original...
#
class FiniteStateMachine(state.State):
	'''
	this is the base FSM class.

	this acts as a collection of states.

	if an initial state is defined for an FSM the instance of 
	FiniteStateMachine will change state to the initial 
	state on init.
	'''
	# class configuration:
	# these will define the state enter/exit event constructors..
	__state_enter_event__ = onEnterState
	__state_exit_event__ = onExitState
	# if this is set, all state changes without transitions will be
	# blocked (e.g. raise an exception)...
	__strict_transitions__ = True
	# this will enable automatic state changing...
	__auto_change_state__ = True
	# this will define the state to which we will auto-change...
	__next_state__ = None

	# class data:
	__states__ = None
	__initial_state__ = None
	_stop_exception = None
	_stop_reason = None

	# this is the super safe version of init.... (incase w mix the
	# incompatible classes....)
	def __init__(self, *p, **n):
		'''
		'''
		# super-safe...
		super(FiniteStateMachine, self).__init__(*p, **n)
		# init all states...
		self.initstates()
		# store a ref to the original startup class....
		# NOTE: this is an instance attribute! (might pose a problem on
		#       serializatio....)
		self.__startup_class__ = self.__class__
		# change state to the initial state if one defined...
		if hasattr(self, '__initial_state__') and self.__initial_state__ != None:
			self.changestate(self.__initial_state__)
		# create a general fsm stop event...
		self.onFiniteStateMachineStop = onFiniteStateMachineStop(fsm=self)
	def start(self):
		'''
		this is the FSM main loop.
		'''
##		# sanity checks...
##		if not hasattr(self, '__fsm__'):
##			raise FiniteStateMachineError, 'can\'t start a raw FSM object (change to a valid state).'
		# start the loop...
		if hasattr(self, '__auto_change_state__') and self.__auto_change_state__:
			if hasattr(self, '_running') and not self._running:
				raise FiniteStateMachineError, 'the %s FSM is already running.' % self
			self._running = True
			try:
				while True:
					# break on terminal state...
					if isterminal(self):
						# fire the state stop event...
						evt_name = 'onStop' + self.__class__.__name__
						if hasattr(self, evt_name):
							getattr(self, evt_name).fire()
						# exit...
						break
##					# handle stops...
##					if self._running == False:
##						if self._stop_exception != None:
##							raise self._stop_exception, self._stop_reason
##						return self._stop_reason
					if self.__next_state__ != None:
						# change state...
						tostate = self.__next_state__
						self.__next_state__ = None
						self._changestate(tostate)
			except FiniteStateMachineStop:
				pass
			self._running = False
			# fire the fsm stop event...
			self.onFiniteStateMachineStop.fire()
		else:
			raise FiniteStateMachineError, 'can\'t start a manual (non-auto-change-state) FSM.'
##	def stop(self, reason=None, exception=None):
##		'''
##		'''
##		self._stop_exception = exception
##		self._stop_reason = reason
##		self._running = False
	# TODO automaticly init newly added states per FSM object on their
	#      (event) addition to the FSM class...
	#      ...or do a lazy init (as in RPG.action)
	#      actually the best thing would be to do both...
	def initstates(self):
		'''
		this will init state event.

		NOTE: it is safe to run this more than once (though this might not be very fast).
		'''
		# init all states...
		for state in self.__states__.values():
			state_name = state.__name__
			for evt_name, evt_cls in (('onEnter' + state_name, self.__state_enter_event__),
									  ('onExit' + state_name, self.__state_exit_event__)): 
				if not hasattr(self, evt_name):
					setattr(self, evt_name, evt_cls(state_name))
			# the stop event...
			if isterminal(state):
				setattr(self, 'onStop' + state_name, onFiniteStateMachineStop(state_name))
	def changestate(self, tostate):
		'''
		'''
		if hasattr(self, '__auto_change_state__') and self.__auto_change_state__:
			self.__next_state__ = tostate
		else:
			self._changestate(tostate)
	def _changestate(self, tostate):
		'''
		'''
		# call the __onexitstate__...
		if hasattr(self, '__onexitstate__'):
			self.__onexitstate__()
		# fire the exit event...
		evt_name = 'onExit' + self.__class__.__name__
		if hasattr(self, evt_name):
			getattr(self, evt_name).fire()
		# change the state...
		super(FiniteStateMachine, self).changestate(tostate)
		# fire the enter event...
		evt_name = 'onEnter' + self.__class__.__name__
		if hasattr(self, evt_name):
			getattr(self, evt_name).fire()
		# run the post init method...
		if hasattr(self, '__onafterstatechange__'):
			self.__onafterstatechange__()
		if hasattr(self, '__onenterstate__'):
			self.__onenterstate__()


#--------------------------------------------------------------_State---
class _StoredState(stored._StoredClass):
	'''
	this meta-class will register the state classes with the FSM.
	'''
	# _StoredClass configuration:
	__class_store_attr_name__ = '__fsm__'

	def storeclass(cls, name, state):
		'''
		register the state with the FSM.
		'''
		fsm = getattr(cls, cls.__class_store_attr_name__)
		# check state name...
		if hasattr(fsm, name):
			raise NameError, 'state named "%s" already exists.' % name
		# register the state...
		if fsm.__states__ == None:
			fsm.__states__ = {name: state}
		else:
			fsm.__states__[name] = state
		# set the fsm initial state...
		if hasattr(state, '__is_initial_state__') and state.__is_initial_state__:
			if hasattr(fsm, '__initial_state__') and fsm.__initial_state__ != None:
				raise FiniteStateMachineError, 'an initial state is already defined for the %s FSM.' % fsm
			fsm.__initial_state__ = state


#---------------------------------------------------------------State---
# TODO write more docs...
# TODO add doc paramiter to transitions...
# TODO error state handler...
# TODO "Sub-FSMs"
# TODO revise magic method names and function...
class State(FiniteStateMachine):
	'''
	this is the base state class for the FSM framwork.	

	there are three utility methods that can be defined:
		__runonce__			: this will be run only once per state, this is
							  done mainly to register callbacks.
		__onstatechange__	: this is run once per state change, right after
							  the change is made and just before the onEnter  
							  event is fired.
		__onafterstatechange__
							: this is called after the state is finalized.
							  that is, just after the state onEnter event 
							  processing is done.
							  NOTE: by default, this will select the first 
									usable transition and use it to change
									state.
		__onenterstate__	: this is called once per state change, just after 
							  the onEnter event is fired.
							  NOTE: this is fired after the __onafterstatechange__
							        method, and does NOTHING by default.
		__onexitstate__		: this is called once per state change, just before
							  the change and before the onExit event is fired.
		__resolvestatechange__
							: this is called by the above method if no usable
							  transition was found and current state is not 
							  terminal.
		NOTE: all of the above methods receive no arguments but the object
			  reference (e.g. self).

	on state instance creation, two events will get defined and added to the FSM:
		onEnter<state-name> : this is fired on state change, just after the 
							  __onstatechange__ method is finished.
		onExit<state-name>	: this is fired just before the state is changed, 
							  just after the __onexitstate__ is done.

	for more information see: pli.pattern.state.State

	'''
	__metaclass__ = _StoredState

	# class configuration:
	# this is the class of fsm this state will belong to
	__fsm__ = None
	# if this is set the state will be registered as initial/start state
	__is_initial_state__ = False
	# if this is set the state will be registered as terminal/end state
	__is_terminal_state__ = False

##	##!!! not yet implemmented section....
##	# Error Handling setop options:
##	# this will enable/disable the error case exit mechanism...
##	__error_exit_enabled__ = False
##	# if this is set, the value will be used a an error case exit from
##	# this state...
##	__error_state__ = None
##	# if this is true, this state will be used as the default error
##	# exit for the fsm...
##	# NOTE: there may be only one default error exit.
##	__is_default_error_state__ = False

	# StoredClass options:
	# do not register this class... (not inherited)
	__ignore_registration__ = True
	# auto register  all subclasses (inherited)
	__auto_register_type__ = True

	# class data:
	_transitions = None

	# TODO add support for string state names... (+ check consistency... (?))
	# TODO write a "removetransition" method....
	def transition(cls, tostate, condition=None):
		'''
		this will create a transition from the current state to the tostate.
		'''
		transitions = cls._transitions
		if transitions == None:
			transitions = cls._transitions = {tostate: condition}
##		elif tostate in transitions:
##			raise TransitionError, 'a transition from %s to %s already exists.' % (cls, tostate)
		else:
			cls._transitions[tostate] = condition
	transition = classmethod(transition)
	def changestate(self, tostate):
		'''
		change the object stete
		'''
		# prevent moving out of a terminal state...
		if hasattr(self, '__is_terminal_state__') and self.__is_terminal_state__:
			raise FiniteStateMachineError, 'can\'t change state of a terminal FSM node %s.' % self
		fsm = self.__fsm__
		# check for transitions...
		if hasattr(fsm, '__strict_transitions__') and fsm.__strict_transitions__ and \
				(not hasattr(self, '_transitions') or self._transitions == None or \
				tostate not in self._transitions):
			raise TransitionError, 'can\'t change state of %s to state %s without a transition.' % (self, tostate)
		# check condition...
		transitions = self._transitions
		if transitions[tostate] != None and not transitions[tostate](self):
			raise TransitionError, 'conditional transition from %s to state %s failed.' % (self, tostate)
		super(State, self).changestate(tostate)
	def iternextstates(self):
		'''
		this will iterate through the states directly reachable from 
		self (e.g. to which there are direct transitions).
		'''
		if self._transitions == None:
			return
		for n in self._transitions: 
			yield n
	iternextstates = classmethod(iternextstates)
	# this method is called after the state is finalized (e.g. after the
	# __onstatechange__ is called and the onEnter event is processed).
	def __onafterstatechange__(self):
		'''
		this will try to next change state.
		'''
		if hasattr(self, '__auto_change_state__') and self.__auto_change_state__:
			if self._transitions != None:
				for tostate in self._transitions:
					try:
						self.changestate(tostate)
						return
					except:
						##!!!
						pass
			if not hasattr(self, '__is_terminal_state__') or not self.__is_terminal_state__:
				if hasattr(self, '__resolvestatechange__'):
					# try to save the day and call the resolve method...
					return self.__resolvestatechange__()
				raise FiniteStateMachineError, 'can\'t exit a non-terminal state %s.' % self
	# this is here for documentation...
##	def __resolvestatechange__(self):
##		'''
##		this is called if no transition from current state is found, to 
##		resolve the situation.
##		'''
##		pass
	# Q: does this need to be __gatattr__ or __getattribute__ ????
	def __getattr__(self, name):
		'''
		this will proxy the attr access to the original startup class....
		'''
		##!!! check for looping searching !!!##
		# get the name in the startup class...
		try:
			return getattr(self.__startup_class__, name)
		except AttributeError:
			raise AttributeError, '%s object has no attribute "%s"' % (self, name)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
