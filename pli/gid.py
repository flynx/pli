#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20100628140508'''
__copyright__ = '''(c) Alex A. Naanou 2010'''


#-----------------------------------------------------------------------
__doc__ = '''\
This module takes care of unique object id's.

two elements participate in an object id:
	- gid module import time (approximation of system start time) -- SYSSTART
	- object/id createion time.

uniqueness is also checked.
'''
#-----------------------------------------------------------------------

import time

import pli.functional as func


#-----------------------------------------------------------------------

# XXX check if this is safe...
SYSSTART = time.time()


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
			gid = format((SYSSTART, time.time()), gids)
		else:
			gid = (SYSSTART, time.time())
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
		l = str(gids != None and len(gids) or '')
		s = ''.join([ a + b for a, b in zip(str(gid[0]), str(gid[1])[::-1]) ]) + l
		res = ''
		for i, c in enumerate(s):
			res += chars[(ord(c)+i)%len(chars)]
		return pattern % res
	return getgid(gids, func.rcurry(fmt_str, chars))



#-----------------------------------------------------------------------
if __name__ == '__main__':
	def gidtuple2str(gid, gids):
		return "id_%s_%s_%s" % tuple([ str(f).replace('.', '') for f in gid ] + [len(gids)])

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
