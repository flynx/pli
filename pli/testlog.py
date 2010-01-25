#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20100125192403'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import sys
from pprint import pprint, pformat


#-----------------------------------------------------------------------

INDENT = 2
TERM_WIDTH = 80

TEST_FILE_NAME = '<test>'
REPR_FUNCTION = repr

MUTE_PREFIX = '!'
PPRINT_PREFIX = '>>>'


#-----------------------------------------------------------------------
# 
# XXX the script does not see the imported modules...
# 		from pprint import pprint
# 		logstr(''''
# 			## this will priduce a name error!
# 			! pprint
# 		'')
#
# 	   there are cases when this works...
#
#
# TODO add error log support...
# TODO add quiet mode...
# TODO reporting...
# TODO exception handling both in testing and in failures....
# TODO add more clever output handling...
# 		for things like:
# 			logstr(''''
# 				print 123
# 				pprint(321)
# 			'')
# TODO add multiline things like if, for, ...
# TODO error reporting should generate something not only readable but
#      reproducable, at this poit it will print the actual result
#      rather than the expected, which will change the semantics of the
#      output...
#
#
#-----------------------------------------------------------------------
#-----------------------------------------------------------------log---
# XXX rewrite...
def log(*cmd, **kw):
	depth = kw.pop('depth', 1)
	rep = kw.pop('repr', REPR_FUNCTION)
	mute = kw.pop('mute', False)

	filename = kw.pop('filename', TEST_FILE_NAME)
	mute_prefix = kw.pop('mute_prefix', MUTE_PREFIX)

	lcl = sys._getframe(depth).f_locals
	glbl = sys._getframe(depth).f_globals
	res = None

	print ' '*(INDENT-1),
	if len(cmd) == 1: 
		if mute:
			print mute_prefix,
		print cmd[0].strip(),
		try:
			res = eval(compile(cmd[0].strip(), filename, 'eval'), glbl, lcl)
			if not mute:
				if len(cmd[0].strip()) + INDENT >= 8:
					print '\n\t->', rep(res)
				else:
					print '\t->', rep(res)
			else:
				print
		# we've got a statement...
		except SyntaxError:
			# XXX need a more robust way to do this...
			eval(compile(cmd[0].strip(), filename, 'exec'), glbl, lcl)
			print ' '
	elif len(cmd) > 1:
		if mute:
			print mute_prefix,
		for c in cmd:
			print c.strip(),
		print cmd[-1].strip(), 
		res = eval(compile(cmd[-1].strip(), filename, 'eval'), glbl, lcl)
		if not mute:
			if len(cmd[-1].strip()) + INDENT >= 8:
				print '\n\t->', rep(res)
			else:
				print '\t->', rep(res)
		else:
			print
	else:
		print
	return res


#----------------------------------------------------------------test---
def test(*cmd, **kw):
	expected, cmd = cmd[-1], cmd[:-1]
	depth = kw.pop('depth', 1)
	rep = kw.pop('repr', REPR_FUNCTION)
	res = log(depth=depth+1, *cmd)
	if res != expected:
		print '\t## Error: result did not match the expected: %s' % rep(expected)


#--------------------------------------------------------pretty_print---
##!!! revise...
# XXX this is the same as log but with pretty printing, need to
#	  redesign this to be more like a mixin to the log...
def pretty_print(*cmd, **kw):
	'''

	NOTE: this will print the value in a non-printable comment so as to be 
		  self-applicamle -- currently multiline structures are not supported.
	'''
	code = cmd[0]
	depth = kw.pop('depth', 1)
	rep = kw.pop('repr', REPR_FUNCTION)
	filename = kw.pop('filename', TEST_FILE_NAME)
	lcl = sys._getframe(depth).f_locals
	glbl = sys._getframe(depth).f_globals

	print PPRINT_PREFIX, code,
	res = pformat(eval(compile(cmd[0].strip(), filename, 'eval'), glbl, lcl), width=80-8-3)
	print '\n##\t->', '\n##\t   '.join(res.split('\n'))


#------------------------------------------------------------loglines---
def loglines(*lines, **kw):
	'''
	'''
	depth = kw.pop('depth', 1)
	mute_prefix = kw.pop('mute_prefix', MUTE_PREFIX)
	pprint_prefix = kw.pop('pprint_prefix', PPRINT_PREFIX)

	for line in lines:

		if line.strip().startswith('##'):
			continue

		if line.strip().startswith('#'):
			print (' '*INDENT) + line.strip()
			continue

		if line.strip().startswith('---'):
			print '-'*(TERM_WIDTH-1)
			continue

		if line.strip().startswith('==='):
			print '='*(TERM_WIDTH-1)
			continue

		if line.strip().startswith(pprint_prefix):
			pretty_print(line.strip()[len(pprint_prefix):], 
							depth=depth+1, 
							pprint_prefix=pprint_prefix, 
							mute_prefix=mute_prefix,
							**kw)
			continue

		if line.strip().startswith(mute_prefix):
			log(line.strip()[len(mute_prefix):], 
					depth=depth+1, 
					mute=True, 
					pprint_prefix=pprint_prefix, 
					mute_prefix=mute_prefix,
					**kw)
			continue

		if type(line) in (str, unicode):
			if line.strip() == '':
				print
				continue
			log(line, depth=depth+1, **kw)
		elif type(line) is tuple:
			test(depth=depth+1, *line, **kw)
		else:
			raise TypeError, 'unsupported line type (can handle strings and tuples, got: %s)' % type(line)
	print


#-----------------------------------------------------------loglines2---
##!!! BUG:
# XXX if '->' is somewhare inside a string in a test string then we are in trouble :)
# 	  e.g. the next line will die with a 'support only one "->" per line' error
#			'f("->") -> "some string"'
##!!! make this extend loglines rather than copy most of the functionality....
def loglines2(*lines, **kw):
	'''
	'''
	depth = kw.pop('depth', 1)
	mute_prefix = kw.pop('mute_prefix', MUTE_PREFIX)
	pprint_prefix = kw.pop('pprint_prefix', PPRINT_PREFIX)

	for line in lines:

		if line.strip().startswith('##'):
			continue

		if line.strip().startswith('#'):
			print (' '*INDENT) + line.strip()
			continue

		if line.strip().startswith('---'):
			print '-'*(TERM_WIDTH-1)
			continue

		if line.strip().startswith('==='):
			print '='*(TERM_WIDTH-1)
			continue

		if line.strip().startswith(pprint_prefix):
			pretty_print(line.strip()[len(pprint_prefix):], 
							depth=depth+1, 
							pprint_prefix=pprint_prefix, 
							mute_prefix=mute_prefix,
							**kw)
			continue

		if line.strip().startswith(mute_prefix):
			log(line.strip()[len(mute_prefix):], 
					depth=depth+1, 
					mute=True, 
					pprint_prefix=pprint_prefix, 
					mute_prefix=mute_prefix,
					**kw)
			continue

		line = line.split('->')
		if len(line) == 1:
			line = line[0]
			if line.strip() == '':
				print
				continue
			log(line, depth=depth+1, **kw)
		elif len(line) == 2:
			test(line[0], eval(line[1]), depth=depth+1, **kw)
		else:
			raise TypeError, 'support only one "->" per line'
	print


#--------------------------------------------------------------logstr---
def logstr(str, **kw):
	'''
	'''
	depth = kw.get('depth', 1)
	strs = []
	for s in str.split('\n'):
		if s.strip().startswith('->'):
			strs[-1] += s
		else:
			strs += [s]
	return loglines2(depth=depth+1, *strs)



#-----------------------------------------------------------------------
if __name__ == '__main__':
	from pprint import pprint
	logstr('''
	# this module will define a special DSL based on python. this
	# language is designed to facilitate module self-testing.
	#
	# this module can be considered as a usage example. below you see
	# the lines that both demo and test the functionality of the
	# module.

	# comments starting with a double '#' are not shown...
	## this is an example...

	# basic comment;
		# NOTE: indent is ignored...
		#       ...but this does not concern comment formatting.

	# next, a few empty lines...



	# now an expression...
	1 + 1

	# an expression with a test value...
	1 + 1 -> 2

	# we can put the expected result on a separate line...
	2 * 3
		-> 6

	# an expression that will fail it's value test...
	1 * 1 -> 2
		## this will break...


	# statements are supported too, but only if no expected result is
	# given...
	# NOTE: it is best to avoid things that print things, they will
	#       generate output that is not a valid test script.
	print '!!!'

	a = 1

	# now test we can the value...
	a 	-> 1



	# pretty printing...
	>>> {1:range(10), 2:range(10), 3:range(10)}


	# it is also possible to mute result output...
	! {1:range(10), 2:range(10), 3:range(10)}


	# now for some basic markup...
	# we can do basic lines...
	---
	===

	# NOTE: one can have more than tree dashes, but not less... two
	#		dashes will be passed to python and thus generate a syntax
	#		error.
	--------



	# that's all at this point.
	''')



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
