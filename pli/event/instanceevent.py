#=======================================================================

#-----------------------------------------------------------------------

__version__ = '''0.0.07'''
__sub_version__ = '''20040320211418'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


# TODO revise this framework...

#-----------------------------------------------------------------------

import event
from event import bind, unbind, isbound, fire


#-----------------------------------------------------------------------
#---------------------------------------------------------------Event---
##!! TEST !!##
class Event(event.AbstractEvent):
	'''
	base abstract event class.
	'''
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

##	def __init__(self, name, *p, **n):
	def __init__(self, *p, **n):
		'''
		'''
		# set event name...
##		if len(p) > 0 and type(p[0] is str):
##			self.__name__ = p[0]
##		self.__name__ = name
		# check event source....
		if (not hasattr(self, '__inherit_source__') or not self.__inherit_source__) and \
				hasattr(self, '__strict_sorce__') and self.__strict_sorce__ and 'source' not in ns:
			raise TypeError, 'an event must have a source.'
		super(Event, self).__init__(*p, **n)
	def source(self):
		'''
		this method will register the callback that will fire the event.
		'''
		if hasattr(self, '__strict_sorce__') and self.__strict_sorce__: 
			raise NotImplementedError, 'an event must have a source.'
	def fire(self, *pargs, **nargs):
		'''
		this will fire the event.
		'''
		# do not fire the event if the predicate returns false...
		if hasattr(self, 'predicate'):
			if not self.predicate(*pargs, **nargs):
				return
		return self.ev_callback(*pargs, **nargs)
	def ev_callback(self, *pargs, **nargs):
		'''
		'''
		evthooks = self.__eventhooks__
		cls_evthooks = self.__class__.__eventhooks__
		# handle hooks if atleast one of the classes or metaclasses
		# hook sets is not none...
		if evthooks != None or cls_evthooks != None:
			for hook in dict([(item, None) for item in \
									(cls_evthooks != None and cls_evthooks or ()) \
									+ (evthooks != None and evthooks or ()) \
							 ]).keys():
				try:
					# might be good to return an event object...
					hook(self, *pargs, **nargs)
				except:
					# raise the exception if either  the hook or the
					# event are in debug mode...
					if hasattr(hook, 'EVT_DEBUG') and hook.EVT_DEBUG or \
							hasattr(self, 'EVT_DEBUG') and self.EVT_DEBUG:
						raise
	def installhook(self, hook_func):
		'''
		'''
		if self.__eventhooks__ == None:
			self.__eventhooks__ = ()
			self.source()
		self.__eventhooks__ += (hook_func,)
	def uninstallhook(self, hook_func):
		'''
		'''
		if hook_func in self.__eventhooks__:
			tmp = list(self.__eventhooks__)
			tmp.remove(hook_func)
			self.__eventhooks__ = tuple(tmp)
		if self.__eventhooks__ == ():
			self.__eventhooks__ = None
			# uninstall handler...
			if hasattr(self, '__auto_uninstall__') and self.__auto_uninstall__ and \
					hasattr(self, 'unsource'):
				self.unsource()
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



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
