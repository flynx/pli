#=======================================================================

__version__ = '''0.0.28'''
__sub_version__ = '''20040212122352'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import re

##import acl
from pli.functional import rcurry
import pli.misc.filterlang as filterlang

##!!! REVIZE !!!##


#-----------------------------------------------------------------------
# WARNING: the selectors are quite slow!
#-----------------------------------------------------------_ls__iter---
# WARNING: this is a LL class. do not use directly...
class _ls__iter(object):
	'''
	this is a bidirectional iterator class...

	NOTE: not intended for direct use...
	'''
	def __init__(self, top):
		self._top = top
		self._position = 0
	def __iter__(self):
		return self
	def next(self):
		isaccessible = self._top._isaccesible
		end = len(self._top._slct_store)
		while self._position < end:
			if self._position < 0:
				self._position = 0
			e = self._top._slct_store[self._position]
			if self._position < end:
				self._position += 1
##					if False not in [f(e) for f in self._top._slct_filter]:
				if isaccessible(e):
					return e
			else:
				break
		raise StopIteration
	def prev(self):
		isaccessible = self._top._isaccesible
		while self._position >= 0:
			if self._position == len(self._top._slct_store):
				self._position -= 1
			e = self._top._slct_store[self._position]
			if self._position >= 0:
				self._position -= 1
##					if False not in [f(e) for f in self._top._slct_filter]:
				if isaccessible(e):
					return e
			else:
				break
		raise StopIteration


#--------------------------------------------------------ListSelector---
class ListSelector(object):
	'''
	this is a generic list selector.
	'''
##	__acl__ = None

	def __init__(self, store, *filters):
		'''
		'''
		self._slct_store = store
		self._slct_filter = filters
		self._slct_iter = self.__iter__()
		self.slct_slice_length = None
		self._slct_slice_start = 0
		self._slct_slice_end = -1
	def _isaccesible(self, obj):
		'''
		test if an object is accessible/visible through the selector...
		'''
		if False not in [f(obj) for f in self._slct_filter]:
			return True
		return False
	_ls__iter = _ls__iter
	def __iter__(self):
		'''
		'''
		return self._ls__iter(self)
	def filter(self, predicate):
		'''
		this will add a filter/predicate to the selector.

		NOTE: this will reset the selector (?).
		'''
		self.reset()
		self._slct_filter += (predicate,)
	def unfilter(self):
		'''
		this will drop all filters.
		'''
		self._slct_filter = ()
	def slice(self, length=None):
		'''
		this will set the slice size.
		if no arguments are given will set the length to maximum.
		'''
		self.slct_slice_length = length
	def next(self):
		'''
		this will return the next bunch and move the cursor to the start of the next bunch.
		'''
		res = []
		if self.slct_slice_length == None:
			# return the whole set...
			self.reset()
##			if hasattr(self, '__acl__') and self.__acl__ != None:
##				acl = self.__acl__
##				res = [ e for e in self._slct_iter if acl.isaccessible(e) and acl.isvisible(e) ]
##			else:
##				res = list(self._slct_iter)
			res = list(self._slct_iter)
			self.reset()
			return res
		try:
			i = 0
##			if hasattr(self, '__acl__') and self.__acl__ != None:
##				acl = self.__acl__
##				while i < self.slct_slice_length:
##					e = self._slct_iter.next() 
##					if acl.isaccessible(e) and acl.isvisible(e):
##						res += [e]
##						i += 1
##			else:
##				while i < self.slct_slice_length:
##					res += [self._slct_iter.next()]
##					i += 1
			while i < self.slct_slice_length:
				res += [self._slct_iter.next()]
				i += 1
		except StopIteration:
			pass
		return res
	def prev(self):
		'''
		this will return the previouse bunch and move the cursor to the start of the prev bunch.
		'''
		res = []
		if self.slct_slice_length == None:
			# return the whole set...
			self.reset()
##			if hasattr(self, '__acl__') and self.__acl__ != None:
##				acl = self.__acl__
##				res = [ e for e in self._slct_iter if acl.isaccessible(e) and acl.isvisible(e)]
##			else:
##				res = list(self._slct_iter)
			res = list(self._slct_iter)
			self.reset()
			return res
		try:
			i = 0
##			if hasattr(self, '__acl__') and self.__acl__ != None:
##				acl = self.__acl__
##				while i < self.slct_slice_length:
##					e = self._slct_iter.prev() 
##					if acl.isaccessible(e) and acl.isvisible(e):
##						res += [e]
##						i += 1
##			else:
##				while i < self.slct_slice_length:
##					res += [self._slct_iter.prev()]
##					i += 1
			while i < self.slct_slice_length:
				res += [self._slct_iter.prev()]
				i += 1
		except StopIteration:
			pass
		res.reverse()
		return res
	def reset(self):
		'''
		this will move the cursor to the start of the res.
		'''
		self._slct_iter._position = 0
	def position(self, pos=None):
		'''
		'''
		if pos != None:
			self._slct_iter._position = pos
		return self._slct_iter._position
	def isatstart(self):
		'''
		'''
		if self.slct_slice_length == None:
			return True
		return self._slct_iter._position == 0
	def isatend(self):
		'''
		'''
		if self.slct_slice_length == None:
			return True
		return self._slct_iter._position == len(self._slct_store)


#--------------------------------------------------ListSortedSelector---
# WARNING: this selector will not get auto-updated on store update!
#          use the refresh method...
# NOTE: the folowing are memory hungry!
# TODO make the sorter a mixin... (?)
class ListSortedSelector(ListSelector):
	'''
	'''
	def __init__(self, store, filters=(), sort=()):
		'''
		'''
		ListSelector.__init__(self, store[:], *filters)
		self._slct_orig_store = store
		self._slct_sort = sort
		if sort != ():
			self._slct_store.sort(self._attr_cmp)
	def reverse(self):
		'''
		'''
		self._slct_store.reverse()
		self.reset()
	def sort(self, *p):
		'''
		'''
		self._slct_sort = p
		self.reset()
		if p != ():
			self._slct_store.sort(self._attr_cmp)
	def refresh(self):
		'''
		'''
		self._slct_store = self._slct_orig_store[:]
##		self.reset()
		if self._slct_sort != ():
			self._slct_store.sort(self._attr_cmp)
	def _attr_cmp(self, a, b):
		'''
		'''
		if len(self._slct_sort) == 0:
			return cmp(a, b)
		for attr in self._slct_sort:
			pa, pb = hasattr(a, attr), hasattr(b, attr)
			if False in (pa, pb):
				return cmp(pa, pb)
			aa, ba = getattr(a, attr), getattr(b, attr)
			if aa != ba:
				return cmp(aa, ba)
		return 0


#--------------------------------------------------DictSortedSelector---
class DictSortedSelector(ListSortedSelector):
	'''
	'''
	def __init__(self, store, filters=(), sort=()):
		'''
		'''
		ListSortedSelector.__init__(self, store.values(), filters, sort)
		self._slct_orig_store = store
	def refresh(self):
		'''
		'''
		self._slct_store = self._slct_orig_store.values()
##		self.reset()
		if self._slct_sort != ():
			self._slct_store.sort(self._attr_cmp)


#----------------------------------------------DictSortedAttrSelector---
# if this flag is set the unavailable attributes will be returned as
# empty strings ('')...
RETURN_UNKNOWN_ATTRS = 1
# TODO make this a mixin... (do not inherit... wrap!)
# TODO make persistent store-specific selector sets...
class DictSortedAttrSelector(DictSortedSelector):
	'''
	'''
	# this will define a getattr-like callable to be used to access
	# stored object attributes....
	__attribute_accessor__ = None

	def __init__(self, store, filters=(), sort=(), attrs=(), flags=RETURN_UNKNOWN_ATTRS):
		'''
		'''
		DictSortedSelector.__init__(self, store, filters, sort)
		self._slct_attrs = attrs
		self._slct_flags = flags
	def attrs(self, *attrs):
		'''
		'''
		self._slct_attrs = attrs
	def _getres(self, lst):
		'''
		'''
		if hasattr(self, '__attribute_accessor__') and self.__attribute_accessor__ != None:
			__getattr = __attribute_accessor__
		else:
			__getattr = getattr
		res = []
		for e in lst:
			set = {}
			if len(self._slct_attrs) == 0:
				##!!!
				return [{} for i in lst]
			for a in self._slct_attrs:
				try:
					set[a] = __getattr(e, a)
				except AttributeError:
					if self._slct_flags&RETURN_UNKNOWN_ATTRS:
						##!!!
						set[a] = ''
			res += [set]
		return res
	def next(self):
		'''
		'''
		return self._getres(DictSortedSelector.next(self))
	def prev(self):
		'''
		'''
		return self._getres(DictSortedSelector.prev(self))


#--------------------------------DictSortedAttrSelectorWithAttrFilter---
# TODO make this a mixin... (do not inherit... wrap!)
##!! revize !!##
class DictSortedAttrSelectorWithAttrFilter(DictSortedAttrSelector):
	'''
	'''
	__private_attrs__ = (
						 '_slct_filter',	# WARNING: this attr is not safe...
						)
	if hasattr(DictSortedAttrSelector, '__private_attrs__'):
		__private_attrs__ = DictSortedAttrSelector.__private_attrs__ + __private_attrs__

	def __init__(self, store, filters={}, sort=(), attrs=(), flags=RETURN_UNKNOWN_ATTRS):
		'''
		'''
		DictSortedAttrSelector.__init__(self, store, (), sort, attrs, flags)
		# make shure we are safe...
		self.filter(filters)
	def _isaccesible(self, obj):
		'''
		'''
		if type(self._slct_filter) is dict:
			if False not in [(hasattr(obj, attr) and getattr(obj, attr) == val) \
								for attr, val in self._slct_filter.items()]:
				return True
			return False
		else:
			return self._slct_filter(obj)
	def filter(self, filters={}):
		'''
		'''
		if type(filters) is str:
			self._slct_filter = filterlang.Filter(filters)
		elif type(self._slct_filter) is not dict:
			self._slct_filter = filters
		else:
			self._slct_filter.update(filters)
	def unfilter(self):
		'''
		'''
		self._slct_filter = {}



#-------------------------------DictSortedAttrSelectorWithFancyFilter---
class DictSortedAttrSelectorWithFancyFilter(DictSortedAttrSelector):
	'''
	'''
	def __init__(self, store, filters=[], sort=(), attrs=(), flags=RETURN_UNKNOWN_ATTRS):
		'''
		'''
		DictSortedAttrSelectorWithAttrFilter.__init__(self, store, (), sort, attrs, flags)
		for f in filters:
			self.filter(f)
	def _filter_func(self, obj, code):
		'''
		'''
		exec code in {}, locals()
	def filter(self, filter_str):
		'''
		'''
		# check the filter string...
		##!!!
		# replace attrs with qualifued
		##!!!
		filter_str = filter_str.replace('@', 'obj.')
		# compile code...
		code = compile(filter_str)
		self._slct_filter += [rcurry(self._filter_func, code)]



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
