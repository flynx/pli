#=======================================================================

__version__ = '''0.0.09'''
__sub_version__ = '''20090410122453'''
__copyright__ = '''(c) Alex A. Naanou 2003-2004'''


#-----------------------------------------------------------------------

import thread
import time

import event


#-----------------------------------------------------------------------

class TimerEventError(Exception):
	'''
	'''
	pass


#-----------------------------------------------------------------------
# this will set the default global timer resolution...
TIMER_RESOLUTION = 10

#---------------------------------------------------------------Timer---
class Timer(object):
	'''
	this is the base timer class.
	'''
	__callbacks__ = ()

	def __init__(self, res=None):
		'''
		'''
		self.resolution = res
		self.running = False
	def installhook(self, hook_func):
		'''
		'''
		if self.__callbacks__ == ():
			self.start()
		self.__callbacks__ += (hook_func,)
	def uninstallhook(self, hook_func):
		'''
		'''
		t = list(self.__callbacks__)
		t.remove(hook_func)
		self.__callbacks__ = tuple(t)
		##!!! check for stop...
	def start(self):
		'''
		start the timer.
		'''
		if not self.running:
			self.running = True
			return thread.start_new(self.loop, ())
		else:
			raise TypeError, 'can\'t start the timer twice'
##	def stop(self):
##		'''
##		'''
##		pass
	def loop(self, res=None):
		'''
		this is the timer loop.
		'''
		while 1:
			if res in (None, 0):
				if self.resolution in (None, 0):
					_res = TIMER_RESOLUTION
				else:
					_res = self.resolution
			time.sleep(_res)
			# if there is a callback call it...
			for f in self.__callbacks__:
				##!!! revise...
				try:
					f()
				except:
					pass

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# create a global timer object...
globaltimer = Timer()


#------------------------------------------------------BaseTimerEvent---
class AbstractTimerEvent(event.AbstractEvent):
	'''
	'''
	# this will define the timer object to be used as the event
	# initiator....
	__timer__ = globaltimer

	def source(self):
		'''
		'''
		self.__timer__.installhook(self.fire)


#------------------------------------------------------BaseTimerEvent---
class BaseTimerEvent(AbstractTimerEvent, event.Event):
	'''
	'''
	__inherit_source__ = True

	def source(cls):
		'''
		'''
		if cls.__name__ == 'BaseTimerEvent':
			raise TypeError, 'can\'t bind to "BaseTimerEvent".'
		cls.__timer__.installhook(cls.fire)
##		return super(BaseTimerEvent, cls).source()
		
	


#----------------------------------------------BaseInstanceTimerEvent---
class BaseInstanceTimerEvent(AbstractTimerEvent, event.InstanceEvent):
	'''
	'''
	pass


#-----------------------------------------------------------------------
# The Events:
#-------------------------------------------------------------onTimer---
class onTimer(BaseTimerEvent):
	'''
	this event is fired on each timer tick.
	'''


#--------------------------------------------------------------Hourly---
class Hourly(BaseTimerEvent):
	'''
	this event is fired once per hour (the accuracy depends on timer resolution).
	'''
	_last = None
	def predicate(cls, *p, **n):
		'''
		'''
		cur = time.strftime('%H')
		if cur != cls._last:
			cls._last = cur
			return True
		return False


#---------------------------------------------------------------Daily---
class Daily(BaseTimerEvent):
	'''
	this event is fired once a day (the accuracy depends on timer resolution).
	'''
	# this will set the time of day when the event is fired (00-24).
	__hour__ = '00'

	def predicate(cls, *p, **n):
		'''
		'''
		last = time.strftime('%H')
		if last == cls.__hour__:
			return True
		return False


#--------------------------------------------------------------InSecs---
class FireInSeconds(AbstractTimerEvent, event.InstanceEvent):
	'''
	this will create an event that will fire after a given number of 
	seconds.
	after this is fired it will be recycled (e.g. the event is fired once)

	NOTE: the accuracy of this depends on the timer resolution.
	'''
	__timer__ = globaltimer

	_fire_at = None
	_hook = None
	timer_enabled = True

	def __init__(self, seconds):
		'''
		'''
		self._fire_in = seconds
		# calculate the tame at which we need to be fired...
		self.start()
	def source(self):
		'''
		'''
		hook = self._hook = self.fire
		self.__timer__.installhook(hook)
	def unsource(self):
		'''
		'''
		hook = self._hook
		self.__timer__.uninstallhook(hook)
		self._hook = None
	def predicate(self, *p, **n):
		'''
		'''
		if self.timer_enabled == True \
				and self._fire_at != None \
				and time.time() >= self._fire_at:
			self.reset()
			return True
		return False
	# user interface methods...
	def reset(self):
		'''
		reset the event.
		'''
		self._fire_at = None 
	def start(self):
		'''
		start the timer.

		NOTE: if the fire time is passed
		'''
		if self._fire_at == None:
			self._fire_at = time.time() + float(self._fire_in)
			self.timer_enabled = True
		else:
			raise TimerEventError, 'can\'t start a running event (reset first).' 
	def stop(self):
		'''
		stop the timer (the event will not fire).
		'''
		self.timer_enabled = False
	def resume(self):
		'''
		resume the timer.

		NOTE: if this is called after the time has passed the event will
		      be fired right away.
		'''
		self.timer_enabled = True
		if self._fire_at != None \
				and time.time() >= self._fire_at:
			self.fire()
			self.reset()
		


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
