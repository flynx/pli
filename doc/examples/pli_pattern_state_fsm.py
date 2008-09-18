#=======================================================================

__version__ = '''0.2.37'''
__sub_version__ = '''20041121151424'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

# TODO rewrite this...
import pli.pattern.state.fsm as fsm
import pli.event as event



#-----------------------------------------------------------------------

# TODO move these to unit tests...
# some basic tests...
print 'initializing:'
print 'creating an fsm...'

class FSM(fsm.FiniteStateMachine): 
	pass 


print 'creating states...'

class A(fsm.State):
	__fsm__ = FSM
	__is_initial_state__ = True

class B(fsm.State):
	__fsm__ = FSM
	def __onafterstatechange__(self):
		print 'testing an illegal transition...'
		try:
			self.changestate(A)
			raise 'Error'
		except fsm.TransitionError, msg:
			print 'got TransitionError:', msg
		print 'now the FSM will decide which transition to take...'
		super(B, self).__onafterstatechange__()

class C(fsm.State):
	__fsm__ = FSM
	__is_terminal_state__ = True


print 'defining transition predicates...'
s = []
sl = 3
def pred_B2C(o):
	global s
	if len(s) > sl:
		s += [0]
		return True
	return False
def pred_B2B(o):
	global s
	if len(s) <= sl:
		s += [0]
		return True
	return False


print 'defining transitions...'
##fsm.transition(A, B)
##fsm.transition(A, C)
fsm.transition(A, B, mode=fsm.MANUAL)
fsm.transition(A, C, mode=fsm.MANUAL)
fsm.transition(B, C, condition=pred_B2C)
fsm.transition(B, B, condition=pred_B2B)


print 'creating an fsm instance...'
mfsm = FSM()

print

print 'preparing events:'
print 'defining handler...'
def f(evt):
	print '   ****', evt.__class__.__name__, ':', evt.state_name
print 'binding events...'
event.bind(mfsm.onEnterA, f)
event.bind(mfsm.onExitA, f)
event.bind(mfsm.onEnterB, f)
event.bind(mfsm.onExitB, f)
event.bind(mfsm.onEnterC, f)
event.bind(mfsm.onExitC, f)


print

# start the FSM...
if mfsm.__auto_change_state__:
	print 'starting the fsm...'
	# NOTE: if we did not have (or would not reach) a terminal 
	#       state this will never exit...
	mfsm.start()

	if not fsm.isterminal(mfsm):
		print 'restarting FSM (on B)...'
		mfsm.changestate(B)


print
print 'testing an illegal transition...'
try:
	mfsm.changestate(FSM.__states__['B'])
	raise 'Error'
except fsm.FiniteStateMachineError, msg:
	print 'got FiniteStateMachineError:', msg

print 'testing predicates...'
print 'A is before B:', fsm.isbefore(A, B)
print 'A is before C:', fsm.isbefore(A, C)
print 'B is before A:', fsm.isbefore(B, A)
print 'B is after A:', fsm.isafter(B, A)

print

print 'done.'




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
