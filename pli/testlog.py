#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20110913175458'''
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
	'''
	'''
	depth = kw.pop('depth', 1)
	rep = kw.pop('repr', REPR_FUNCTION)
	mute = kw.pop('mute', False)

	filename = kw.pop('filename', TEST_FILE_NAME)
	mute_prefix = kw.pop('mute_prefix', MUTE_PREFIX)

	lcl = sys._getframe(depth).f_locals
	glbl = sys._getframe(depth).f_globals
	res = None
	err = None

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
			##!!! add exception handling...
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
			##!!! add exception handling...
			eval(compile(cmd[0].strip(), filename, 'exec'), glbl, lcl)
			code += ' \n'
		# we've got an exception...
		except Exception, e:
			err = e
			# XXX figure out a better syntax to represent exceptions...
			data['result'] = '\n\t-X-> %s\n' % rep(err) 
	elif len(cmd) > 1:
		if mute:
			data['mute_prefix'] = mute_prefix
		data['command'] = ''.join([c.strip() for c in cmd]) + cmd[-1].strip()
		##!!! add exception handling...
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

	return code % data, res, err


#----------------------------------------------------------------test---
def test(*cmd, **kw):
	expected, cmd = cmd[-1], cmd[:-1]
	expected_err = kw.pop('expected_err', None)
	depth = kw.pop('depth', 1)
	rep = kw.pop('repr', REPR_FUNCTION)
	code, res, err = log(depth=depth+1, *cmd)

	##!!! for some reason, if we have an exception, we do not reach this spot...

	if err is not None:
		if expected_err is None:
			raise err
		if expected_err == err:
			##!!! stub...
			res = err
		##!!! stub...
		res = err
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
	##!!! add exception handling...
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

	line_count = 0
	lines_failed = 0

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
			line_count += 1
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
			line_count += 1
			res = log(line, depth=depth+1, **kw)[0]
			if not only_errors:
				yield res
		elif len(line) == 2:
			line_count += 1
			##!!! add exception handling...
			res, text = test(line[0], eval(line[1]), depth=depth+1, **kw)
			if not res:
				lines_failed += 1
			if not only_errors or not res:
				yield text
		else:
			raise TypeError, 'support only one "->" per line'
	yield ''

	yield {
		'lines': line_count, 
		'fails': lines_failed,
	}


#--------------------------------------------------------------logstr---
def logstr(text, **kw):
	'''
	'''
	depth = kw.pop('depth', 1)
	stats = kw.pop('print_stats', True)

	strs = []
	for s in text.split('\n'):
		if s.strip().startswith('->'):
			strs[-1] += s
		else:
			strs += [s]
	for l in loglines2(depth=depth+1, *strs, **kw):
		if type(l) not in (str, unicode):
			if stats and l['lines'] > 0:
				print (' '*INDENT) + '## executed %(lines)s lines, of which %(fails)s failed.' % l
		else:
			print l



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

	a = 1

	# now we can test the value...
	a 	-> 1

	# we can also test for fails...
	1/0

	1/0
##		-X-> ZeroDivisionError


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

	# and we can print only errors (same code as up to this point
	# re-run with errors_only option set)...
	'''

	logstr(test_code, print_stats=False)

	# enable only error printing...
	logstr(test_code + '''\n\t# we can also print exec stats...''',
			print_stats=True, only_errors=True)

	logstr('''
	---

	# statements are supported too, but only if no expected result is
	# given...
	# NOTE: it is best to avoid things that print things, they will
	#       generate output that is not a valid test script.
	print '!!!'


	# oh, and did I mention that logstr is self-applicable? 
	# ...well it is! that is if you avoud mixing the code with prints ;)


	# that's all at this point.
	''')



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
