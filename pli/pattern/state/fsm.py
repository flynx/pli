#=======================================================================

__version__ = '''0.2.17'''
__sub_version__ = '''20040317151209'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

__doc__ = '''\
This module defines a Finite State Machine framework.
'''


#-----------------------------------------------------------------------

import pli.pattern.store.stored as stored
import pli.event.instanceevent as instanceevent

import state



#-----------------------------------------------------------------------
#---------------------------------------------FiniteStateMachineError---
# TODO write more docs...
class FiniteStateMachineError(Exception):
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
# TODO make manual state changes non-recursive (e.g. first exit of
#      cotext and then change)...
#      moght be good to add directivs/options to auto change or select
#      next state...
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
	terurn True if s2 is reachable from s1.
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
	terurn True if s1 is reachable from s2.
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
	terurn true if s is inside a loop (e.g. s is reachable from s)
	'''
	return isbefore(s, s)



#----------------------------------------------------------transition---
# TODO add support for string state names... (+ check consistency... (?))
# TODO add transition predicate...
def transition(s1, s2, predicate=None):
	'''
	create a transition from s1 to s2.
	'''
	if not isterminal(s1):
		s1.transition(s2)
	else:
		raise FiniteStateMachineError, 'can\'t add transition to a terminal state %s.' % s1


#-----------------------------------------------------------------------
#--------------------------------------------------------onEnterState---
# TODO write more docs...
class onEnterState(instanceevent.Event):
	'''
	'''
	def __init__(self, state_name):
		'''
		'''
		self.state_name = state_name
		super(onEnterState, self).__init__()


#---------------------------------------------------------onExitState---
# TODO write more docs...
class onExitState(instanceevent.Event):
	'''
	'''
	def __init__(self, state_name):
		'''
		'''
		self.state_name = state_name
		super(onExitState, self).__init__()


#--------------------------------------------------FiniteStateMachine---
# WARNING: this has not been tested for being thread-safe...
# NOTE: whole FSMs can not (yet) be reprodused by deep copying... (not
#       tested)
# TODO test for safty of parallel execution of two fsm instances...
# TODO write more docs...
class FiniteStateMachine(state.State):
	'''
	this is the base FSM class.

	this acts as a collection of states.

	if an initial state is defined for an FSM the instance of 
	FiniteStateMachine will change state to the initial 
	state on init.
	'''
	# class cofiguration:
	# these will define the state enter/exit event constructors..
	__state_enter_event__ = onEnterState
	__state_exit_event__ = onExitState
	# if this is set, all statechanges without transitions will be
	# blocked (e.g. raise an exception)...
	__strict_transitions__ = True
	# this will enable automatic state changing...
	__auto_change_state__ = True
	# this will define the state to which we will autochange...
	__next_state__ = None

	# class data:
	__states__ = None
	__initial_state__ = None

	def __init__(self):
		'''
		'''
		super(FiniteStateMachine, self).__init__()
		# init all states...
		self.initstates()
		# change state to the initial state if one defined...
		if hasattr(self, '__initial_state__') and self.__initial_state__ != None:
			self.changestate(self.__initial_state__)
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
			while True:
				# break on terminal state...
				if isterminal(self):
					break
				if self.__next_state__ != None:
					# change state...
					tostate = self.__next_state__
					self.__next_state__ = None
					self._changestate(tostate)
			self._running = False
		else:
			raise FiniteStateMachineError, 'can\'t start a manual (non-auto-change-state) FSM.'
	# TODO ignore enter events of initial state and exit events of
	#      terminal states... (as these will never (?) be used)
	#      (???)...
	#      this might also be solved by calling the initial enter event
	#      just before __runonce__ and the termonal exit event just
	#      after the __onchangestate__...
	# TODO automaticly init newly added states per FSM object on their
	#      (event) addition to the FSM class...
	#      ...or do a laizy init (as in RPG.action)
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


#--------------------------------------------------------------_State---
class _StoredState(stored._StoredClass):
	'''
	this meta-class will register the state classes with the FSM.
	'''
	# _StoredClass cofiguration:
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
class State(FiniteStateMachine):
	'''
	this is the base state class for the FSM framwork.	

	there are three utility methods that can be defined:
		__runonce__			: this will be run only once per state, this is
							  done to mainly register callbacks.
		__onstatechange__	: this is run once per state change, right after
							  the change is made and just before the onEnter  
							  event is fired.
		__onafterstatechange__
							: this is called after the state is finalized.
							  that is just after the state onEnter event 
							  processing is done.
		NOTE: all of the above methods receive no arguments but the object
			  reference.

	on state istance creation, two events will get defined and added to the FSM:
		onEnter<state-name> : this is fired on state change, just after the 
							  __onstatechange__ method is finished.
		onExit<state-anme>	: this is fired just befor the state is changed.

	for more information see: pli.pattren.state.State

	'''
	__metaclass__ = _StoredState

	# class cofiguration:
	# this is the class of fsm this state will belong to
	__fsm__ = None
	# if this is set the state will be registered as initial/start state
	__is_initial_state__ = False
	# if this is set the state will be registered as terminal/end state
	__is_terminal_state__ = False

	# StoredClass options:
	# do not register this class... (not inherited)
	__ignore_registration__ = True
	# auto register  all subclasses (inherited)
	__auto_register_type__ = True

	# class data:
	# TODO make this a dict....
	__next_states__ = None

	# TODO add support for string state names... (+ check consistency... (?))
	# TODO write a "removetransition" method....
	# TODO add transition predicate...
	def transition(cls, tostate, predicate=None):
		'''
		this will create a transition from the current state to the tostate.
		'''
		# process self...
		if not hasattr(cls, '__next_states__') or cls.__next_states__ == None:
			cls.__next_states__ = [tostate]
		else:
			cls.__next_states__ += [tostate]
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
				(not hasattr(self, '__next_states__') or self.__next_states__ == None or \
				tostate not in self.__next_states__):
			raise TransitionError, 'can\'t change state of %s to %s without a transition.' % (self, tostate)
		# change the state...
		super(State, self).changestate(tostate)
	def iternextstates(self):
		'''
		this will iterate through the states directly reachable from 
		self (e.g. to which there are direct transitions).
		'''
		if self.__next_states__ == None:
			return
		for n in self.__next_states__: 
			yield n
	iternextstates = classmethod(iternextstates)
	# this is here for documentation...
##	def __onafterstatechange__(self):
##		'''
##		this method is called after the state is finalized (e.g. after the
##		__onstatechange__ is called and the onEnter event is processed).
##		'''
##		pass



#=======================================================================
# TODO move these to unit tests...
# some basic tests...
if __name__ == '__main__':
	print 'initializing:'
	print 'creating an fsm...'

	class FSM(FiniteStateMachine): 
		pass 
	
	print 'creating states...'

	class A(State):
		__fsm__ = FSM
		__is_initial_state__ = True
		def __onafterstatechange__(self):
			self.changestate(B)

	class B(State):
		__fsm__ = FSM
		def __onafterstatechange__(self):
			print 'testing an illegal transition...'
			try:
				self.changestate(A)
				raise 'Error'
			except TransitionError, msg:
				print 'got TransitionError:', msg
			self.changestate(C)

	class C(State):
		__fsm__ = FSM
		__is_terminal_state__ = True
##		def __onafterstatechange__(self):
##			self.changestate(B)
	
	print 'defining transitions...'
	transition(A, B)
	transition(A, C)
	transition(B, C)

	print 'creating an fsm instance...'
	fsm = FSM()

	print

	print 'preparing events:'
	print 'defining handler...'
	def f(evt):
		print '   ****', evt.__class__.__name__, ':', evt.state_name
	print 'binding events...'
	instanceevent.bind(fsm.onEnterA, f)
	instanceevent.bind(fsm.onExitA, f)
	instanceevent.bind(fsm.onEnterB, f)
	instanceevent.bind(fsm.onExitB, f)
	instanceevent.bind(fsm.onEnterC, f)
	instanceevent.bind(fsm.onExitC, f)
	
	print

	# start the FSM...
	if fsm.__auto_change_state__:
		print 'starting the fsm...'
		# NOTE: if we did not have (or would not reach) a terminal 
		#       state this will never exit...
		fsm.start()


	print

	print 'testing an illegal transition...'
	try:
		fsm.changestate(FSM.__states__['B'])
		raise 'Error'
	except FiniteStateMachineError, msg:
		print 'got FiniteStateMachineError:', msg

	print 'testing predicates...'
	print 'A is before B:', isbefore(A, B)
	print 'A is before C:', isbefore(A, C)
	print 'B is before A:', isbefore(B, A)
	print 'B is after A:', isafter(B, A)

	print

	print 'done.'


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
