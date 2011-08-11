#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20110811160644'''
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

	code = '%(indent)s %(mute_prefix)s%(command)s%(result)s'
	data = {
		'indent': '',
		'mute_prefix': '',
		'command': '',
		'result': '',
	}

	data['indent'] = ' '*(INDENT-1)
	if len(cmd) == 1: 
		if mute:
			data['mute_prefix'] = mute_prefix
		data['command'] = cmd[0].strip()
		try:
			res = eval(compile(cmd[0].strip(), filename, 'eval'), glbl, lcl)
			if not mute:
				if len(cmd[0].strip()) + INDENT >= 8:
					data['result'] = '\n\t-> %s\n' % rep(res) 
				else:
					data['result'] = '\t-> %s\n' % rep(res) 
			else:
				data['result'] = '\n'
		# we've got a statement...
		except SyntaxError:
			# XXX need a more robust way to do this...
			eval(compile(cmd[0].strip(), filename, 'exec'), glbl, lcl)
			code += ' \n'
	elif len(cmd) > 1:
		if mute:
			data['mute_prefix'] = mute_prefix
		data['command'] = ''.join([c.strip() for c in cmd]) + cmd[-1].strip()
		res = eval(compile(cmd[-1].strip(), filename, 'eval'), glbl, lcl)
		if not mute:
			if len(cmd[-1].strip()) + INDENT >= 8:
				data['result'] = '\n\t->%s\n' % rep(res) 
			else:
				data['result'] = '\t->%s\n' % rep(res) 
		else:
			data['result'] = '\n'
	else:
		code += '\n'

	return code % data, res


#----------------------------------------------------------------test---
def test(*cmd, **kw):
	expected, cmd = cmd[-1], cmd[:-1]
	depth = kw.pop('depth', 1)
	rep = kw.pop('repr', REPR_FUNCTION)
	code, res = log(depth=depth+1, *cmd)
	text = code
	if res != expected:
		text += '\t## Error: result did not match the expected: %s' % rep(expected)
		return False, text
	return True, text


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

	text = '%s %s' % (PPRINT_PREFIX, code)
	res = pformat(eval(compile(cmd[0].strip(), filename, 'eval'), glbl, lcl), width=80-8-3)
	text += '%s %s' % ('\n##\t->', '\n##\t   '.join(res.split('\n')))
	return text


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
			print log(line.strip()[len(mute_prefix):], 
					depth=depth+1, 
					mute=True, 
					pprint_prefix=pprint_prefix, 
					mute_prefix=mute_prefix,
					**kw)[0]
			continue

		if type(line) in (str, unicode):
			if line.strip() == '':
				print
				continue
			print log(line, depth=depth+1, **kw)[0]
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
	only_errors = kw.pop('only_errors', False)

	for line in lines:

		if line.strip().startswith('##'):
			continue

		if line.strip().startswith('#'):
			if not only_errors:
				yield (' '*INDENT) + line.strip()
			continue

		if line.strip().startswith('---'):
			if not only_errors:
				yield '-'*(TERM_WIDTH-1)
			continue

		if line.strip().startswith('==='):
			if not only_errors:
				yield '='*(TERM_WIDTH-1)
			continue

		if line.strip().startswith(pprint_prefix):
			if not only_errors:
				yield pretty_print(line.strip()[len(pprint_prefix):], 
								depth=depth+1, 
								pprint_prefix=pprint_prefix, 
								mute_prefix=mute_prefix,
								**kw)
			continue

		if line.strip().startswith(mute_prefix):
			res = log(line.strip()[len(mute_prefix):], 
					depth=depth+1, 
					mute=True, 
					pprint_prefix=pprint_prefix, 
					mute_prefix=mute_prefix,
					**kw)[0]
			if not only_errors:
				yield res
			continue

		line = line.split('->')
		if len(line) == 1:
			line = line[0]
			if line.strip() == '':
				if not only_errors:
					yield ''
				continue
			res = log(line, depth=depth+1, **kw)[0]
			if not only_errors:
				yield res
		elif len(line) == 2:
			res, text = test(line[0], eval(line[1]), depth=depth+1, **kw)
			if not only_errors or not res:
				yield text
		else:
			raise TypeError, 'support only one "->" per line'
	yield ''


#--------------------------------------------------------------logstr---
def logstr(str, **kw):
	'''
	'''
	depth = kw.pop('depth', 1)
	strs = []
	for s in str.split('\n'):
		if s.strip().startswith('->'):
			strs[-1] += s
		else:
			strs += [s]
	print '\n'.join(l for l in loglines2(depth=depth+1, *strs, **kw))



#-----------------------------------------------------------------------
if __name__ == '__main__':
	from pprint import pprint
	test_code = '''
	# this module will define a special DSL based on python. this
	# language is designed to facilitate module self-testing.
	#
	# this module can be considered as a usage example. below you see
	# the lines that both demo and test the functionality of the
	# module.

	# comments starting with a double '#' are not shown...
	## here's is an example...

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
	#print '!!!'

	a = 1

	# now we can test the value...
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
	'''

	logstr(test_code)


	logstr('''
	===
	# and we can print only errors (see below)...
	''')


	logstr(test_code, only_errors=True)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
