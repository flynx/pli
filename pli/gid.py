#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20101118140517'''
__copyright__ = '''(c) Alex A. Naanou 2010'''


#-----------------------------------------------------------------------
__doc__ = '''\
This module takes care of unique object id's.

this is a compatibility module for some legacy code. use uuid instead.

uniqueness is also checked.
'''
#-----------------------------------------------------------------------

##raise Warning, 'use the standard uuid instead of this.'


#-----------------------------------------------------------------------

import time
import uuid

import pli.functional as func


#-----------------------------------------------------------------------
#--------------------------------------------------------------getgid---
def getgid(gids=None, format=None):
	'''
	will generate an object ID.

	if gids is given, it will be used as a set storing the created gids. this
	is used for uniqueness testing.

	if format function is given, it will be used as the final gid object 
	generator/formatter. format will take the two timestamp tuples and the 
	generated gid list.
	'''
	while True:
		if format != None:
			gid = format(uuid.uuid4(), gids)
		else:
			gid = uuid.uuid4()
		if gids != None:
			if gid in gids:
##				time.sleep(0.1)
				continue
			gids.update((gid,))
		return gid


#-----------------------------------------------------------getstrgid---
def getstrgid(gids=None, chars='aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ', pattern='OID_%s'):
	'''
	'''
	def fmt_str(gid, gids=None, chars='abcABC'):
		'''
		'''
		s = gid.get_hex()
		res = ''
		for i, c in enumerate(s):
			res += chars[(ord(c)+i)%len(chars)]
		return pattern % res
	return getgid(gids, func.rcurry(fmt_str, chars))



#-----------------------------------------------------------------------
if __name__ == '__main__':
	def gidtuple2str(gid, gids):
		return "id_%s" % gid.get_hex()

	OIDS = set()

	ngetgid = func.curry(getgid, OIDS, gidtuple2str)

	print ngetgid()
	print ngetgid()
	print ngetgid()
	print ngetgid()
	print ngetgid()
	print ngetgid()

	print getstrgid(OIDS)
	print getstrgid(OIDS)
	print getstrgid(OIDS)
	print getstrgid(OIDS)
	print getstrgid(OIDS)
	print getstrgid(OIDS)


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
