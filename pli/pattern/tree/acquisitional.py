#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20050411063117'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.pattern.mixin.mapping as mapping
import pli.pattern.proxy.generic as proxy
import pli.logictypes as logictypes


#-----------------------------------------------------------------------
# TODO rename this module to something like acquisitional.py
# TODO parant resolution protocol (if not present use attr).
# TODO acquisition cut (mignt be done by the above...)
# TODO might be good to do a recursive depth iterator...
# TODO path modification and resolution priority...
# TODO wrap the return of __getitem__
#      - add context data (for both the origin (?) and current 
#        contexts)
# TODO revise the module structure...
#
#
# AbstractAcquisitionalNode				- create, resolve up, basic proto, mixin
#	AbstractAcquisitionalNodeMapping	- mapping, mixin
#		BasicNodeMapping				- specific, config, mixin
#			Directory (fs mixin)
#			...
#	BasicNode							- specific, config, mixin
#		File (fs mixin)
#		...
#	BasicNodeReference					- mixin
#		NodeContextProxy				- mixin, basic proto
#
#
# TODO make this an instance of AbstractTreeNode...
class AbstractAcquisitionalNode(object):
	'''
	'''
	pass


class AcquisitionalNodeMixin(AbstractAcquisitionalNode):
	'''
	'''
	def __acquire__(self):
		'''
		'''
		parent = getattr(self, 'parent', None)
		if parent != None:
			yield parent
			for o in parent.__acquire__():
				yield o


#-----------------------------------------------------------BasicNode---
class BasicNode(AcquisitionalNodeMixin):
	'''
	'''
##	parent = None

	def __init__(self, parent, name, *p, **n):
		'''
		'''
		self.__name__ = name
##		self.parent = None
		if parent != None:
			self.parent = parent
			parent.children[name] = self
##			self.parent = None
		self.children = {}


#--------------------------------------------------BasicNodeReference---
##!!! REWRITE !!!##
class BasicNodeReference(BasicNode, proxy.InheritAndOverrideProxy):
	'''
	'''
	##!!!!! FIND A BETTER (MORE GENTLE) WAY TO DO THIS !!!!!##
	# TODO avoid duble writes...
	def __init__(self, target, parent, name, *p, **n):
		'''
		'''
		# NOTE: the way the __init__ is called is a workaround pythons
		#       type check on first arg of method...
		# NOTE: the class is passed up to avoid changing the targets
		#       state (NS).
		BasicNode.__dict__['__init__'](self.__class__, parent, name, *p, **n)
		# this is to correcting a little side-effect... (in the above
		# code we passed the class, thus it is registred as a child,
		# not the original rarget...)
		# TODO avoid duble writes...
		if hasattr(self, 'parent') and self.parent != None:
			self.parent.children[name] = self
##		self.parent.children[name] = self


#------------------------------------------------------ProxyNameSpace---
class ProxyNameSpace(logictypes.WritableDictUnion, dict):
	'''
	'''
	__modify_props__ = logictypes.GET_LOCAL_FIRST \
						| logictypes.WRITE_LOCAL \
						| logictypes.DELETE_FIRST


#----------------------------------------------------NodeContextProxy---
class NodeContextProxy(BasicNode, proxy.InheritAndOverrideProxy):
##class NodeContextProxy(BasicNode, proxy.TransparentInheritAndOverrideProxy):
	'''
	'''
##	__proxy_public_attrs__ = proxy.TransparentInheritAndOverrideProxy.__proxy_public_attrs__ \
##			+ (
##					'parent',
##			  )

	##!!!!! FIND A BETTER (MORE GENTLE) WAY TO DO THIS !!!!!##
	# TODO avoid duble writes...
	def __init__(self, target, context, *p, **n):
		'''
		'''
##		self.__dict__ = ProxyNameSpace(self.__dict__) 
##		BasicNode.__dict__['__init__'](self.__class__, getattr(context, 'parent', None), self.__name__, *p, **n)
		self.__class__.parent = context


#----------------------------------------------------BasicNodeMapping---
class BasicNodeMapping(BasicNode, mapping.Mapping):
	'''
	'''
	__node_reference_class__ = BasicNodeReference

	def __getitem__(self, name):
		'''
		'''
		return self.children[name]
	# WARNING: this will cause proxy nesting...
	def __setitem__(self, name, value):
		'''
		'''
		if isinstance(value, BasicNode):
			BasicNodeReference(value, self, name)
		else:
			self.children[name] = value
	def __delitem__(self, name):
		'''
		'''
		del self.children[name]
	def __iter__(self):
		'''
		'''
		return self.children.__iter__()


#----------------------------------------------BasicAcquisitionalNode---
class BasicAcquisitionalNode(BasicNodeMapping):
	'''
	'''
	# signature:
	# 	__context_wrapper__(cur_context, res)
##	__context_wrapper__ = None
	__context_wrapper__ = NodeContextProxy
	# WARNING: be ware of acquisition loops!
	# TODO resolve acquisition loops...
	def __getitem__(self, name):
		'''
		'''
		wrapper = getattr(self, '__context_wrapper__', None)
		try:
			if wrapper == None:
				return super(BasicAcquisitionalNode, self).__getitem__(name)
			else:
				return wrapper(super(BasicAcquisitionalNode, self).__getitem__(name), self)
		except KeyError:
			if self.parent == None:
				raise
			if wrapper == None:
				return self.parent[name]
			else:
				return wrapper(self.parent[name], self)


#-----------------------------------------------------------------------
if __name__ == '__main__':
	import pickle

	# test node creation...
	root = BasicAcquisitionalNode(None, 'root')

	BasicAcquisitionalNode(root, 'a')

	BasicAcquisitionalNode(root, 'b')
	BasicAcquisitionalNode(root, 'c')

	# test node access...
	BasicAcquisitionalNode(root['a'], 'x')
	BasicAcquisitionalNode(root['a'], 'y')
	BasicAcquisitionalNode(root['a'], 'z')

	print '''root['a']'''
	print root['a']
	print '''root['a']['x']'''
	print root['a']['x']
	print '''root['a']['x']['b']'''
	print root['a']['x']['b']
	print '!!!!!!!'
	print root['a']['x']['b']
	print '''root['b']'''
	print root['b']
	print '''root['b']['a']['x']['b']'''
	print root['b']['a']['x']['b']

	print 

##	for n in root['b']['a']['x']['b']['a'].__acquire__():
##		print n.__name__, '/',


	# test direct node assignment...
	root['c']['123'] = 123
	root['c']['root'] = root

	print

	print root
	print root['c']['root']

##	print root.parent
	print root['c']['root'].parent

	print

	print root['c']['root']['b']['a']['x']['b']

	root['b']['rrr'] = root['c']['root']

	print root['b']['rrr']['b']['a']['x']['b']

	print root['c']['root'].parent

##	for n in root['b']['rrr']['b']['a']['x'].__acquire__():
##		print n.__name__, '/', 

	root2 = pickle.loads(pickle.dumps(root))

	# test node removal....
	del root['b']['rrr']

	# test for possible del side-effects...
	print root['c']['root'].parent
	print root['c']

	print
	print

	# raw pickle test...
##	root2 = pickle.loads(pickle.dumps(root))

	print root2['a']
	print root2['a']['x']
	print root2['a']['x']['b']
	print root2['b']
	print root2['b']['a']['x']['b']
	print root2['c']['root']['b']['a']['x']['b']
	print root2['b']['rrr']['b']['a']['x']['b']
	print root2['c']['root'].parent
	print root2['c']








#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
