#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20100628135348'''
__copyright__ = '''(c) Alex A. Naanou 2010'''


#-----------------------------------------------------------------------
__doc__ = '''\
This module takes care of unique object id's.

two elements participate in an object id:
	- oid module import time (approximation of system start time) -- SYSSTART
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
#--------------------------------------------------------------getoid---
def getoid(oids=None, format=None):
	'''
	will generate an object ID.

	if oids is given, it will be used as a set storing the created oids. this
	is used for uniqueness testing.

	if format function is given, it will be used as the final oid object 
	generator/formatter. format will take the two timestamp tuples and the 
	generated oid list.
	'''
	while True:
		if format != None:
			oid = format((SYSSTART, time.time()), oids)
		else:
			oid = (SYSSTART, time.time())
		if oids != None:
			if oid in oids:
##				time.sleep(0.1)
				continue
			oids.update((oid,))
		return oid


#-----------------------------------------------------------getstroid---
def getstroid(oids=None, chars='aAbBcCdDeEfFgGhHiIjJkKlLmMnNoOpPqQrRsStTuUvVwWxXyYzZ'):
	'''
	'''
	def fmt_str(oid, oids=None, chars='abcABC'):
		'''
		'''
		l = str(oids != None and len(oids) or '')
		s = ''.join([ a + b for a, b in zip(str(oid[0]), str(oid[1])[::-1]) ]) + l
		res = ''
		for i, c in enumerate(s):
			res += chars[(ord(c)+i)%len(chars)]
		return res
	return getoid(oids, func.rcurry(fmt_str, chars))



#-----------------------------------------------------------------------
if __name__ == '__main__':
	def oidtuple2str(oid, oids):
		return "id_%s_%s_%s" % tuple([ str(f).replace('.', '') for f in oid ] + [len(oids)])

	OIDS = set()

	ngetoid = func.curry(getoid, OIDS, oidtuple2str)

	print ngetoid()
	print ngetoid()
	print ngetoid()
	print ngetoid()
	print ngetoid()
	print ngetoid()

	print getstroid(OIDS)
	print getstroid(OIDS)
	print getstroid(OIDS)
	print getstroid(OIDS)
	print getstroid(OIDS)
	print getstroid(OIDS)


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
