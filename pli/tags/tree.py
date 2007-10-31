#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20071031133738'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.tags.generic as generic
import pli.tags.tag as tag
import pli.tags.path as path


#-----------------------------------------------------------------------
# XXX this needs to get cleaned, partially re-written and possibly
#     split into several other modules...
# XXX might be a good idea to mirror the __getattr__ with __getitem__
#     for "bad" tag name support...
# XXX write doc and examples...
#
# TODO generate an ID for each object in store!!! (do as a mixin and
#      possibly not here...)
#
#-----------------------------------------------------------------------
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
	__object_tag__ = 'instance'

	__tagset__ = None

	##!!! need a name...
	def __init__(self, name, constructor, *tags):
		'''
		'''
		if ('constructor', name) in self.__tagset__:
			raise TypeError, 'constructor id must be unique, id "%s" already exists!' % name
		self._name = name
		self._constructor = constructor
		self._tags = tags
		# tag self...
		##!!! revise the constructor/name pair format... (use tag groups?)
		self.__tagset__.tag(self, 'constructor', name, ('constructor', name), *tags)
	# XXX would be good to add the "format" support.... (this might be
	#     too generic)
	def __call__(self, *p, **n):
		'''
		'''
		res = self.__dict__['_constructor'](*p, **n)
		self.__tagset__.tag(res, self.__object_tag__, *self._tags)
		return res



#-----------------------------------------------------------------------
class BaseTagTreePathProxy(path.RecursiveAttrPathProxy):
	'''
	'''
	def __getattr__(self, name):
		'''
		'''
		# constructor support...
		if ('constructor', name) in self._root:
			# XXX is this safe??? (constructors should be unique!)
			return tuple(self._root.select(('constructor', name)))[0]
		return super(BaseTagTreePathProxy, self).__getattr__(name)
	
	# public interface...
	# in general, this will form the args and call the corresponding
	# root methods...
	@public
	def relatedtags(self, *tags):
		'''
		'''
		return self._root.relatedtags(*self._path + tags)
	##!!! OID !!!##
	# XXX add efficient counting...
	def list(self):
		'''
		'''
		return self._root.select(generic.OBJECT_TAG, *self._path)

	##!!!
	##!!! OID !!!##
	@public
	def view(self, oid):
		'''
		view object data.
		'''
		# get the object...
		##!!!
		# get the object format...
		##!!!
		# get object data using it's format...
		##!!!
		raise NotImplementedError
	##!!!
	##!!! OID !!!##
	@public
	def update(self, oid, **attrs):
		'''
		update an object.
		'''
		# get the object...
		##!!!
		# check attrs with format... (???)
		##!!!
		# update object data...
		##!!!
		raise NotImplementedError
##	##!!! OID !!!##
##	@public
##	def delete(self, oid):
##		'''
##		delete an object.
##		'''
##		pass


#----------------------------------------------------TagTreePathProxy---
##!!! may need a more specific name...
class TagTreePathProxy(BaseTagTreePathProxy):
	'''
	'''
	@public
##	def list(self, form=None, to=None, count=None, *attrs):
	def list(self, *attrs):
		'''
		list the data form the objects in this subtree.
		'''
		res = []
		# XXX make this iterative...
##		objs = self._root.select(generic.OBJECT_TAG, *self._path)
		objs = super(TagTreePathProxy, self).list()
		for o in objs:
			##!!! the id here is a stub !!!##
##			data = {'oid': self._root._getoid(o)}
			data = {'oid': id(o)}
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
	


#-------------------------------------------------------------TagTree---
class TagTree(tag.TagSet):
	'''
	'''
	__node_path_proxy__ = TagTreePathProxy
	
	def __getattr__(self, name):
		'''
		'''
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
##		return super(TagTree, self).tag(obj, *tags)
	@public
	def relatedtags(self, *tags):
		'''
		'''
		# skip "special" constructor IDs...
		return set( t for t in super(TagTree, self).relatedtags(*tags) 
						if type(t) != tuple )




#-----------------------------------------------------------------------
if __name__ == '__main__':

	tree = TagTree()

	class constructor(NodeConstructor):
		__tagset__ = tree

	#
	class A(object):
		attr = 123
	class B(object): pass

	constructor('A', A, 'some_tag')
	constructor('B', B, 'some_other_tag')

	print tree.constructor.list()
	print
	print tree.some_tag.constructor.list()
	print
	print tree.some_tag.relatedtags()
	print
	print tree.A()
	print tree.some_tag.A()
	print tree.some_tag.constructor.A()
	print tree.B()
	print tree.some_other_tag.constructor.B()
	print
	print tree.instance.list('attr', '__class__')
	print
	print tree.some_tag.instance.list()
	print
	print tree.some_other_tag.list()
	print
	print tree.relatedtags()
	print tree.some_other_tag.relatedtags()
		


#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
