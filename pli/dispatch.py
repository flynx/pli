#=======================================================================

__version__ = '''0.1.10'''
__sub_version__ = '''20040823024309'''
__copyright__ = '''(c) Alex A. Naanou 2003'''

__thanks__ = '''
some parts of this module were inspired by the article 
	"Generalizing polymorphism with multimethods" by David Mertz

for more information see:
	<http://www-106.ibm.com/developerworks/linux/library/l-pydisp.html>
	<http://gnosis.cx/publish/programming/charming_python_b12.txt>
	<http://gnosis.cx/publish/>

David's own version of Dispatch can be found here:
	<http://gnosis.cx/download/gnosis/magic/multimethods.py>
	or in the package:
	<http://gnosis.cx/download/Gnosis_Utils-current.tar.gz>

Have Fun!

'''


#-----------------------------------------------------------------------

from __future__ import generators
from pli.functional import rcurry


#-----------------------------------------------------------------------
#-------------------------------------------------------DispatchError---
class DispatchError(Exception):
	pass



#-----------------------------------------------------------------------
#------------------------------------------------------StaticDispatch---
# NOTE: this might be a bit too straight forward...  :)
class StaticDispatch(object):
	'''
	'''
	def __init__(self, rules=None):
		'''
		'''
		if rules == None:
			self.sd_rules = {}
		else:
			self.sd_rules = rules
		super(StaticDispatch, self).__init__()
	def __call__(self, arg, *pargs, **nargs):
		'''
		'''
		return self.resolve(arg)(*pargs, **nargs)
	def resolve(self, arg):
		'''
		'''
		try:
			return self.sd_rules[arg]
		except KeyError:
			raise DispatchError, 'no matches found for "' + str(arg) + '".'
	def get_rules(self, func):
		'''
		'''
		return [ p for p, f in self.sd_rules.items() if f == func ]
	def add_rule(self, obj, func):
		'''
		'''
		if obj in self.sd_rules:
			raise DispatchError, 'rule conflict ("' + str(obj) + '").'
		self.sd_rules[obj] = func
	def del_rule(self, obj):
		'''
		'''
		del self.sd_rules[obj]


#-----------------------------------------------DynamicStrictDispatch---
##!! TEST !!##
class DynamicStrictDispatch(object):
	'''
	this is a strict dynamic dispatch class.

	all cases where there are multiple matches will raise DispatchError.
	'''
	def __init__(self):
		'''
		'''
		self.dsd_rules = {}
		super(DynamicStrictDispatch, self).__init__()
	def __call__(self, obj, *pargs, **nargs):
		'''
		'''
		res = [ f for p, f in self.dsd_rules.items() if p(obj)]
		l = len(res)
		if l > 1:
			raise DispatchError, 'multiple choices...'
		if l == 0:
			raise DispatchError, 'no matches found.'
		return res[0](obj, *pargs, **nargs)
	def add_rule(self, predicate, func):
		'''
		'''
		self.dsd_rules.update({predicate: func})
	def del_rule(self, predicate):
		'''
		'''
		del self.dsd_rules[predicate]


#-----------------------------------------------DynamicWeightDispatch---
##!! TEST !!##
class DynamicWeightDispatch(object):
	'''
	weight oriented dynamic dispatch class.

	in cases of multiple matches only the match whose predicate returns 
	the largest number (weight) will get called.
	'''
	def __init__(self):
		'''
		'''
		self.dwd_rules = {}
		super(DynamicWeightDispatch, self).__init__()
	def __call__(self, *pargs, **nargs):
		'''
		will resolve the method for the obj and exec it with the args 
		given (the object its self is the fires arg).
		'''
		# get all dwd_rules that match
		res = [ (p(*pargs, **nargs), f) for p, f in self.dwd_rules.items() ]
		l = len(res)
		if l == 0:
			raise DispatchError, 'no matches found.'
		# sort dwd_rules by weight
		res.sort()
		return res[-1][1](*pargs, **nargs)
	def add_rule(self, predicate, func):
		'''
		'''
		self.dwd_rules.update({predicate: func})
	def del_rule(self, predicate):
		'''
		'''
		del self.dwd_rules[predicate]


###------------------------------------------------DynamicMultyDispatch---
##class DynamicMultyDispatch(object):
##	'''
##	'''
##	def __init__():
##		'''
##		'''
##		pass


#-------------------------------------------------------DispatchByArg---
# TODO make a more versitile priority processimg
#                                         (manual/auto/by_model/...)
class DispatchByArg(object):
	'''
	argument oriented dispatch class.

	will resolve by argument count then type.

	rules are ordered by weight, thus the rule with the maximum weight
	is used if there is more than one match.


	rules must be of the following format:

		( (pattern, func [, weight]) [, ...] )

		e.g. a sequence of tuples.
		where:
			pattern : is a sequence of argument types
			func    : is the callable that will get called on rule match
			weight  : optional priority (default: 0)


	a predicate is the method used to process the pattern.
	the predicate must obey the following interface:

		predicate(pattern, args) -> res

		where:
			pattern : is the pattern of the rule
			args    : the arguments passed to the dispatch object
			res     : either True or False depending on fact of the match


	NOTE: in the call all keyword arguments will be ignored by the test, and
	      will be passed directly to the resolved callable.
	'''
	def __init__(self, rules=None, predicate=None):
		'''
		'''
		self.dba_rules = {}
		self.predicate = predicate
		# set the rules....
		if rules != None:
			for rule in rules:
				if len(rule) == 2:
					self.add_rule(rule[0], rule[1])
				elif len(rule) == 3:
					self.add_rule(rule[0], rule[1], rule[3])
				else:
					raise TypeError, 'bad rule format.'
		super(DispatchByArg, self).__init__()
	def __call__(self, *pargs, **nargs):
		'''
		'''
		res = self.resolve(*pargs)
		if res == None:
			raise DispatchError, 'no matches found.'
		return res(*pargs, **nargs)
	def call_iter(self, *pargs, **nargs):
		'''
		yeild the results of all matches from heigh to low priority.
		'''
		for func in self.resolve_iter(*pargs):
			yield func(*pargs, **nargs)
##	def predicate(self, pattern, args):
##		'''
##		'''
##		pass
	def resolve_iter(self, *pargs):
		'''
		yeild all the matching callables from heigh to low priority.
		'''
		if self.predicate == None:
			predicate = lambda p: False not in map(issubclass, tuple(map(type, pargs)), p[1])
		else:
			predicate = rcurry(self.predicate, pargs)
		res = filter(predicate, self.dba_rules[len(pargs)])
##		res.reverse()
##		for o in res:
##			yield o[-1]
		while 1:
			if len(res) == 0:
				return
			yield res.pop(-1)[-1]
	def resolve(self, *pargs):
		'''
		return the method that is resolved using args.
		'''
		# this might be a bit faster....
##		if self.predicate == None:
##			predicate = lambda p: False not in map(issubclass ,tuple(map(type, pargs)), p[1])
##		else:
##			predicate = rcurry(self.predicate, pargs)
##		res = filter(predicate, self.dba_rules[len(pargs)])
##		if len(res) == 0:
##			return None
##		return res[-1][-1]
		try:
			return self.resolve_iter(*pargs).next()	
		except StopIteration:
			raise DispatchError, 'no matches found.'
	# TODO make this process ranges of args...  (?)
	def get_rules(self, func, arg_count=None):
		'''
		return the list of rules (arg sets used as a rules) for the callable func.

		if arg_count is given then only sets of that length will be searched.
		'''
		# create the list
		res = []
		if arg_count == None:
			for s in self.dba_rules.values():
				res += s
				res.sort()
		else:
			res = self.dba_rules[arg_count]
		# filter the results...
		##!! is this output format correct???
##		return map(lambda e: (e[0], e[1]), filter(lambda t: t[-1] == func, res))
		return [ (e[0], e[1]) for e in res if e[-1] == func ]
	def add_rule(self, args, func, weight=0):
		'''
		'''
		if type(args) != tuple:
			raise TypeError, 'args must be a tuple.'
		la = len(args)
		rules = self.dba_rules
		if la not in rules:
			rules[la] = [(weight, args, func)]
		else:
			rules = rules[la]
			# check if we have duplicates
			if len(filter(lambda e: e[1]==args, rules)) > 0:
				raise TypeError, 'can\'t define more than one rule per argument pattern.'
			rules += [(weight, args, func)]
			rules.sort()
	def del_rule(self, args):
		'''
		'''
		l = len(args)
		self.dba_rules[l][:] = filter(lambda e: e[1]!=args, self.dba_rules[l])
		


#-----------------------------------------------------------------------
##!! TEST !!##
#------------------------------------------------DispatchByTypesNArgs---
class DispatchByTypesNArgs(StaticDispatch, DispatchByArg):
	'''
	dispatch by multiple args and/or type names.

	this is a combination of two dispatchers: StaticDispatch and DispatchByArg.
	'''
	def __init__(self):
		'''
		'''
		super(DataStoreDispatch, self).__init__()
	def __call__(self, obj, type=None, *pargs, **nargs):
		'''
		'''
		res = self.resolve(obj, type)
		if res == None:
			raise DispatchError, 'no matches found.'
		return res(obj, *pargs, **nargs)
	def resolve_iter(self, obj, type=None):
		'''
		'''
		if type != None:
			try:
				yield StaticDispatch.resolve(self, type)
				return
			except DispatchError:
				pass
		for elem in DispatchByArg.resolve_iter(self, obj):
			yield elem
	def resolve(self, obj, type=None):
		'''
		'''
		# first try by type...
		if type != None:
			try:
				return StaticDispatch.resolve(self, type)
			except DispatchError:
				pass
		# if none found use object
		try:
			return DispatchByArg.resolve(self, obj)
		except DispatchError:
			pass
		# if can't resolve err!
		raise DispatchError, 'can\'t resolve.'
	def get_rules(self, func):
		'''
		'''
		return StaticDispatch.get_rules(self, func), DispatchByArg.get_rules(self, func) 
	def add_rule(self, arg_spec=None, func=None, type_spec=None, weight=0):
		'''
		NOTE: if type is given the weight option is ignored...
		NOTE: both arg_spec and type_spec must be iterable.
		'''
		if func == None:
			raise TypeError, 'a func must be specified.'
		if (arg_spec or type_spec) is None:
			raise TypeError, 'either or both of arg_spec and type_spec must be specified!'
		if type_spec != None:
			for type in type_spec:
				StaticDispatch.add_rule(self, type, func)
		if arg_spec != None:
			DispatchByArg.add_rule(self, arg_spec, func, weight)
	##!! rewrite
##	def del_rule(self, obj=None, type=None):
##		'''
##		'''
##		if None not in (obj, type):
##			raise TypeError, 'only one rule can be deleted per call.'
##		if type != None:
##			StaticDispatch.del_rule(self, type)
##		elif obj != None:
##			DispatchByArg.del_rule(self, (obj,))
##		else:
##			raise TypeError, 'one of obj or type must be specified.'


#--------------------------------------------------DispatchByTypeNArg---
class DispatchByTypeNArgs(DispatchByTypesNArgs):
	'''
	dispatch by single type name and/or multiple args.

	this is a combination of two dispatchers: StaticDispatch and DispatchByArg.
	'''
	def add_rule(self, arg_spec=None, func=None, type_name=None, weight=0):
		'''
		NOTE: if type is given the weight option is ignored...
		note: arg_spec must be iterable.s
		'''
		if func == None:
			raise TypeError, 'a func must be specified.'
		if (arg_spec or type_name) is None:
			raise TypeError, 'either or both of arg_spec and type_name must be specified!'
		if type_name != None:
			StaticDispatch.add_rule(self, type_name, func)
		if arg_spec != None:
			DispatchByArg.add_rule(self, arg_spec, func, weight)
	##!! rewrite
##	def del_rule(self, obj=None, type=None):
##		'''
##		'''
##		if None not in (obj, type):
##			raise TypeError, 'only one rule can be deleted per call.'
##		if type != None:
##			StaticDispatch.del_rule(self, type)
##		elif obj != None:
##			DispatchByArg.del_rule(self, (obj,))
##		else:
##			raise TypeError, 'one of obj or type must be specified.'


#--------------------------------------------------DispatchByTypeNArg---
# old...
class DispatchByTypeNArg(DispatchByTypesNArgs):
	'''
	dispatch by single arg and/or type name.

	this is a combination of two dispatchers: StaticDispatch and DispatchByArg.
	'''
	def add_rule(self, obj=None, func=None, type=None, weight=0):
		'''
		NOTE: if type is given the weight option is ignored...
		'''
		if func == None:
			raise TypeError, 'a func must be specified.'
		if (obj or type) is None:
			raise TypeError, 'either or both of obj and type must be specified!'
		if type != None:
			StaticDispatch.add_rule(self, type, func)
		if obj != None:
			DispatchByArg.add_rule(self, (obj,), func, weight)
	def del_rule(self, obj=None, type=None):
		'''
		'''
		if None not in (obj, type):
			raise TypeError, 'only one rule can be deleted per call.'
		if type != None:
			StaticDispatch.del_rule(self, type)
		elif obj != None:
			DispatchByArg.del_rule(self, (obj,))
		else:
			raise TypeError, 'one of obj or type must be specified.'



#=======================================================================
#                                            vim:set sw=4 ts=4 nowrap :
