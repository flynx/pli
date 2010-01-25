#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20100125185504'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import sys
from pprint import pprint, pformat


#-----------------------------------------------------------------------

INDENT = 2
TERM_WIDTH = 80

TEST_FILE_NAME = '<test>'
REPR_FUNCTION = repr


#-----------------------------------------------------------------------
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
#
#
#-----------------------------------------------------------------------
#-----------------------------------------------------------------log---
# XXX rewrite...
def log(*cmd, **kw):
	depth = kw.pop('depth', 1)
	rep = kw.pop('repr', REPR_FUNCTION)
	filename = kw.pop('filename', TEST_FILE_NAME)
	mute = kw.pop('mute', False)
	lcl = sys._getframe(depth).f_locals
	glbl = sys._getframe(depth).f_globals
	res = None
	print ' '*(INDENT-1),
	if len(cmd) == 1: 
		if mute:
			print '!',
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
			print '!',
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

	print '>>>', code,
	res = pformat(eval(compile(cmd[0].strip(), filename, 'eval'), glbl, lcl), width=80-8-3)
	print '\n##\t->', '\n##\t   '.join(res.split('\n'))


#------------------------------------------------------------loglines---
def loglines(*lines, **kw):
	'''
	'''
	depth = kw.pop('depth', 1)
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

		if line.strip().startswith('>>>'):
			pretty_print(line.strip()[3:], depth=depth+1)
			continue

		if line.strip().startswith('!'):
			log(line.strip()[1:], depth=depth+1, mute=True, **kw)
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

		if line.strip().startswith('>>>'):
			pretty_print(line.strip()[3:], depth=depth+1)
			continue

		if line.strip().startswith('!'):
			log(line.strip()[1:], depth=depth+1, mute=True, **kw)
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
	## comments starting with a double '#' are not shown...
	# basic comment;
		# NOTE: indent is ignored...
		#       ...but this does not concern comment formatting.
	# next a few empty lines...



	# now an expression...
	1 + 1

	# an expression with a test value...
	1 + 1 -> 2

	# we can put the expected result on a separate line...
	2 * 3
		-> 6

	# an expression that will fail it's value test...
	1 * 1 -> 2

	# statements are supported too, but only if no expected value is
	# passed...
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

	# NOTE: one can have more than tree dashes, but not less...
	--------


	
	# that's all at this point.
	''')



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
