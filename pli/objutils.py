#=======================================================================

__version__ = '''0.0.22'''
__sub_version__ = '''20071017141129'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import types
import new


#-----------------------------------------------------------------------
#-------------------------------------------------classinstancemethod---
##!! revise !!##
class classinstancemethod(object):
	'''

	a universal class/instance/direct method constructor/dispatcher.
	'''
	def __init__(self, func, inst_func=None, direct_func=None):
		'''
		'''
		self.func = func
		self.inst_func = inst_func != None and inst_func or func
		self.direct_func = direct_func != None and direct_func or func
	def __call__(self, *p, **n):
		'''
		'''
		# we are called directly...
		return self.direct_func(*p, **n)
	def __get__(self, obj, cls=None):
		'''
		'''
		if obj == None:
			# we are called from a class...
			return new.instancemethod(self.func, cls, type(cls))
		else:
			# we are called from an instance...
			return new.instancemethod(self.inst_func, obj, cls)
		


#-----------------------------------------------------------------------
#-----------------------------------------------------ObjectWithAttrs---
# XXX might be good to rename this... and to add method interface
#	  checking support...
# TODO add update callbacks (__attr_update_callbacks__ = {<attr>: <meth>[, ...]})
# TODO add regex attribute naming.... (e.g. if <attr> is a regexp
#	   object use it to match the attr name...)
#	   NOTE: might be good to use a predicate...
class ObjectWithAttrs(object):
	'''
	a generic object class with attribute creation an update automation.

	this class checks attribute format.
	'''
	# this defines an acl object to be used...
	__acl__ = None
	# this will restrict the attribute that can be created for this
	# object to the ones mentioned in the list (DO NOT SET HERE!).
	# value: tuple
	__attr_format__ = None
	# this defines a tuple of attributes that must be defined on object
	# init.
	# value: tuple
	__essential_attrs__ = None
##	# this defines the callbacks for attr update... (RPC only at the
##	# moment...)
##	# value: dict
##	__attr_update_callbacks__ = {}
	# if this is unset the checks will ignore all attrs that are not in
	# format...
	# TODO revise....
	__strict_attr_format__ = True
	# this will enable attribute type checking... (change for legacy
	# support only... though might be good for a speedup)
	__check_attr_types__ = True
	# this defines the values that are to be treated as "no-vals" (e.g.
	# ignored on type checks...)
	__none_values__ = ('', None)

	def __init__(self, name, attrs={}):
		'''
		create an object with attrs from a dict...
		'''
		super(ObjectWithAttrs, self).__init__(name)
		# check essential attrs....
		if hasattr(self, '__essential_attrs__') and self.__essential_attrs__ != None:
			essential_attrs = [ (type(attr) not in (str, unicode) and attr[0] or attr) \
								for attr in self.__essential_attrs__ ]
			err = []
			if False in [ attr in attrs and self._isattrwritable(attr, \
																 attrs[attr], \
																 strict=hasattr(self, '__strict_attr_format__') and self.__strict_attr_format__, \
																 format=self.__essential_attrs__) \
								or (err.append(attr), False)[-1] \
							for attr in essential_attrs ]:
				raise TypeError, 'essential attribute format mismatch in %s.' % (err,)
		self.update(attrs)
	# the isconsisten protocol...
	def __isconsistent__(self):
		'''
		check object consistency...
		'''
		return _checkarttrs(self.__dict__)
	# NOTE: this is not very efficient if more than one attr is added 
	#		in a loop (e.g. on object init)...
	def _isattrwritable(self, name, value, format=None, strict=True, message=None, none_vals=False):
		'''
		this predicate will return true if the attribute is writable.

		NOTE: this function impements error reporting a side-effect.

		the error message[s] will be appended to the message argument (if present).

		NOTE: the argument "message" must be of type list (if present).
		NOTE: the "message" argument will be modified during this functions execution.
		'''
		if format == None:
			if hasattr(self, '__attr_format__') and self.__attr_format__ != None and len(self.__attr_format__) != 0:
				format = self.__attr_format__
				##!!!
				none_vals = True
			else:
				return True 
		# cache the complex format...
		cformat = {}
		[ cformat.update({e[0]: e[1:]}) for e in format if type(e) not in (str, unicode) ]
##		# NOTE: both of the folowing are quite slow...
##		# cache the regex format...
##		rformat = []
##		# cache the predicate format...
		pformat = []
		if hasattr(self, '__check_attr_types__') and self.__check_attr_types__:
			if name not in format:
				if name in cformat:
					# get data...
					e = cformat[name]
					etype = len(e) > 0 and type(e[0]) not in (str, unicode) and e[0] or ''
					# check none_vals
					if none_vals and hasattr(self, '__none_values__') and \
							self.__none_values__ and value in self.__none_values__:
						return True
					# check type...
					try:
						if type(etype) in (str, unicode) or issubclass(type(value), etype):
							return True
					except TypeError:
						# we get here if issubclass failse when
						# comparing types with a function/lambda
						pass
					# check predicate....
					# XXX (temporary??) the predicate can only be a
					#	  function or a lambda...
##					if callable(etype):
					if type(etype) in (types.LambdaType, types.FunctionType):
						try:
							if etype(value):
								return True
						except Exception, msg:
							print '>>>', msg
							# implement the side-effect...
							if message != None:
								if type(message) != list:
									raise TypeError, 'message paramiter must be of type "list".'
								message += [msg]
						except:
							pass
				elif not strict:
					return True
				return False
		# legacy only....
		elif name not in format and name not in cformat:
				return False
		return True
	# sloooow _checkarttrs version... (uses _isattrwritable in a 
	# loop...)
	def _checkarttrs(self, attrs, errors=None, none_vals=False):
		'''
		check if attribute dict given is compatible with format (see self._isattrwritable for details...)

		NOTE: this function impements error reporting a side-effect. 

		all the the arguments that generate errors will be appended to the errors argument (if present).

		NOTE: the argument "errors" must be of type list (if present).
		NOTE: the "errors" argument will be modified during this functions execution.
		'''
		# NOTE: this is very inefficient!!!
		if errors == None:
			for name, val in attrs.items():
				if not self._isattrwritable(name, val, strict=(hasattr(self, '__strict_attr_format__') and self.__strict_attr_format__), none_vals=none_vals):
					return False
		elif type(errors) == list:
			errors[:] = []
			for name, val in attrs.items():
				if not self._isattrwritable(name, val, strict=(hasattr(self, '__strict_attr_format__') and self.__strict_attr_format__), none_vals=none_vals):
					errors += [name]
			if len(errors) > 0:
				return False
		else:
			raise TypeError, 'errors paramiter must be of type "list".'
		return True
	def update(self, attrs):
		'''
		update object attributes.

		NOTE: in strict mode this will disallow an update of non-existant
			  attributes.
		'''
		# XXX comment the folowing two lines out if __setattr__ is used...
		err = []
		if not self._checkarttrs(attrs, errors=err):
			raise AttributeError, 'can\'t update object %s, attribute format mismatch in %s.' % (self, err)
		if self.__acl__ != None:
			acl_setattr = self.__acl__.setattr
			for n, v in attrs.items():
				acl_setattr(self, n, v)
		else:
			for n, v in attrs.items():
				setattr(self, n, v)
	# the attribute interface....
	##!! test !!##
	def __setattr__(self, name, val):
		'''
		'''
		if not self._isattrwritable(name, val, strict=(hasattr(self, '__strict_attr_format__') and self.__strict_attr_format__)):
			raise TypeError, 'attribute "%s" does not comply with the format of %s object.' % (name, self)
##		self.__dict__[name] = val
		super(ObjectWithAttrs, self).__setattr__(name, val)
	def __delattr__(self, name):
		'''
		'''
		if hasattr(self, '__essential_attrs__') and self.__essential_attrs__ != None:
			if name in self.__essential_attrs__ or \
					name in [ attr[0] for attr in self.__essential_attrs__ if type(attr) not in (str, unicode) ]:
				raise TypeError, 'can not remove essential attribute "%s" of %s object.' % (name, self)
		del self.__dict__[name]
	# introspection...
	# TODO make this prittier....
	def __help__(cls):
		return cls.getattributetextformat()
	__help__ = classmethod(__help__)
	def getattributetextformat(cls):
		'''
		this will return a text definition of the attr format of obj.
		'''
		def _format_str(struct):
			res = ''
			for elem in struct:
				if type(elem) is str:
					name = elem
					atype = 'any type'
					doc = ''
				elif type(elem) in (tuple, list):
					name = elem[0]
					atype = len(elem) > 1 \
								and	(type(elem[1]) not in (str, unicode) and elem[1].__name__ or False) \
								or 'any type'
					doc = (len(elem) > 1 and type(elem[1]) in (str, unicode) and elem[1] or '') \
							+ (len(elem) > 2 and type(elem[2]) in (str, unicode) and elem[2] or '')
				res += '  %-30s : %s\n' % ('%s (%s)' % (name, atype), doc)
			return res
		# essential attrs:
		res = 'Essential Attributes:\n'
		if hasattr(cls, '__essential_attrs__') and cls.__essential_attrs__ != None:
			r = _format_str(cls.__essential_attrs__)
			res += r == '' and '  None\n' or r
		else:
			res += '  None\n'
		res += '\n'
		# attr format:
		res += 'Attribute Format:\n'
		if hasattr(cls, '__attr_format__') and cls.__attr_format__ != None:
			r = _format_str(cls.__attr_format__)
			res += r == '' and '  None\n' or r
		else:
			res += '  None\n'
		return res + '\n'
	getattributetextformat = classmethod(getattributetextformat)
	def getattributeformat(cls, name=None):
		'''
		'''
		def _format_dict(struct, target_name=None):
			res = {}
			for elem in struct:
				if type(elem) is str:
					name = elem
					atype = 'any'
					doc = ''
				elif type(elem) in (tuple, list):
					name = elem[0]
					atype = len(elem) > 1 \
								and	(type(elem[1]) not in (str, unicode) and elem[1].__name__ or False) \
								or 'any'
					doc = (len(elem) > 1 and type(elem[1]) in (str, unicode) and elem[1] or '') \
							+ (len(elem) > 2 and type(elem[2]) in (str, unicode) and elem[2] or '')
				# return type of requested attr...
				if target_name != None and target_name == name:
					return [name, atype, doc]
				res[name] = (atype, doc)
			if target_name != None:
				# if name was not found....
				return []
			return res
		# requested name...
		if name != None:
			res = []
			if hasattr(cls, '__essential_attrs__') and cls.__essential_attrs__ != None:
				res = _format_dict(cls.__essential_attrs__, name)
			if res == [] and hasattr(cls, '__attr_format__') and cls.__attr_format__ != None:
				res = _format_dict(cls.__attr_format__, name)
			return res
		# empty res...
		res = {}
		# essential attrs:
		if hasattr(cls, '__essential_attrs__') and cls.__essential_attrs__ != None:
			res['essential'] = _format_dict(cls.__essential_attrs__)
		# attr format:
		if hasattr(cls, '__attr_format__') and cls.__attr_format__ != None:
			res['format'] = _format_dict(cls.__attr_format__)
		return res
	getattributeformat = classmethod(getattributeformat)



#=======================================================================
#											 vim:set ts=4 sw=4 nowrap :
