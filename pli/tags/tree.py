#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20100201014206'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.tags.tagset as tagset
import pli.tags.path as path

import pli.objutils as objutils
import pli.pattern.mixin.mapping as mapping

##import oid


#-----------------------------------------------------------------------
# XXX this needs to get cleaned, partially re-written and possibly
#     split into several other modules...
# XXX write doc and examples...
#
# TODO generate an ID for each object in store!!! (do as a mixin and
#      possibly not here...)
# TODO add support for different format tagchains...
#
#-----------------------------------------------------------------------
##!!! move somewhere and revise !!!##
def getoid(obj):
	'''
	'''
	return 'OID_%s' % str(id(obj)).replace('-', 'X')


#--------------------------------------------------------------public---
##!!! STUB
def public(meth):
	'''
	'''
	return meth


#-----------------------------------------------------------------------
#-----------------------------------------------------NodeConstructor---
# object constructor wraper...
# - when created will register and tag itself.
# - will proxy to the original constructor and tag the resulting object.
class NodeConstructor(object):
	'''
	'''
	# most likely will not need to be changed manualy...
##	__object_tags__ = ('instance',)
	__object_tags__ = ()

	__tagset__ = None

	type = 'constructor'

	# XXX move the defaults out of the code...
	def __init__(self, name, constructor, *tags):
		'''
		'''
##		if ('constructor', name) in self.__tagset__:
		chain = self.__tagset__.tags2chain('constructor', name)
		if chain in self.__tagset__:
			raise TypeError, 'constructor id must be unique, id "%s" already exists!' % name
		self.constructor_name = name
		self._constructor = constructor
		self._tags = tags
		# tag self...
		##!!! revise the constructor/name pair format... (use tag groups?)
		self.__tagset__.tag(self, 'constructor', name, chain, *tags)
	# XXX would be good to add the "format" support.... (this might be
	#     too generic)
	def __call__(self, *p, **n):
		'''
		create an object.
		'''
		res = self.__dict__['_constructor'](*p, **n)
		self.__tagset__.tag(res, *(self.__object_tags__ + self._tags))
		return res
	def __getattr__(self, name):
		'''
		'''
		return getattr(self._constructor, name)


#-----------------------------------NodeConstructorWithOIDReturnMixin---
##!!! IMO this functionality should be in the serializer... (if can't 
##!!! serialize an object then return it's OID...)
class NodeConstructorWithOIDReturnMixin(object):
	'''
	'''
	def __call__(self, *p, **n):
		'''
		'''
		return {'oid': getoid(super(NodeConstructorWithOIDReturnMixin, self).__call__(*p, **n))}


#------------------------------------NodeConstructorWithCallbackMixin---
class NodeConstructorWithCallbackMixin(object):
	'''
	'''
	# defines the name of the inteface method called when the object is
	# created.
	# signature:
	# 	<method-name>(oid, tagset, tags)
	__node_constructor_callback_name__ = '__ontreenodecreate__'

	def __call__(self, *p, **n):
		'''
		'''
		res = super(NodeConstructorWithOIDReturnMixin, self).__call__(*p, **n)
		# call the interface method...
		if hasattr(res, self.__node_constructor_callback_name__):
			getattr(res, self.__node_constructor_callback_name__)(getoid(res), self.__tagset__, self.__object_tags__ + self._tags)
		return res



#----------------------------------------------DynamicNodeConstructor---
class DynamicNodeConstructor(NodeConstructor):
	'''
	'''
	def __init__(self, tagset, name, constructor, common_tags=(), object_tags=()):
		'''
		'''
		self.__tagset__ = tagset
		self.__object_tags__ = object_tags

		super(DynamicNodeConstructor, self).__init__(name, constructor, *common_tags)

	def __getstate__(self):
		'''
		'''
		return self.__dict__
	def __setstate__(self, state):
		'''
		'''
		self.__dict__.update(state)

#---------------------------------DynamicNodeConstructorWithOIDReturn---
##!!! does this need to get reorgonized?
class DynamicNodeConstructorWithOIDReturn(NodeConstructorWithOIDReturnMixin, DynamicNodeConstructor):
	'''
	'''
	pass


#------------------------DynamicNodeConstructorWithOIDReturnNCallback---
class DynamicNodeConstructorWithOIDReturnNCallback(NodeConstructorWithCallbackMixin, 
													NodeConstructorWithOIDReturnMixin, 
													DynamicNodeConstructor):
	'''
	'''
	pass


#-----------------------------------------------------------------------
#----------------------------------------------------TagTreePathProxy---
# XXX add direct interface...
class TagTreePathProxy(path.RecursiveAttrPathProxy):
	'''
	'''
	def __getattr__(self, name):
		'''
		'''
		if name.startswith('OID_'):
			return self._getobject(name)
		chain = self._root.tags2chain('constructor', name)
		if chain in self._root:
##			return [ o for o in self._root.all(chain, self._root.__object_tag__).objects()
##						if o != self._root.__tag_tag__][0]
			# XXX is this safe??? ...can this return anything other
			#     than the constuctor?
			return self._root.all(chain, self._root.__object_tag__).objects().pop()
		return super(TagTreePathProxy, self).__getattr__(name)
##	__getitem__ = __getattr__
	
	# public interface...
	# in general, this will form the args and call the corresponding
	# root methods...
	@public
	def relatedtags(self, *tags):
		'''
		'''
		return self._root.relatedtags(*self._path + tags)
	@public
	def chains(self, *tags):
		'''
		'''
		return self._root.chains(*self._path + tags)
	##!!! OID !!!##
	# XXX add efficient counting...
	# XXX split this into two levels... one to return objects and
	#     another to format them into attrs... (???)
	@public
##	def list(self, form=None, to=None, count=None, *attrs):
	def list(self, *attrs):
		'''
		list the data form the objects in this subtree.
		'''
		res = []
		# XXX make this iterative...
		objs = self._root.all(self._root.__object_tag__, *self._path)
		for o in objs:
			##!!! the id here is a stub !!!##
##			data = {'oid': self._root._getoid(o)}
##			data = {'oid': 'OID_%s' % str(id(o)).replace('-', 'X')}
			data = {'oid': getoid(o)}
			res += [data]
			for a in attrs:
				# skip the oid as we added it already...
				if a == 'oid':
					continue
				# skip attrs that do not exist in the object...
				if not hasattr(o, a):
					continue
				# XXX this is a good spot for ACL check...
				data[a] = getattr(o, a)
		return res
	
	# object interface...
	def _getobject(self, oid):
		'''
		'''
		##!!! STUB... do a better direct object by oid select !!!##
		objs = self._root.all(self._root.__object_tag__, *self._path)
		for o in objs:
			##!!! the id here is a stub !!!##
##			if ('OID_%s' % str(id(o)).replace('-', 'X')) == oid:
			if getoid(o) == oid:
				return o
		raise TypeError, 'non-existant object id: %s' % oid
	
	# shorthand object interface...
	@objutils.classinstancemethod
	def view(self, oid, *attrs):
		'''
		'''
		return self._getobject(oid).view(*attrs)
	def update(self, oid, **attrs):
		'''
		'''
		return self._getobject(oid).update(**attrs)
	

#----------------------------------------TagTreePathProxyMappingMixin---
# XXX make this a tad more efficient...
class TagTreePathProxyMappingMixin(mapping.Mapping):
	'''
	'''
	def __getitem__(self, name):
		'''
		'''
		return self._getobject(name)
	def __setitem__(self, name, val):
		'''
		'''
		raise NotImplementedError
	def __delitem__(self, name):
		'''
		'''
		raise NotImplementedError
	def __iter__(self):
		'''
		'''
		for o in self.list():
			yield o['oid']


#---------------------------------------------TagTreePathProxyMapping---
# XXX add exclude support...
class TagTreePathProxyMapping(TagTreePathProxyMappingMixin, TagTreePathProxy):
	'''
	'''
	##!!! need to see of part of the path is a constructor and return that...
	def __getattrpath__(self, root, path):
		'''
		'''
		res = root
		for p in path:
			##!!! need to see of p is a constructor name...
			res = res[p]
		return res



#--------------------------------------------------------TagTreeMixin---
##!!!! not yet very picklable...
class TagTreeMixin(tagset.AbstractTagSet):
	'''
	'''
	# this is needed here as the attr proxy try and get it othewise...
	# ...another way to go is add an exception to the .__getattr__
	# method, explicitly raising attrerror when this is not here...
##	__stored_set_constructor__ = None

	__node_path_proxy__ = TagTreePathProxyMapping
	
	def __getattr__(self, name):
		'''
		'''
		# support pickle...
		##!!! automate this... (might be a good idea to put this into path.py)
		if name.startswith('__') and name.endswith('__'): 
			return getattr(super(TagTreeMixin, self), name)
		return getattr(self.__node_path_proxy__(self, ()), name)

##	##!!! for type-checking to work need to split the tag method into two:
##	##!!! one for internal use and one "public"...
##	@public
##	def tag(self, obj, *tags):
##		'''
##		'''
##		for t in tags:
##			if type(t) not in (str, unicode):
##				raise TypeError, 'tag type must be str, got %s.' % type(t)
##		return super(TagTreeMixin, self).tag(obj, *tags)
	@public
	def relatedtags(self, *tags):
		'''
		'''
		# skip "special" constructor IDs...
		return set( t for t in super(TagTreeMixin, self).relatedtags(*tags) 
						if type(t) != tuple )


#-------------------------------------------------------------TagTree---
##class TagTree(TagTreeMixin, tagset.TagSet):
class TagTree(TagTreeMixin, tagset.DictTagSet):
	'''
	'''
	__stored_set_constructor__ = set

##	def __getstate__(self):
##		'''
##		'''
##		return 1
##	def __setstate__(self, state):
##		'''
##		'''
##		pass



#-----------------------------------------------------------------------
# XXX this can be considered app-level code... most likely should be
#     elsware...
#--------------------------------------------------BaseTagTreeHandler---
class BaseTagTreeHandler(object):
	'''
	this provides administrative tree handling, without affecting the tree itself.
	'''
	__tree_constructor__ = None
	__node_constructor_wrapper__ = None

	__constructor_tags__ = ()
	__instance_tags__ = ()

	tree = None

	# XXX might be good to be able to thread some args to the tree
	#     constructor...
	def __init__(self, constructor_tags=(), instance_tags=()):
		'''
		'''
		self.__constructor_tags__ += constructor_tags
		self.__instance_tags__ += instance_tags

		self.tree = self.__tree_constructor__()
	def constructor(self, name, constructor, 
			constructor_tags=(), 
			instance_tags=(), 
			ignore_default_constructor_tags=False, 
			ignore_default_instance_tags=False):
		'''
		create a custom constructor.
		'''
		# construct tag lists...
		if ignore_default_constructor_tags:
			c_tags = constructor_tags
		else:
			c_tags = self.__constructor_tags__ + constructor_tags 
		if ignore_default_instance_tags:
			i_tags = instance_tags
		else:
			i_tags = self.__instance_tags__ + instance_tags 
		# do the call...
		return self.__node_constructor_wrapper__(
								self.tree, 
								name, 
								constructor, 
								common_tags=c_tags, 
								object_tags=i_tags)


#------------------------------------------------------TagTreeHandler---
class TagTreeHandler(BaseTagTreeHandler):
	'''
	'''
	__tree_constructor__ = TagTree
##	__node_constructor_wrapper__ = DynamicNodeConstructor
##	__node_constructor_wrapper__ = DynamicNodeConstructorWithOIDReturn
	__node_constructor_wrapper__ = DynamicNodeConstructorWithOIDReturnNCallback

	# XXX this is currently not needed as the NodeConstructor class 
	#     takes care of this internally.... (should be customisable!)
##	__constructor_tags__ = ('constructor',)
	__instance_tags__ = ('instance',)

	# XXX this is currently not needed as the NodeConstructor class 
	#     takes care of this internally.... (should be customisable!)
##	def constructor(self, name, constructor, constructor_tags=(), instance_tags=()):
##		'''
##		'''
##		return super(TagTreeHandler, self).constructor(
##							name, 
##							constructor, 
##							(name, ('constructor', name)) + constructor_tags, 
##							instance_tags)



#-----------------------------------------------------------------------
if __name__ == '__main__':

	from pli.testlog import logstr

	handler = TagTreeHandler()
	tree = handler.tree
	
	def constructor(name, constructor, *tags):
		return handler.constructor(name, constructor, tags)


	class A(object):
		attr = 123
	class B(object):
		pass

	logstr('''
	# creating constructors...
	constructor('A', A, 'some_tag')
	constructor('B', B, 'some_other_tag')

	>>> tree.constructor.list()
	
	>>> tree.some_tag.constructor.list()
	
	>>> tree.some_tag.relatedtags()
	
	tree.A
	tree.A()
	tree.some_tag.A()
	tree.some_tag.constructor.A()
	tree.B()
	tree.some_other_tag.constructor.B()
	
	>>> tree.instance.list('attr', '__class__')
	
	>>> tree.some_tag.instance.list()
	
	>>> tree.some_other_tag.list()
	
	>>> tree.relatedtags()
	>>> tree.some_other_tag.relatedtags()

	tree.addtags('xxx', 'yyy')
	tree.xxx.keys()

	AA = constructor('X', A, 'fff:ggg')
	tree.X()

	tree['fff:ggg']

	tree['fff']


##	##!!! pickle does not seem to work with recursive references... (2.5.1-specific?)
##	import pickle
##
##	class X(object): pass
##
##	x = X()
##
##	d = {'x':x}
##	x.d = d
##	print d
##	print pickle.dumps(d)

	import cPickle as pickle

	s = pickle.dumps(tree)

	ss = pickle.dumps(tree.some_tag)

	AA

	sss = pickle.dumps(AA)

	''')


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
