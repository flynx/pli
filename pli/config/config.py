#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20040321184607'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.pattern.store.stored as stored
import pli.pattern.state.fsm as fsm
import pli.event as event
import pli.event.instanceevent as instanceevent
##import pli.dispatch as dispatch

from pli.pattern.state.fsm import transition


#-----------------------------------------------------------------------
# Concepts:
# 	Config
# 	State
# 	Rule
# 	Event (pli.event)
#
# Components:
# 	State
# 		- set of events
# 	Config
# 		- collection of rules
# 		- collection of states (state classes)
# 	Rule
# 		- registration routeen
# 		- condition/rule code
# 		- reaction code
#
#
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# Typical Composition:
# 	System Composition:
# 		- config
# 		- FSM
# 		- events
# 		- rules
# 	Compnent Composition:
# 		- sub-config (???)
# 		- FSM
# 		- events
# 		- rules
# 			- dependency rules.
# 			- abstract compositional rules (define how the component
# 			  is to be built-into the system).
# 			- internal rules (used by sub componenets).
#
#-----------------------------------------------------------------------
class Component(instanceevent.Event):
	'''
	'''
	pass


#----------------------------------------------------------Dependency---
##!! REVISE !!##
class Dependency(instanceevent.Event):
	'''
	'''
	def __init__(self, cfg, dep):
		'''
		'''
		# register the callback...
		# event...
		if hasattr(cfg, dep) and event.isevent(getattr(cfg, dep)):
			event.bind(getattr(cfg, dep), self.fire())
		##!!!
	def __str__(self):
		'''
		'''
		pass
	def __repr__(self):
		'''
		'''
		pass
	def __nonzero__(self):
		'''
		'''
		pass
	def fire(self):
		'''
		'''
		# change state...
		if self:
			super(Dependency, self).fire()
	def getdependency(self):
		'''
		'''
		pass


#-------------------------------------------------DependencyInterface---
class DependencyInterface(object):
	'''
	'''

	__dependency_class__ = Dependency

	def __init__(self):
		'''
		'''
		self._dependencies = {}
	# dependency interface:
	def getdependency(self, name):
		'''
		'''
		# register and create dependency...
		dep = self._dependencies[name] = self.__dependency_class__(self, name)
		return dep




#-----------------------------------------------------------------------
#--------------------------------------------------------------Config---
# this must take the initial state at startup...
# Q: can a config contain more than one FSM?????
# Q: does config need to be an FSM???
class BasicConfig(fsm.FiniteStateMachine):
	'''
	'''
	__rules__ = None


	def __init__(self):
		'''
		'''
		super(BasicConfig, self).__init__()
		# init rules...
		rules = self.__rules__ = {}
		if self.__class__.__rules__ != None:
			for name, rule in self.__class__.__rules__.iteritems():
				# register the rules with the config instance...
				rule = rules[name] = rule(self)
				if hasattr(rule, '__register__'):
					rule.__register__()
##	def initstates(self):
##		'''
##		'''
##		super(Config, self).initstates()


#--------------------------------------------------------------Config---
class Config(BasicConfig, DependencyInterface):
	'''
	'''
	pass



#-----------------------------------------------------------------------
#---------------------------------------------------------------State---
##!! check if mro is wrong !!##
class State(fsm.State, Config):
	'''
	'''
	__fsm__ = None
	__ignore_registration__ = True



#-----------------------------------------------------------------------
#---------------------------------------------------------_StoredRule---
# Q: should rules be stored as classes or objects???
class _StoredRule(stored._StoredClass):
	'''
	'''
	__class_store_attr_name__ = '__config__'

	def storeclass(cls, name, rule):
		'''
		'''
		config = getattr(cls, cls.__class_store_attr_name__)
		# check rule name...
		if hasattr(config, name):
			raise NameError, 'rule named "%s" already exists.' % name
		# register the rule...
		if config.__rules__ == None:
			config.__rules__ = {name: rule}
		else:
			config.__rules__[name] = rule


#-----------------------------------------------------------BasicRule---
class BasicRule(object):
	'''
	'''
	__metaclass__ = _StoredRule
	# Q: can a rule belong to something other than a config?
	__config__ = None
	__ignore_registration__ = True

	def __init__(self, conf):
		'''
		'''
		super(BasicRule, self).__init__()
		# set the config object...
		self.__config__ = conf
	# interface methods:
	def __register__(self):
		'''
		this is called to register the rule handler...
		'''
		pass
##	def __call__(self):
##		'''
##		check the rule/predicate...
##		'''
##		pass


#----------------------------------------------------------------Rule---
class Rule(BasicRule):
	'''
	'''
	__ignore_registration__ = True

	def __call__(self):
		'''
		check the rule/predicate...
		'''
		return self.condition()
	def condition(self):
		'''
		this method defines the condition.
		on call, of this returns True rule.succeed() is called, else rule.fail()...
		'''
		pass
	# std reactions:
	def fail(self):
		'''
		rule failure handler.
		'''
		pass
	def succeed(self):
		'''
		rule success handler.
		'''
		pass



#=======================================================================
if __name__ == '__main__':
	# Example Code:

	# define the system FSM (or use one from the pli.config.system_fsm.*)...
	# each state will create a set of events (onEnter<state>, onExit<state>)
	class mySystemConfig(Config):
		pass

	class RegistringData(State):
		'''this state is where most rules must get registred (e.g.
		plugin-rules etc.), register data for option/config parcers... etc.'''
		__is_initial_state__ = True
		__fsm__ = mySystemConfig

		def __onafterstatechange__(self):
			'''
			'''
			print '000'
			self.changestate(Initializing)

	class Initializing(State):
		'''this will init/register system components'''
		__fsm__ = mySystemConfig

		def __onafterstatechange__(self):
			'''
			'''
			print '111'
			self.changestate(Startingup)

	class Startingup(State):
		'''this will run system components'''
		__fsm__ = mySystemConfig

		def __onafterstatechange__(self):
			'''
			'''
			print '222'
			self.changestate(Running)

	class Running(State):
		'''this is the running state'''
		__fsm__ = mySystemConfig

		def __onafterstatechange__(self):
			'''
			'''
			print '333'
			self.changestate(Shuttingdown)

	class Shuttingdown(State):
		'''this will shutdown/terminate system components'''
		__is_terminal_state__ = True
		__fsm__ = mySystemConfig

		def __onafterstatechange__(self):
			'''
			'''
			print '444'
			pass
	
	# create transitions...
	transition(RegistringData, Initializing)	
	transition(Initializing, Startingup)
	transition(Startingup, Running)
	transition(Running, Shuttingdown)

	# define rules...
	# Ex: config_parser module...
	class ConfParseInitRule(BasicRule):
		__config__ = mySystemConfig
		# when to run (event)
		def __register__(self):
			#event.bind(self.__config__.onRegistringData, self)
			# depend on opt parser... (???)
			# e.g. if no defaults given wait for OptParser...
			if hasattr(self.__config__, 'config_file') is None:
				event.bind(self.__config__.__rules__.OptParserInitRule.onSuccess, self)
			else:
				event.bind(self.__config__.onEnterRegistringData, self)
		def __call__(self, evt, *p, **n):
			print self.__class__.__name__, '!!!!!!'
		# condition
		def condition(self):
			if stateof(self.__config__) is RegistringData:
				return self.succeed()
			else:
				return self.fail()
		# reaction
		def succeed(self):
			# register options with option parser
			pass
		def fail(self):
			pass

	class ConfParseRule(BasicRule):
		__config__ = mySystemConfig
		# when to run (event)
		def __register__(self):
			#event.bind(self.__config__.onEnterInitializing, self)
			event.bind(self.__config__.onEnterInitializing, self)
		def __call__(self, evt, *p, **n):
			print self.__class__.__name__, '!!!!!!'
		# condition
		def condition(self):
			if stateof(self.__config__) is Initializing:
				return self.succeed()
			else:
				return self.fail()
		# reaction
		def fail(self):
			pass
		def succeed(self):
			pass
	
	# create a config instance... 
	#	(each config instance represents a runable/configurable system
	#	instance...)
	sys_cfg = mySystemConfig()

	def f(evt):
		print '   ****', evt.__class__.__name__, ':', evt.state_name
	event.bind(sys_cfg.onEnterRegistringData, f)

	# init the system...
	sys_cfg.start()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
