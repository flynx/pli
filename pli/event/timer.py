#=======================================================================

__version__ = '''0.0.09'''
__sub_version__ = '''20040331000551'''
__copyright__ = '''(c) Alex A. Naanou 2003-2004'''


#-----------------------------------------------------------------------

import thread
import time

import event


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
		self.__callbacks__ = t
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
				f()

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
# create a global timer object...
globaltimer = Timer()


#------------------------------------------------------BaseTimerEvent---
class BaseTimerEvent(event.Event):
	'''
	'''
	__inherit_source__ = True
	# this will define the timer object to be used as the event
	# initiator....
	__timer__ = globaltimer

	def source(cls):
		'''
		'''
		if cls.__name__ == 'BaseTimerEvent':
			raise TypeError, 'can\'t bind to "BaseTimerEvent".'
		cls.__timer__.installhook(cls.fire)



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
		


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
