#=======================================================================

#-----------------------------------------------------------------------

__version__ = '''0.3.15'''
__sub_version__ = '''20040530032430'''
__copyright__ = '''(c) Alex A. Naanou 2003-2004'''


#-----------------------------------------------------------------------

__doc__ = '''\
This module defines the event framework.

Basic concepts:
	Event:
		  An object that represents a hook-point (bind-point), and controls 
		the execution of its hooks/handlers.
		When an event is *fired* all registered (or *bound*) handlers are
		called. The handler execution model depends on the event class 
		used. In general the handlers are executed sequentially in no 
		particular order.
		  It is guaranteed that all handlers of an event are called (except
		when error suppression is disabled (see next..)).
	Event handler/callback/hook:
		  A routine bound to a particular event (one or more) and called 
		when/if the event is fired.
		  If the handler of an event raises an error, this error is ignored.
		(unless the __suppress_exceptions__ attribute of either the handler
		or the event is set).

'''



#-----------------------------------------------------------------------

import pli.objutils as objutils



#-----------------------------------------------------------------------
#----------------------------------------------------------EventError---
class EventError(Exception):
	'''
	a general event error.
	'''

#------------------------------------------------------EventBindError---
class EventBindError(EventError):
	'''
	an event bind error.
	'''


#-----------------------------------------------------------------------
#----------------------------------------------------------------bind---
def bind(event, func, HOOK_DEBUG=False):
	'''
	register func as the event callback.

	HOOK_DEBUG will enable exception propagation from event handlers.
	'''
	if isevent(event):
		if HOOK_DEBUG:
			try:
				# NOTE: this does not pickle correctly...
				func.__suppress_exceptions__ = False
			except:
				pass
		event.installhook(func)
	else:
		raise EventBindError, 'can\'t bind to non-event object %s.' % event


#--------------------------------------------------------------unbind---
def unbind(event, func):
	'''
	unregister func as the event callback.
	'''
	if isevent(event):
		event.uninstallhook(func)
	else:
		raise EventBindError, 'can\'t unbind from non-event object %s.' % event


#-------------------------------------------------------------isbound---
def isbound(event, func):
	'''
	test if func is bound to event.
	'''
	if isevent(event):
		return func in event.__eventhooks__
	else:
		raise EventError, 'object %s is not an event.' % event


#----------------------------------------------------------------fire---
def fire(event, *p, **n):
	'''
	fire the event.

	shortcut for <event>.fire(...)
	'''
	if isevent(event):
		event.fire(*p, **n)
	else:
		raise EventError, 'can\'t fire a non-event object %s.' % event


#-------------------------------------------------------------isevent---
def isevent(obj):
	'''
	check if obj is an event (e.g. related to AbstractEvent)
	'''
	return isinstance(obj, AbstractEvent) or issubclass(obj, AbstractEvent)



#-----------------------------------------------------------------------
#-------------------------------------------------------AbstractEvent---
class AbstractEvent(object):
	'''
	this should be the root of all events and event-like objects. used 
	mainly for isevent and the like...
	'''


#--------------------------------------------------------InstanceEvent---
class InstanceEvent(AbstractEvent):
	'''
	this class defines basic instance event.

	  This can be considered an event factory (each instance of this class 
	is an event).

	  This is intended for use as a base event class, to create multiple 
	similar events, with the ability to bind to each *micro* event.

	event configuration attributes:
		__auto_uninstall__		: if this is set and the unsource method
								  is present the event handler will 
								  automaticly be uninstalled when the 
								  last hook/callback is removed.
								  default: True
		__inherit_source__		: if this is True and the event does not
								  have a source it will be inherited from
								  its parent.
								  default: False
		__strict_source__		: this if set will prevent an event from 
								  being created without a source.
								  default: False
		__max_handler_count__	: this defines the maximum number if 
								  handlers per event (None for no limit)
								  default: None
		__unique_handler_call__	: if this is true a handler may be 
								  installed only once.
								  default: True
		__unique_handler_bind__	: if this is true the ability to bind
								  the same handler to this event will 
								  be disabled (on repeated bind 
								  EventBindError will be raised)
								  default: False
		__suppress_exceptions__ : this is true will supress exceptions 
								  generated by event handlers, thus will 
								  guarantee that evry handler will get 
								  called.
								  NOTE: this might be rather traitorous
								        as all errors are supressed and
										ignored.
		NOTE: all of the above attributes are optional, and most of them
		      can be changed on-the-fly...

	event general interface methods:
		source()				: this is the event installation method.
								  this method is called automaticly on 
								  first handler bind, and usually is used
								  to install the event callback that will
								  fire the event.
								  by default this is obligatory (see the
								  __strict_source__, __inherit_source__ 
								  options).
								  if this is not defined, one must fire 
								  the event manually.
		unsourse()				: this is an optional uninstall method.
								  this is called to uninstall the event 
								  and cleanup (reverse of source).
								  (see the __auto_uninstall__).
		fire(*p, **n)			: this is the event fire method. call this
								  to manually fire the event. usually this
								  is overloaded to define a handler 
								  signature, e.g. the arguments this 
								  receives are passed as-is to both the 
								  predicate method and each handler.
								  NOTE: the arguments are not copied when
								        passed, thus it is possible to run 
										into side-effects (with mutable 
										types).
								  NOTE: the handler will receive the event
								        object as the first argument.
		predicate(*p, **n)		: this method if defined is called by the 
								  fire routine to determine if the event 
								  handlers are to be called.
								  if this returns True the handlers are 
								  called, else the fire method exits silently.
								  NOTE: this must be signature compatible 
								        with the fire method.
		clear()					: this method will remove all handlers of the
								  event (to the exception of class-level 
								  handlers).
								  NOTE: this will call the unsourse method
								        if it is enabled.
		__callhook__(hook, evt, *p, **n)
								: an optional hook wrapper. this is called
								  once per hook, and should call the hook 
								  passing it its arguments.
								  NOTE: if this is changed during event 
								        execution, the current event run will
										not be affected (e.g. the new wrapper 
										will only be used on next event fire).
		
	NOTE: these event do not behave as do traditional events, e.g. the 
	      handler is not passed the event object containing the event data.
		  it is actually passed the event itself and the arguments to fire 
		  depending on a particular event.
	NOTE: here only the public interface is documented, for more LL 
	      information see the comments in the source code.
	NOTE: this was not intended for direct use.
	'''
	# this will hold the hooks/callbacks...
	# WARNING: do not edit manually...
	__eventhooks__ = None
	# if this is set and the unsource method is present the event
	# handler will automaticly be uninstalled when the last
	# hook/callback is removed...
	# default: True
	__auto_uninstall__ = True
	# if this is True and the event does not have a source it will be
	# inherited from its parent...
	# default: False
	__inherit_source__ = False
	# this if set will prevent an event from being created without a
	# source...
	# default: False
	__strict_source__ = False
	# this defines the maximum number if handlers per event (None for
	# no limit)
	# default: None
	__max_handler_count__ = None
	# if this is true a handler may be installed only once.
	# default: True
	__unique_handler_call__ = True
	# if this is true the ability to bind the same handler to this
	# event will be disabled (on repeated bind EventBindError will be
	# raised)
	# default: False
	__unique_handler_bind__ = False
	# if this is set to False the event ececution will break on first
	# handler exception...
	# default: False
	__suppress_exceptions__ = False

	def __init__(self, *p, **n):
		'''
		init the event object.
		'''
		if self.__class__ is InstanceEvent:
			raise TypeError, 'can\'t use the InstanceEvent class directly.'
		# check event source....
##		if (not hasattr(self, '__inherit_source__') or not self.__inherit_source__) and \
##				hasattr(self, '__strict_source__') and self.__strict_source__ and not hasattr(self, 'source'):
		if not hasattr(self, 'source') \
				and hasattr(self, '__strict_source__') and self.__strict_source__:
			raise TypeError, 'an event must have a source.'
		super(InstanceEvent, self).__init__(*p, **n)
##	def __callhook__(self, hook, evt, *p, **n):
##		'''
##		this, if present, will be used to call each hook (e.g. hook wrapper).
##		'''
##		hook(evt, *p, **n)
	def source(self):
		'''
		this method will register the callback that will fire the event.
		NOTE: this is a class method.
		'''
		if hasattr(self, '__strict_source__') and self.__strict_source__:
			raise NotImplementedError, 'an event must have a source.'
	source = objutils.classinstancemethod(source)
	def fire(self, *pargs, **nargs):
		'''
		this will check the predicate if present and fire the event.

		NOTE: if the predicate will return False the event will not be fired.
		NOTE: the predicate will receive the same args as fire.
		'''
		# do not fire the event if the predicate returns false...
		if hasattr(self, 'predicate'):
			if not self.predicate(*pargs, **nargs):
				return
		return self._exec_event_callback(*pargs, **nargs)
	def _exec_event_callback(self, *pargs, **nargs):
		'''
		this is the LL event handler executer.

		NOTE: this was not intended for direct use.
		'''
		# do not fire the event if the predicate returns false...
		evthooks = self.__eventhooks__
		self_evthooks = self.__class__.__eventhooks__
		# handle hooks if at least one of the classes or metaclasses
		# hook sets is not none...
		if evthooks != None or self_evthooks != None:
			if not hasattr(self, '__unique_handler_call__') or self.__unique_handler_call__:
				##!!! use the set type...
				# remove all repeating elements from the hook list...
				hooks = dict([(item, None) for item in \
									(self_evthooks != None and self_evthooks or ()) \
									+ (evthooks != None and evthooks or ()) \
							 ]).keys() 
			else:
				hooks = (self_evthooks != None and self_evthooks or ()) + (evthooks != None and evthooks or ())
			# check if we have a hook wrapper....
			if hasattr(self, '__callhook__') and callable(self.__callhook__):
				# call wrapped hooks...
##				raise NotImplementedError, 'assync event mode is not yet enabled.'
				wrapper = self.__callhook__
				for hook in hooks:
					try:
						# wrap the hook...
						wrapper(hook, self, *pargs, **nargs)
					except:
						# raise the exception if either  the hook or the
						# event are in debug mode...
						if (not hasattr(hook, '__suppress_exceptions__') or hook.__suppress_exceptions__ == False) or \
								(not hasattr(self, '__suppress_exceptions__') or self.__suppress_exceptions__ == False):
							raise
##						elif False:
##							# log the exception.....
##							##!!!
##							pass
			else:
				# call bare hooks...
				for hook in hooks:
					try:
						# call the hook...
						hook(self, *pargs, **nargs)
					except:
						# raise the exception if either  the hook or the
						# event are in debug mode...
						if (not hasattr(hook, '__suppress_exceptions__') or hook.__suppress_exceptions__ == False) or \
								(not hasattr(self, '__suppress_exceptions__') or self.__suppress_exceptions__ == False):
							raise
##						elif False:
##							# log the exception.....
##							##!!!
##							pass
	def installhook(self, hook_func):
		'''
		this will install an event hook/handler.
		'''
		if self.__eventhooks__ == None:
			self.__eventhooks__ = ()
			self.source()
		# handler count...
		if hasattr(self, '__max_handler_count__') and self.__max_handler_count__ != None \
				and len(self.__eventhooks__) >= self.__max_handler_count__:
			raise EventBindError, 'maximum handler count reached for %s.' % self
		# handler uniqueness...
		if hasattr(self, '__unique_handler_bind__') and self.__unique_handler_bind__:
			evthooks = self.__eventhooks__
			self_evthooks = self.__class__.__eventhooks__
			if hook_func in (self_evthooks != None and self_evthooks or ()) \
								+ (evthooks != None and evthooks or ()):
				raise EventBindError, 'the handler %s is already bound to event %s' % (hook_func, self)
			self.__eventhooks__ += (hook_func,)
		else:
			self.__eventhooks__ += (hook_func,)
	installhook = objutils.classinstancemethod(installhook)
	def uninstallhook(self, hook_func):
		'''
		this will uninstall an event hook/handler.
		'''
		if hook_func in self.__eventhooks__:
			tmp = list(self.__eventhooks__)
			tmp.remove(hook_func)
			self.__eventhooks__ = tuple(tmp)
		if self.__eventhooks__ == ():
			self.clear()
	uninstallhook = objutils.classinstancemethod(uninstallhook)
	def clear(self):
		'''
		this will drop all handlers for this event.
		'''
		self.__eventhooks__ = None
		# uninstall handler...
		if hasattr(self, '__auto_uninstall__') and self.__auto_uninstall__ and \
				hasattr(self, 'unsource'):
			self.unsource()

	
#--------------------------------------------------------------_ClassEvent---
# NOTE: this might change in the future...
# NOTE: it might be good to pass an event instance to the handler,
#       though this will be memory hungry (copy per handler...)
class _ClassEvent(InstanceEvent, type):
	'''

	NOTE: the time the event is fired depends on the actual event class.
	NOTE: the args the callback will receive depend on the actual event it
	      is bound to.
	'''
	# this will hold the hooks/callbacks...
	# WARNING: do not edit manually...
	__eventhooks__ = None
	# if this is set and the unsource method is present the event
	# handler will automaticly be uninstalled when the last
	# hook/callback is removed...
	__auto_uninstall__ = True
	# this defines the maximum number if handlers per event (None for
	# no limit)
	__max_handler_count__ = None
	# this will define a list of methods to be auto-converted to
	# classmethods....
	# WARNING: do not change unless you know what you are doing!
	__interface_methods__ = (
							 'fire', 
							 'source', 
							 'unsource',
							 'predicate',
							 '__callhook__',
							)

##	__suppress_exceptions__ = True

	def __init__(cls, name, bases, ns):
		'''
		'''
		# check event source.... ##!!! revise this check !!!#
		if (not hasattr(cls, '__inherit_source__') or not cls.__inherit_source__) and \
				hasattr(cls, '__strict_source__') and cls.__strict_source__ and 'source' not in ns:
			raise TypeError, 'an event must have a source.'
		# classmethodify methods...
		for meth in cls.__interface_methods__:
			if meth in ns:
				setattr(cls, meth, classmethod(ns[meth]))
		super(_ClassEvent, cls).__init__(name, bases, ns)
##	def __call__(cls, *pargs, **nargs):
##		'''
##		'''
##		super(_ClassEvent, cls).__call__()


#----------------------------------------------------------ClassEvent---
class ClassEvent(AbstractEvent):
	'''
	base abstract class event.

	  In essence, this is the same as the InstanceEvent, thus all 
	documentation written for the above is applicable here, with the 
	exception that each ClassEvent subclass is an event by itself
	(the event factory here is a metaclass).

	  this is to be used for global, system level events, where there
	is no need to create multiple copies of the event.


	NOTE: this was not intended for direct use.
	'''
	__metaclass__ = _ClassEvent
	# this will hold the hooks/callbacks...
	# WARNING: do not edit manually...
	__eventhooks__ = None
	# if this is True and the event does not have a source it will be
	# inherited from its parent...
	# NOTE: an event must have a source.
	__inherit_source__ = False
	# this if set will prevent an event from being created without a
	# source...
	__strict_source__ = False

	def source(self):
		'''
		this method will register the callback that will fire the event.
		NOTE: this is a class method.
		'''
		if hasattr(self, '__strict_source__') and self.__strict_source__:
			raise NotImplementedError, 'an event must have a source.'
	# these are here for documentation...
##	def unsource(cls):
##		'''
##		this will uninstall the event hook...
##		'''
##	def predicate(cls, *pargs, **nargs):
##		'''
##		this should test if an event is to be fired... 
##		(return True to fire False to ignore)
##		'''
##		return True
##	def fire(cls, *pargs, **nargs):
##		'''
##		'''

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# legacy support (and a convenient shorthand :) )...
Event = ClassEvent



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
