#=======================================================================

__version__ = '''0.1.00'''
__sub_version__ = '''20051216154923'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------
__doc__ = '''\
This module is an example usage a an almost pure FSM program. Here we 
will define a rather traditional coffee machine as an FSM.

The Coffee Machine FSM (CoffeeMachine) consistes of 8 states and 23 
transitions.

NOTE: this is an almost pure FSM, as there is one (only) condition 
	  that is checked (hidden) within a method (which is: "is there is 
	  enough sugar for the requested number of portions").


State Hierarchy:
================
                              '
    +- actual states -------+ ' +-- meta states ---------------------------------------------------------+
                              '
      CoffeeMachineOff ------ ' -------------------------- CoffeeMachineUnPowered -+
                              '                                                    |
                              '                                                    |
                              '                                                    |
      CoffeeMachineNoCoffee - ' --+                                                +- CoffeeMachineState
                              '   |                                                |
                              '   +- CoffeeMachineErr --+                          |
      CoffeeMachineNoWater -- ' --+                     |                          |
                              '   |                     |                          |
                              '   |                     |                          |
      CoffeeMachineNoSugar -- ' --+                     |                          |
                              '                         +- CoffeeMachinePowered ---+
                              '                         |
                              '                         |
      CoffeeMachineReady ---- ' ------------------------+
                              '                         |
                              '                         |
                              '                         |
      CoffeeMachineMixing --- ' --+                     |
                              '   |                     |
                              '   |                     |
      CoffeeMachineBoiling -- ' --+                     |
                              '   +- CoffeeMachineBusy -+
                              '   |
      CoffeeMachinePouring -- ' --+
                              '
                              '


The CoffeeMachine (FSM):
=======================

    +------>o CoffeeMachineOff <--------------------------------+
    |       |    (Initial)                                      |
    |       |                                                   |
 . .|. . . .|. . . . . . . . . . . . . . . . . . . . . . . . . .|. . . .
    |       |                     .                             |
    |       |                     . +->o CoffeeMachineNoCoffee -+
    |       |                     . |  |                        |
    |       |                     . |  +----------------------------+
    |       v                     . |                           |   |
    |   +-->o CoffeeMachineReady ---+                           |   |
    |   |   |                     . +->o CoffeeMachineNoWater --+   |
    |   |   |                     . |  |                        |   |
    |   |   |                     . |  +----------------------------+
    |   |   |                     . |                           |   |
    +-------+-----------+         . |                           |   |
        |   |           |         . +->o CoffeeMachineNoSugar --+   |
        |   |           |         .    |                        |   |
        |   |           +<-------------+----------------------------+
        |   |           |         .                             |   |
 . . . .|. .|. . . . . .|. . . . . . . . . . . . . . . . . . . .|. .|. .
        |   |           |                                       |   |
        |   |           v                                       |   |
        |   |           o CoffeeMachineMixing ------------------+   |
        |   |           |                                       |   |
        |   |           v                                       |   |
        |   |           o CoffeeMachineBoiling -----------------+   |
        |   |           |                                       |   |
        +<--------------+                                       |   |
        |   |           |                                       |   |
        |   +<----------+                                       |   |
        |   |                                                   |   |
        |   +<------------------------------------------------------+
        |   |                                                   |
        |   v                                                   |
        +---o CoffeeMachinePouring -----------------------------+


'''

#-----------------------------------------------------------------------

import time

import pli.pattern.state.fsm as fsm
import pli.event as event
from pli.functional import rcurry


#-----------------------------------------------------------------------

POWER = 230


#-----------------------------------------------------------------------
#-------------------------------------------------------CoffeeMachine---
class CoffeeMachine(fsm.FiniteStateMachine):
	'''
	this is the root CoffeeMachine FSM class.
	'''
	# CoffeeMachine data...
	# max capacities:
	max_water_res = 4000
	max_sugar_res = 500 
	max_coffee_res = 500

	pot_capacity = 1000
	coffee_per_pot = 50

	# portion setup:
	cup_capacity = 50
	sugar_portion = 20

	# delay times (seconds):
	pouring_time = 1
	mixing_time = 2
	boiling_time = 5

	def __init__(self, *p, **n):
		'''
		'''
		self.water = 0
		self.sugar = 0
		self.coffee = 0

		self.pot = 0

		super(CoffeeMachine, self).__init__(*p, **n)


#-----------------------------------------------------------------------
# meta states...
#--------------------------------------------------CoffeeMachineState---
class CoffeeMachineState(fsm.State):
	'''
	'''
	__fsm__ = CoffeeMachine
	__ignore_registration__ = True

	# CoffeeMachine active interface...
	def loadsugar(self, quantity):
		'''
		'''
		total = self.sugar + quantity
		res = 0
		if total > self.max_sugar_res:
			self.sugar = self.max_sugar_res
			res = total - self.max_sugar_res 
		else:
			self.sugar = total
		return res
	def loadwater(self, quantity):
		'''
		'''
		total = self.water + quantity
		res = 0
		if total > self.max_water_res:
			self.water = self.max_water_res
			res = total - self.max_water_res 
		else:
			self.water = total
		return res
	def loadcoffee(self, quantity):
		'''
		'''
		total = self.coffee + quantity
		res = 0
		if total > self.max_coffee_res:
			self.coffee = self.max_coffee_res
			res = total - self.max_coffee_res 
		else:
			self.coffee = total
		return res
	def pourcup(self):
		'''
		'''
		pass
	def preparecoffee(self):
		'''
		'''
		pass
	def toglepower(self):
		'''
		'''
		raise NotImplementedError
	# CoffeeMachine readouts and sensors...
	def hassugar(self):
		'''
		'''
		pass
	def haswater(self):
		'''
		'''
		pass
	def hascoffee(self):
		'''
		'''
		pass
	def haspower(self):
		'''
		'''
		return 210 <= POWER <= 260


#----------------------------------------------CoffeeMachineUnPowered---
class CoffeeMachineUnPowered(CoffeeMachineState):
	'''
	'''
	__ignore_registration__ = True

	def toglepower(self):
		'''
		'''
		self.changestate(CoffeeMachineReady)


#------------------------------------------------CoffeeMachinePowered---
class CoffeeMachinePowered(CoffeeMachineState):
	'''
	'''
	__ignore_registration__ = True

	def loadsugar(self, quantity):
		'''
		'''
		res = super(CoffeeMachinePowered, self).loadsugar(quantity)
		self.changestate(CoffeeMachineReady)
		return res
	def loadwater(self, quantity):
		'''
		'''
		res = super(CoffeeMachinePowered, self).loadwater(quantity)
		self.changestate(CoffeeMachineReady)
		return res
	def loadcoffee(self, quantity):
		'''
		'''
		res = super(CoffeeMachinePowered, self).loadcoffee(quantity)
		self.changestate(CoffeeMachineReady)
		return res
	def preparecoffee(self):
		'''
		'''
		# TODO move the following three lines to the mixing state...
		self.pot = self.pot_capacity
		self.water -= self.pot_capacity
		self.coffee -= self.coffee_per_pot

		self.changestate(CoffeeMachineMixing)
	def pourcup(self, sugar=0):
		'''
		'''
		if sugar < 0:
			sugar = 0
		if self.pot < self.cup_capacity:
			self.preparecoffee()
		sugar = sugar*self.sugar_portion
		# check if we have enough sugar...
		if self.sugar < sugar:
			raise Exception, 'not enough sugar...'
		self.sugar -= sugar
		self.pot -= self.cup_capacity
		self.changestate(CoffeeMachinePouring)
	def toglepower(self):
		'''
		'''
		self.changestate(CoffeeMachineOff)
	# the sensors are digital, thus they need power to work...
	def hassugar(self):
		'''
		'''
		return self.sugar >= self.sugar_portion
	def haswater(self):
		'''
		'''
		return self.water >= self.pot_capacity
	def hascoffee(self):
		'''
		'''
		return self.coffee >= self.coffee_per_pot


#----------------------------------------------------CoffeeMachineErr---
class CoffeeMachineErr(CoffeeMachinePowered):
	'''
	'''
	__ignore_registration__ = True


#---------------------------------------------------CoffeeMachineBusy---
class CoffeeMachineBusy(CoffeeMachinePowered):
	'''
	'''
	__ignore_registration__ = True



#-----------------------------------------------------------------------
# actual states...
#----------------------------------------------------CoffeeMachineOff---
class CoffeeMachineOff(CoffeeMachineUnPowered, fsm.InitialState):
	'''
	'''
	pass


#-----------------------------------------------CoffeeMachineNoCoffee---
class CoffeeMachineNoCoffee(CoffeeMachineErr):
	'''
	'''
	def preparecoffee(self):
		'''
		'''
		raise Exception, 'No Coffee...'
	

#------------------------------------------------CoffeeMachineNoWater---
class CoffeeMachineNoWater(CoffeeMachineErr):
	'''
	'''
	def preparecoffee(self):
		'''
		'''
		raise Exception, 'No Water...'
	

#------------------------------------------------CoffeeMachineNoSugar---
class CoffeeMachineNoSugar(CoffeeMachineErr):
	'''
	'''
	def pourcup(self, sugar=0):
		'''
		'''
		if sugar == 0:
			return super(CoffeeMachineErr, self).pourcup()
		raise Exception, 'No Sugar...'
	

#--------------------------------------------------CoffeeMachineReady---
class CoffeeMachineReady(CoffeeMachinePowered):
	'''
	'''
	pass


#------------------------------------------------CoffeeMachineBoiling---
class CoffeeMachineBoiling(CoffeeMachineBusy):
	'''
	'''
	def __onafterstatechange__(self):
		'''
		'''
		time.sleep(self.boiling_time)
		return super(CoffeeMachineBoiling, self).__onafterstatechange__()

	def preparecoffee(self):
		'''
		'''
		pass
	def pourcup(self, sugar=0):
		'''
		'''
		pass


#-------------------------------------------------CoffeeMachineMixing---
class CoffeeMachineMixing(CoffeeMachineBusy):
	'''
	'''
	def __onafterstatechange__(self):
		'''
		'''
		time.sleep(self.mixing_time)
		return super(CoffeeMachineMixing, self).__onafterstatechange__()

	def preparecoffee(self):
		'''
		'''
		pass
	def pourcup(self, sugar=0):
		'''
		'''
		pass


#------------------------------------------------CoffeeMachinePouring---
class CoffeeMachinePouring(CoffeeMachineBusy):
	'''
	'''
	def __onafterstatechange__(self):
		'''
		'''
		time.sleep(self.pouring_time)
		return super(CoffeeMachinePouring, self).__onafterstatechange__()

	def preparecoffee(self):
		'''
		'''
		pass
	def pourcup(self, sugar=0):
		'''
		'''
		pass



#-----------------------------------------------------------------------
# transitions...
# NOTE: if we use the non-strict transition mode then all manual
#       transitions can be omitted...
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# startup...
# manual (external actor)...
fsm.transition(CoffeeMachineOff, CoffeeMachineReady, 
									condition=lambda o: o.haspower(), 
									mode=fsm.MANUAL)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# ready to err...
# automatic...
fsm.transition(CoffeeMachineReady, CoffeeMachineNoCoffee, 
									condition=lambda o: not o.hascoffee())
fsm.transition(CoffeeMachineReady, CoffeeMachineNoWater, 
									condition=lambda o: not o.haswater())
fsm.transition(CoffeeMachineReady, CoffeeMachineNoSugar, 
									condition=lambda o: not o.hassugar())

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# make and serve...
# manual (external actor)...
fsm.transition(CoffeeMachineReady, CoffeeMachineMixing, mode=fsm.MANUAL)
fsm.transition(CoffeeMachineNoSugar, CoffeeMachineMixing, mode=fsm.MANUAL)
fsm.transition(CoffeeMachineReady, CoffeeMachinePouring, mode=fsm.MANUAL)
fsm.transition(CoffeeMachineNoCoffee, CoffeeMachinePouring, mode=fsm.MANUAL)
fsm.transition(CoffeeMachineNoWater, CoffeeMachinePouring, mode=fsm.MANUAL)
fsm.transition(CoffeeMachineNoSugar, CoffeeMachinePouring, mode=fsm.MANUAL)
# automatic...
fsm.transition(CoffeeMachineMixing, CoffeeMachineBoiling)
fsm.transition(CoffeeMachineBoiling, CoffeeMachineReady)
fsm.transition(CoffeeMachinePouring, CoffeeMachineReady)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# err to ready...
# manual (external actor)...
fsm.transition(CoffeeMachineNoCoffee, CoffeeMachineReady, mode=fsm.MANUAL)
fsm.transition(CoffeeMachineNoWater, CoffeeMachineReady, mode=fsm.MANUAL)
fsm.transition(CoffeeMachineNoSugar, CoffeeMachineReady, mode=fsm.MANUAL)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# shutdown...
# manual (external actor)...
fsm.transition(CoffeeMachineReady, CoffeeMachineOff, mode=fsm.MANUAL)
fsm.transition(CoffeeMachineNoCoffee, CoffeeMachineOff, mode=fsm.MANUAL)
fsm.transition(CoffeeMachineNoWater, CoffeeMachineOff, mode=fsm.MANUAL)
fsm.transition(CoffeeMachineNoSugar, CoffeeMachineOff, mode=fsm.MANUAL)
fsm.transition(CoffeeMachineMixing, CoffeeMachineOff, mode=fsm.MANUAL)
fsm.transition(CoffeeMachineBoiling, CoffeeMachineOff, mode=fsm.MANUAL)
fsm.transition(CoffeeMachinePouring, CoffeeMachineOff, mode=fsm.MANUAL)



#-----------------------------------------------------------------------
#-------------------------------------------------------setup_logging---
# this function is irrelevant to the example... (though it might pose
# some interest)
def setup_logging(fsm_obj, events=(), actions=(), force=False):
	'''
	'''
	def report(*p):
		print ' '.join(p)

	def s_report(evt, *p):
		print evt.state_name, ' '.join(p)
	
	# states...
	for e in events:
		event.bind(getattr(fsm_obj, e), rcurry(s_report, '...'))

	# TODO move this to the aspect module...
	# NOTE: this will log only explicit external (through the object)
	#       method access....
	def wrap_meth(obj, meth_name, pre=None, post=None, force=False):
		'''
		'''
		if not force and meth_name in vars(obj):
			raise TypeError, 'will not overwrite object data.'
		def wrapper(*p, **n):
			'''
			'''
			if pre != None:
				pre(obj, meth_name, *p, **n)
			res = getattr(super(obj.__class__, obj), meth_name)(*p, **n)
			if post != None:
				return post(obj, meth_name, res, *p, **n)
			return res
		setattr(obj, meth_name, wrapper)
	
	# actions...
	for m in actions:
		wrap_meth(fsm_obj, m, pre=lambda obj, meth, *p, **n: report('\n-->', meth, *[str(i) for i in p]), force=force)
	


#=======================================================================
if __name__ == '__main__':
	# logging data....
	actions = (
		'loadsugar', 
		'loadwater', 
		'loadcoffee', 
		'pourcup', 
		'preparecoffee', 
		'toglepower'
	)

	events = (
		'onEnterCoffeeMachineOff',
		'onEnterCoffeeMachineNoCoffee',
		'onEnterCoffeeMachineNoWater',
		'onEnterCoffeeMachineNoSugar',
		'onEnterCoffeeMachineReady',
		'onEnterCoffeeMachineMixing',
		'onEnterCoffeeMachineBoiling',
		'onEnterCoffeeMachinePouring',
	)

	# create a coffee machine...
	cm = CoffeeMachine()

	# setup logging...
	setup_logging(cm, events, actions)

	# set it up...
	cm.start()

##	POWER = 110

	# power it up....
	cm.toglepower()

	# load the thing up...
	cm.loadwater(2500)
	cm.loadcoffee(500)
	cm.loadsugar(100)

##	# and we are ready to go...
##	cm.preparecoffee()

	cups = 3

	for i in range(cups):
		cm.pourcup()

	cm.toglepower()
	cm.toglepower()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
