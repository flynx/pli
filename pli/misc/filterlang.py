#=======================================================================
#-----------------------------------------------------------------------

__version__ = '''0.0.06'''
__sub_version__ = '''20040212035339'''
__copyright__ = '''(c) Alex A. Naanou 2003'''



#-----------------------------------------------------------------------
##__doc__ = r'''
##
##Filter Syntax:
##
##	<filter> ::= <expr>
##	<expr> ::= <expr> == <expr> | <expr> != <expr> | <expr> <= <expr> |
##	           <expr> >= <expr> | <expr> > <expr> | <expr> > <expr> |
##               <expr> is <expr> | <expr> and <expr> | <expr> or <expr> |
##			   not <expr> | (<expr>) | <func> | <item>
##	<func> ::= <func-name>(<expr>[, <expr>[, ...]])
##	<func-name> ::= <type> | len | type | callable | isinstance | issubclass | hasattr |
##	                getattr | dir | vars
##	<item> ::= <var> | <type> | <value>
##	<type> ::= int | float | complex | str | list | tuple | dict | boolean
##	<var> ::= @[a-zA-Z_][a-zA-Z0-9_]*
##	<value> ::= <mutable-value> | <imutable-value> | <singleton-value>
##	<imutable-value> ::= [0-9]* | [0-9]*.[0-9]* | [0-9]*[.[0-9]*]e[0-9]* | ([0-9]*+[0-9]*j)
##	                     \'[^\']*\' | \"[^\"]*\" |
##						 (<expr>,[ <expr>[, ...]])
##	<mutable-value> ::= \[<expr>[, <expr>[, ...]]\] |
##	                    \{<expr>:<expr> [, <expr>:<expr>[, ...]\}
##	<singleton-value> ::= None | True | False
##
##NOTE: the above grammar does not cover complete python semantics.
##
##'''

#-----------------------------------------------------------------------

import re
##import acl

##import warnings


#-----------------------------------------------------------------------
#---------------------------------------------------------FilterError---
class FilterError(Exception):
	'''
	'''



#-----------------------------------------------------------------------
# WARNING: the Filter class was not tested for safety...
#--------------------------------------------------------------Filter---
##!! revise... (this is a litle ugly, might need some massaging...)
class Filter(object):
	'''
	'''
	# this will set the ACL lib/class to be used in the filter
	# expression... (to disable ACL use None)
	__acl_lib__ = None
	# this will set the compile mode of the filter expression, this can
	# be one of three: 'single', 'eval' or 'exec'
	__compile_mode__ = 'eval'

	def __init__(self, flt=None):
		'''
		'''
		if flt != None:
			self.compile(flt)
	def __call__(self, obj, **ns):
		'''
		'''
		try:
			if self.__compile_mode__ != 'eval':
				exec self.flt in {'__filtered_object__':obj, 'acl': self.__acl_lib__}, ns
				return ns['__flt_res__']
			return eval(self.flt, {'__filtered_object__':obj, 'acl': self.__acl_lib__}, ns) and True or False
		except:
			return False
	def compile(self, flt):
		'''
		'''
		##!!! do security...
		##!!!
		# prevent refs to external objects...
		if flt.find('__filtered_object__') != -1 or flt.find('__flt_res__') != -1:
			raise FilterError, 'filter string can not contain "__flt_res__" or "__filtered_object__".'
		self.flt_str = flt
		# set attribute and object access...
		if self.__compile_mode__ == 'eval':
			flt_cstr = ''
		else:
			flt_cstr = r'__flt_res__ = '
		##!!! check for mutable data and *update* methods....
		if self.__acl_lib__ == None:
			flt_cstr = flt_cstr \
							+ re.sub(r'(^|\s+|[^\\])@([a-zA-Z_][a-zA-Z0-9_]*)', \
									  r'\1getattr(__filtered_object__, "\2")', flt)
##									  r'\1__filtered_object__.\2)', flt)
		else:
			flt_cstr = flt_cstr \
							+ re.sub(r'(^|\s+|[^\\])@([a-zA-Z_][a-zA-Z0-9_]*)', \
									  r'\1acl.getattr(__filtered_object__, "\2")', flt)
		flt_cstr = re.sub(r'(^|\s+|[^\\])@', r'\1__filtered_object__', flt_cstr)
		self.flt_cstr = re.sub(r'\\@', r'@', flt_cstr)
		# compile...
		self.flt = compile(self.flt_cstr, '<filter_expr>', self.__compile_mode__)
	def run(self, obj, **ns):
		'''
		'''
		return self.__call__(obj, **ns)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
