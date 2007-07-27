#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20070728002827'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import sys

import pli.event as evt
from pli.functional import curry


#-----------------------------------------------------------------------
#----------------------------------------------------------------bind---
# Example:
#	from pli.event.decorator import bind
#
# 	@bind(onSomeEvent)
# 	def handler(evt, *p, **n):
# 		'''
# 		'''
# 		pass
#
def bind(event, HOOK_DEBUG=False):
	'''
	this will bind the decorated object to event.

	NOTE: multiple binds are allowed.
	'''
	return curry(evt.bind, event, HOOK_DEBUG=HOOK_DEBUG)



#-----------------------------------------------------------------------
#----------------------------------------------_is_call_event_handler---
def _is_call_event_handler(func):
	'''
	'''
	if hasattr(func, 'evt_pre_call'):
		return True
	return False


#------------------------------------------_create_call_event_handler---
# XXX make this picklable!
# XXX should we use aspecting here??
def _create_call_event_handler(func, pre_event=None, post_event=None, err_event=None):
	'''
	'''
	if not _is_call_event_handler(func):
		# create a wrapper...
		def _call_event_handler(*p, **n):
			'''
			'''
			# do the pre event...
			for evt in _call_event_handler.evt_pre_call:
				evt.fire(func, *p, **n)
			# do the call...
			try:
				res = func(*p, **n)
			except Exception, err:
				# do the err event...
				for evt in _call_event_handler.evt_err_call:
					evt.fire(func, err)
				# XXX might be good to be more thorough here... (e.g.
				#     use the same traceback as the original...)
				raise err
			except:
				# handle other exceptions...
				err = sys.exc_info()
				# do the err event...
				for evt in _call_event_handler.evt_err_call:
					evt.fire(func, err[0])
				# XXX might be good to be more thorough here... (e.g.
				#     use the same traceback as the original...)
				raise err[0]
			# do the post event...
			for evt in _call_event_handler.evt_post_call:
				evt.fire(func, res)
			return res
		_call_event_handler.evt_pre_call = ()
		_call_event_handler.evt_post_call = ()
		_call_event_handler.evt_err_call = ()
		_call_event_handler.evt_target_func = func
		res = _call_event_handler
	else:
		res = func
	
	# add events...
	if pre_event != None:
		res.evt_pre_call += (pre_event,)
	if post_event != None:
		res.evt_post_call += (post_event,)
	if err_event != None:
		res.evt_err_call += (err_event,)

	return res


#---------------------------------------------------------precallfire---
# XXX do we need the reverse of this??
def precallfire(event):
	'''
	decorate a callable to fire an event before it's call.

	NOTE: the event will recive the callables arguments.
	'''
	def _decorate(func):
		'''
		'''
		return _create_call_event_handler(func, pre_event=event)
	return _decorate

#--------------------------------------------------------postcallfire---
# XXX do we need the reverse of this??
def postcallfire(event):
	'''
	decorate a callable to fire an event after it's call.

	NOTE: the event will recive call return value.
	'''
	def _decorate(func):
		'''
		'''
		return _create_call_event_handler(func, post_event=event)
	return _decorate


#-------------------------------------------------------errorcallfire---
# XXX might be a good idea to filter errors here (e.g. @errorcallfire(onBadError, TypeError))...
# XXX do we need the reverse of this??
def errorcallfire(event):
	'''
	decorate a callable to fire an event if it's call results in an error.

	NOTE: the event will recive exception object raised.
	NOTE: this will not eat the error, rather, it will be re-raised just 
	      after the event handlers are done.
	'''
	def _decorate(func):
		'''
		'''
		return _create_call_event_handler(func, err_event=event)
	return _decorate



#-----------------------------------------------------------------------
if __name__ == '__main__':


	import pli.event as evt

	class onBeforeCall(evt.Event): pass
	class onAfterCall(evt.Event): pass
	class onCallError(evt.Event): pass

	@bind(onBeforeCall)
	def precallhandler(evt, func, *p, **n):
		print 'PRECALL:', evt, func, p, n


	@bind(onAfterCall)
	def postcallhandler(evt, func, *p, **n):
		print 'POSTCALL:', evt, func, p, n


	@bind(onCallError)
	def errorcallhandler(evt, func, *p, **n):
		print 'CALL ERROR:', evt, func, p, n

	

	@precallfire(onBeforeCall)
	@postcallfire(onAfterCall)
	@errorcallfire(onCallError)
	def f(action='call', *p, **n):
		print 'IN_CALL', p, n
		if action == 'except':
			raise TypeError, '!!!'
##		if action == 'str except':
##			raise '!!!'
		return 'result string'


	print '-'*72
	print 'normal call:'
	print
	f()

	print

	try:
		print '-'*72
		print 'call with normal exception:'
		print
		f('except')
	except:
		pass

	print

##	try:
##		print '-'*72
##		print 'call with str exception:'
##		print
##		f('str except')
##	except:
##		pass





#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
