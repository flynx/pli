#=======================================================================

#-----------------------------------------------------------------------

__version__ = '''0.2.09'''
__sub_version__ = '''20040321213622'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


# TODO revise this framework...

#-----------------------------------------------------------------------
#----------------------------------------------------------------bind---
def bind(event, func, HOOK_DEBUG=False):
	'''
	register func as the event callback.

	HOOK_DEBUG will enable exception propogation from event handlers.
	'''
	if HOOK_DEBUG:
		try:
			# NOTE: this does not pickle correctly...
			func.__suppress_exceptions__ = True
		except:
			pass
	event.installhook(func)


#--------------------------------------------------------------unbind---
def unbind(event, func):
	'''
	unregister func as the event callback.
	'''
	event.uninstallhook(func)


#-------------------------------------------------------------isbound---
def isbound(event, func):
	'''
	test if func is bound to event.
	'''
	return func in event.__eventhooks__


#----------------------------------------------------------------fire---
def fire(event, *p, **n):
	'''
	fire the event.

	shortcut for <event>.fire(...)
	'''
	event.fire(*p, **n)


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
	'''
	pass

	
#--------------------------------------------------------------_Event---
# NOTE: this might change in the future...
# NOTE: it might be good to pass an event instance to the handler,
#       though this will be memory hungry (copy per handler...)
class _Event(type):
	'''

	NOTE: the time the event is fired depends on the actual event class.
	NOTE: the args the callbeck will recive depend on the actual event it is bound to.
	'''
	# this will hold the hooks/callbacks...
	# WARNING: do not edit manualy...
	__eventhooks__ = None
	# if this is set and the unsource method is present the event
	# handler will automaticly be uninstalled when the last
	# hook/callback is removed...
	__auto_uninstall__ = True
	# this will define a list of methods to be auto-converted to
	# classmethods....
	# WARNING: do not change unless you know what you are doing!
	__interface_methods__ = ('fire', 'source', 'unsource', 'predicate')

##	__suppress_exceptions__ = True

	def __init__(cls, name, bases, ns):
		'''
		'''
		# check event source....
		if (not hasattr(cls, '__inherit_source__') or not cls.__inherit_source__) and \
				hasattr(cls, '__strict_sorce__') and cls.__strict_sorce__ and 'source' not in ns:
			raise TypeError, 'an event must have a source.'
		# classmethodify methods...
		for meth in cls.__interface_methods__:
			if meth in ns:
				setattr(cls, meth, classmethod(ns[meth]))
		super(_Event, cls).__init__(name, bases, ns)
##	def __call__(cls, *pargs, **nargs):
##		'''
##		'''
##		super(_Event, cls).__call__()
	def fire(cls, *pargs, **nargs):
		'''
		'''
		# do not fire the event if the predicate returns false...
##		if hasattr(cls, 'predicate'):
##			if not cls.predicate(*pargs, **nargs):
##				return
		return cls.ev_callback(*pargs, **nargs)
	def ev_callback(cls, *pargs, **nargs):
		'''
		'''
		# do not fire the event if the predicate returns false...
		# TODO move this into cls.fire...
		if hasattr(cls, 'predicate'):
			if not cls.predicate(*pargs, **nargs):
				return
		evthooks = cls.__eventhooks__
		cls_evthooks = cls.__class__.__eventhooks__
		# handle hooks if atleast one of the classes or metaclasses
		# hook sets is not none...
		if evthooks != None or cls_evthooks != None:
			for hook in dict([(item, None) for item in \
									(cls_evthooks != None and cls_evthooks or ()) \
									+ (evthooks != None and evthooks or ()) \
							 ]).keys():
				try:
					# might be good to return an event object...
					hook(cls, *pargs, **nargs)
				except:
					# raise the exception if either  the hook or the
					# event are in debug mode...
					if hasattr(hook, '__suppress_exceptions__') and hook.__suppress_exceptions__ == False or \
							hasattr(cls, '__suppress_exceptions__') and cls.__suppress_exceptions__ == False:
						raise
	def installhook(cls, hook_func):
		'''
		'''
		if cls.__eventhooks__ == None:
			cls.__eventhooks__ = ()
			cls.source()
		cls.__eventhooks__ += (hook_func,)
	def uninstallhook(cls, hook_func):
		'''
		'''
		if hook_func in cls.__eventhooks__:
			tmp = list(cls.__eventhooks__)
			tmp.remove(hook_func)
			cls.__eventhooks__ = tuple(tmp)
		if cls.__eventhooks__ == ():
			cls.__eventhooks__ = None
			# uninstall handler...
			if hasattr(cls, '__auto_uninstall__') and cls.__auto_uninstall__ and \
					hasattr(cls, 'unsource'):
				cls.unsource()


#---------------------------------------------------------------Event---
class Event(AbstractEvent):
	'''
	base abstract event.
	'''
	__metaclass__ = _Event
	# this will hold the hooks/callbacks...
	# WARNING: do not edit manualy...
	__eventhooks__ = None
	# if this is True and the event does not have a source it will be
	# inherited from its parent...
	# NOTE: an event must have a source.
	__inherit_source__ = False
	# this if set will prevent an event from being created without a
	# source...
	__strict_sorce__ = False

	def source(cls):
		'''
		this method will register the callback that will fire the event.
		NOTE: this is a class method.
		'''
		if hasattr(self, '__strict_sorce__') and self.__strict_sorce__:
			raise NotImplementedError, 'an event must have a source.'
##	# these are here for documentation...
##	def unsource(cls):
##		'''
##		this will unistall the event hook...
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
##	def ev_callback(cls, *pargs, **nargs):
##		'''
##		'''



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
