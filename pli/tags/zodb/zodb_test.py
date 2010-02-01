#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20091008174151'''
__copyright__ = '''(c) Alex A. Naanou 2007'''


#-----------------------------------------------------------------------

# zodb...
import ZODB
from ZODB import FileStorage, DB
import ZODB.config
import transaction

import time

##from persistent import Persistent
from persistent import mapping
##import BTrees.OOBTree
##from BTrees.OOBTree import OOSet, OOBTree, Set



#-----------------------------------------------------------------------

##!!! patch/wrap the data to make it transaction-aware...


#-----------------------------------------------------------------------
# XXX might be good to have a seporate reset mode (to create new data)...
# 
# TODO a raw data browser...
#
LOG_ENABLED = False

def log(
		pre='\t\t\t[%(id)s]\t%(name)s(*%(args)s, **%(nargs)s)', 
		post='\t\t\t[%(id)s]\t\t-> %(res)s'):
	def _log(func):
		def _logger(*p, **n):
			if LOG_ENABLED:
				call_id = func.__name__ + str(time.time())
				print pre % {'id': call_id, 'name': func.__name__, 'args': p, 'nargs': n}
				res = func(*p, **n)
				print post % {'id': call_id, 'res': res, 'name': func.__name__, 'args': p, 'nargs': n}
				return res
			else:
				return func(*p, **n)
		return _logger
	return _log


#-----------------------------------------------------------------------
##!!! this tiny framework is not intended for pruduction use, for that 
##!!! it needs to at least not use globals...
@log()
def opendb(db_config):
	'''
	'''
	global db, connection, root

	db = ZODB.config.databaseFromURL(db_config)
	connection	= db.open()
	root		= connection.root()


@log()
def getorcreate(name, setup):
	'''
	'''
	try:
		# get the data if it exists...
		site = root.get(name, None)

		if site == None:
			# create the data and store it for the first time...
			site = setup()
			root[name] = site

	finally:
		commit()

	return site


@log()
def commit():
	transaction.commit()


@log()
def closedb():
	commit()
	connection.close()
	db.close()



#-----------------------------------------------------------------------
if __name__ == '__main__':

	import zset as zset
	import ztagset as ztagset

	CFG='./zodb_test.conf'

	opendb(CFG)


	# create some stuff...
	s = getorcreate('foo', lambda: zset.zset())
	t = getorcreate('boo', lambda: ztagset.ZDictTagSet())


	print 's:', s
	if 'fooo' not in s:
		s.add('fooo')
		print 's:', s
	else:
		s.add(len(s))
		print 's:', s
	commit()

	print

	print 't:', t.tags()
	if 'ttt' not in t:
		t.tag('aaa', 'ttt')
		print 't:', t.tags()
	else:
		t.tag('aaa', '%s' % str(len(t.tags())))
		print 't.tags:', t.tags()
		print 't.objects:', t.objects()

	commit()


	closedb()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
