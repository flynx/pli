#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20091008174201'''
__copyright__ = '''(c) Alex A. Naanou 2007'''


#-----------------------------------------------------------------------

import transaction
import sys


#-----------------------------------------------------------------------
#------------------------------------------------------------mutating---
# XXX move this to a more generic spot... (good as a general zodb
#     support decorator)
def mutating(meth):
	'''
	set ._p_changed on the object calling the method...
	'''
	def _mutating(self, *p, **n):
		'''
		'''
		res = meth(self, *p, **n)
		self._p_changed = True
		return res
	return _mutating


#-------------------------------------------------------transactional---
def transactional(meth):
	'''
	set a savepint, execute the method and if all goes well commit, else
	rollback to the savepoit.

	if the soft_transaction decorator was also used, this will not do a 
	hard commit. only rollback to the savepoint in case of an error.
	(see soft_transaction for more details)
	'''
	def _transactional(self, *p, **n):
		'''
		'''
		# create a save point...
		pre = transaction.savepoint()
		try:
			res = meth(self, *p, **n)
			# XXX is this good?
			if not getattr(meth, '_soft_transaction', False):
				transaction.commit()
			return res
		except:
			pre.rollback()
			# re-raise the error...
			raise
	return _transactional


#----------------------------------------------------soft_transaction---
def soft_transaction(meth):
	'''
	use savepoints but do not commit the transaction.

	this is to be used if a method needs to execute as part of a sute an 
	a commit is to be issued only if the whole sute is done.

	NOTE: this is pointless unless used in conjunction with @transactional.
	'''
	meth._soft_transaction = True
	return meth


#----------------------------------------------------subtransactional---
def subtransactional(meth):
	'''
	shorthand for a transactional method decorator that does not commit 
	the global transactions but cleans up if something goes wrong.

	same as:
		@transactional
		@soft_transaction
		def meth(...):
			...
	'''
	return transactional(soft_transaction(meth))


#---------------------------------------------------------------split---
# XXX this is fully generic.... move to pli!
def split(name, *decorators):
	'''
	apply decorators to func and save result with name, not affecting 
	the original.

	NOTE: this can safely be used in combenation with other decorators.
	NOTE: the order is still important and what will go into func depends
	      on what decorators were executed before split.

	Example:
		@a
		@b(123)
		@split('func2', x, y(321))
		def func(...):
			pass

		# this is identical to:
		def func(...): 
			pass
		func2 = func
		func = a(b(123)(func))
		func2 = x(y(321)(func))

	'''
	def _split(func):
		'''
		'''
		orig = func
		# decorate the function...
		for d in decorators[::-1]:
			func = d(func)
		# save the decorated func by name in the containing ns...
		sys._getframe(1).f_locals[name] = func
		return orig
	return _split



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
