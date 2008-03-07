#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20040913172511'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

from sets import Set

import pli.dispatch as dispatch
import pli.pattern.mixin.mapping as mapping
import pli.interface as interface



#-----------------------------------------------------------------------
#------------------------------------------------BasicMappingDispatch---
# this is a mapping mixin....
class BasicMappingDispatch(dispatch.BasicDispatch, mapping.BasicMapping):
	'''
	this is a mapping dispatch object.

	this provides the capability to store objects in different mappings...
	'''
	# this is a dict with keys as markers and values are arbitery
	# mappings... 
	__targets__ = None

	# basic mapping methods...
	def __getitem__(self, name):
		'''
		'''
		for v in self.__targets__.itervalues():
			if name in v:
				return v[name]
		raise KeyError, name
	def __setitem__(self, name, value):
		'''
		'''
		self.resolve(value)[name] = value
	def __delitem__(self, name):
		'''
		'''
		for v in self.__targets__.itervalues():
			if name in v:
				del v[name]
	def __iter__(self):
		'''
		'''
		for v in self.__targets__.itervalues():
			for k in v:
				yield k
	# consistensy protocol...
	def __isconsistent__(self):
		'''
		'''
		# check if we have intersecting targets...
		res = []
		[ res.append(t.keys()) for k in self.__targets__.itervalues() ]
		return len(res) == len(Set(res))
	# dispatch method...
	def resolve(self, obj):
		'''
		return the apropriate target for the given object.
		'''
		raise NotImplementedError, 'the resolve method must be implemented.'


#---------------------------------------BasicMappingInterfaceDispatch---
class BasicMappingInterfaceDispatch(BasicMappingDispatch):
	'''
	'''
	# if this is True, single interfaces as thy are returned by
	# interfaces.getinterfaces (in a tuple) will be un wrapped and
	# stored as-is...
	__unwrap_single_interfaces__ = True

	def addrule(self, marker, target):
		'''
		'''
		if hasattr(self, '__unwrap_single_interfaces__') and self.__unwrap_single_interfaces__ \
				and type(marker) in (tuple, list) and len(marker) == 1:
			marker = marker[0]
		return super(BasicMappingDispatch, self).addrule(marker, target)
	def resolve(self, obj):
		'''
		'''
		interfaces = interface.getinterfaces(obj)
		if hasattr(self, '__unwrap_single_interfaces__') and self.__unwrap_single_interfaces__ \
				and type(interfaces) in (tuple, list) and len(interfaces) == 1:
			try:
				return super(BasicMappingDispatch, self).resolve(interfaces[0])
			except dispatch.DispatchError:
				pass
		return super(BasicMappingDispatch, self).resolve(interfaces)



#=======================================================================
if __name__ == '__main__':

	class IA(interface.Interface):
		__format__ = {
						'aaa' : {
							'type': int,
							'default': 321,
						},
					 }

	class IB(IA):
		__format__ = {
						'bbb' : {
							'type': str,
							'default': '',
							'writable': True,
						},
						'*' : {
							'LIKE': 'bbb',
						},
					 }

	class A(interface.ObjectWithInterface):
		__implemments__ = IA

	class B(interface.ObjectWithInterface):
		__implemments__ = IB

	store = BasicMappingInterfaceDispatch()
	IAStore = {}
	store.addrule((IA,), IAStore)
	IBStore = {}
	store.addrule((IB,), IBStore)


	a0 = A()
	a1 = A()
	a2 = A()

	b0 = B()
	b1 = B()
	b2 = B()

	b0.xxx = '123'

	print 'b0 data: ', interface.getdata(b0)


	store['a0'] = a0
	store['a1'] = a1
	store['a2'] = a2

	store['b0'] = b0
	store['b1'] = b1
	store['b2'] = b2

	print IAStore
	print IBStore

	print store['a0'] == a0
	print store['b1'] == b1

	print 'a0' in store
	print 'b0' in store

	print [ k for k in store ]



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
