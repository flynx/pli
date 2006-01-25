#=======================================================================

__version__ = '''0.1.02'''
__sub_version__ = '''20060125163912'''
__copyright__ = '''(c) Alex A. Nannou 2004'''

__doc__ = '''\
'''


#-----------------------------------------------------------------------

import os
import sys
import types

import pli.importutils as importutils
import pli.event as event
import pli.misc.extendedtypes as exttypes
import pli.misc.misc as misc


#-----------------------------------------------------------------------
#-----------------------------------------------PluginDependencyError---
class PluginDependencyError(Exception):
	'''
	'''
	pass


#--------------------------------------------------------onPluginLoad---
class onPluginLoad(event.Event):
	'''

	the callback will recive the name of the plugin package and the 
	module object....
	'''



#-----------------------------------------------------------------------
# TODO a more basic version with method callbacks intead of events...
# TODO more docs...
# TODO cleanup code...
#-------------------------------------------------------------Plugins---
class Plugins(object):
	'''
	'''
	__packageiter__ = staticmethod(importutils.packageiter)

	def __init__(self, path=None, prefix=None):
		'''
		'''
		if path == None:
			# by default get path relative to the module this was
			# called from.... (????)
			#   (e.g. import all that is on callres level...)
			i = 0
			while True:
				f_locals = sys._getframe(frame_depth+i).f_locals
				if '__file__' in f_locals:
					break
				i += 1
			path = os.path.dirname(f_locals['__file__'])
			if prefix == None:
				# the prefix is same as caller...
				 n = f_locals['__name__']
				 if n != '__main__':
					 prefix = n
		elif type(path) == types.ModuleType:
			mod = path
			# get path...
			path = os.path.dirname(mod.__file__)
			if prefix == None and mod.__name__ != '__main__':
				# get prefix...
				prefix = mod.__name__
		elif exttypes.isstring(path):
			pass
##			self.path = path
			if prefix == None:
				# normalize the path...
				f = os.path.normpath(path)
				# guess the prefix 
				# see if it is in sys.modules...
				for n, v in sys.modules.iteritems():
					if hasattr(v, '__file__') and v.__file__.startswith(f) and v.__name__ != None:
						prefix = v.__name__
						break
				# Q: is there anythong else we could do here???
				##!!!
		else:
			raise TypeError, 'the path may either be a string (or unicode), a package or None (got: %s).' % path

		self.path = path
		self.prefix = prefix
		self.plugins = {}
		##!!!
		self.sorted_plugins = None
	
	# custumization methods...
	def __getplugins__(self):
		'''
		this will get a list of loadable plugins.

		NOTE: this will override the old list.
		NOTE: this will actually import all the found modules, regardless of 
		      if they are plugins or not.
		'''
		prefix = self.prefix
		plugins = self.plugins
		plugins.clear()
		isplugin = self.__isplugin__
		for n in self.__packageiter__(self.path):
			# import the plugin...
			name = prefix + '.' + n
			##!!! correct the context...
			o = __import__(name)
			for nn in name.split('.')[1:]:
				o = getattr(o, nn)
			# check the module...
			if isplugin(o):
##				plugins[n] = o
				plugins[name] = o
		return plugins
	
	# the folowing are stubs...
	def __isplugin__(self, obj):
		'''
		this will test a plugin for compliancy.

		NOTE: this will not load the plugin.
		'''
		return True
	def __cmpplugins__(self, a, b):
		'''
		'''
		##!!!
		return 0
	# NOTE: this should call the onPluginLoad event...
	def __loadplugin__(self, plugin):
		'''
		'''
		raise NotImplementedError
	def __unloadplugin__(self, plugin):
		'''
		'''
		raise NotImplementedError

	def __sortplugins__(self):
		'''
		'''
		plugins = self.sorted_plugins = self.plugins.values()
		if plugins == []:
			return
##		plugins.sort(cmp=self.__cmpplugins__)
		##!! revise !!##
		plugins = misc.bsort(plugins, cmp=self.__cmpplugins__)
	
	# actions....
	def read(self):
		'''
		this will read the plugins, their configuration and dependencies.
		'''
		self.__getplugins__()
		self.__sortplugins__()
	# XXX do more checks... (are the plugins read before this??)
	def load(self):
		'''
		this will load the plugins in order of dependency.
		'''
		load = self.__loadplugin__
		for p in self.sorted_plugins:
			load(p)
	# XXX should the order of the unload be reversed???
	def unload(self):
		'''
		'''
		load = self.__unloadplugin__
		for p in self.sorted_plugins:
			unload(p)
	
	# interface methods...
	##!!!


#-----------------------------------------------PluginsDependencyErro---
class PluginsDependencyErro(Exception):
	'''
	'''
	pass


#---------------------------------------------PluginsWithDependencies---
class PluginsWithDependencies(Plugins):
	'''
	'''
	# NOTE: __plugindepends__ and __builddependencies__ are called
	#       AFTER all plugins are imported...	
	def __plugindepends__(self, plugin):
		'''
		this will get object dependencies.

		NOTE: this should only provide direct dependencies.
		'''
		return []
	def __builddependencies__(self):
		'''
		this will build the dependency tree.

		NOTE: this will break if a dependency loop is detected.
		'''
		res = self._dependency_cache = {}
		getdeps = self.__plugindepends__
		for plugin in self.plugins.values():
			# NOTE: here we will exclude the root from the tree...
			##!!! itertree
			deps = res[plugin] = list(itertree(plugin, getdeps))[1:]
		return res
	def __cmpplugins__(self, a, b):
		'''
		'''
		res = 0
		if b in self._dependency_cache[a]:
			res = 1
		if a in self._dependency_cache[b]:
			if res != 0:
				raise PluginDependencyError, 'cyclic dependency error (%s, %s).' % (a, b)
			res = -1
		return res
	def __sortplugins__(self):
		'''
		'''
		self.__builddependencies__()
		super(PluginsWithDependencies, self).__sortplugins__()









#-----------------------------------------------------------------------
##!!! MOVE THIS TO A SEPORATE MODULE...
#------------------------------------------------------------TreeErro---
class TreeError(Exception):
	'''
	'''
	pass


#-----------------------------------------------------------------------
WALK_DEPTH = 0
WALK_BREADTH = 1

LOOP_ERR = 0
LOOP_IGNORE = 1

#------------------------------------------------------------itertree---
def itertree(tree, getchildren=None, mode=WALK_BREADTH, onloop=LOOP_ERR):
	'''
	return a list of nodes of a tree.
	'''
	seen = [tree]
	yield tree
	l = getchildren(tree)
	while l != []:
		c = l.pop(0)
		if c in seen:
			# complain...
			if onloop == LOOP_ERR:
				raise TreeError, 'loop detected.'
			# ignore the looping branch and continue...
			if onLoop == LOOP_IGNORE:
				continue
			# sanity check...
			raise TypeError, 'unknown loop handler event code.'
		seen += [c]
		yield c
		if mode == WALK_BREADTH:
			l += getchildren(c)
		elif mode == WALK_DEPTH:
			l[:0] = getchildren(c)
		else:
			raise TypeError, 'unknown mode (%s).' % mode



#-----------------------------------------------------------------------
if __name__ == '__main__':

	t = [((1, 2), (3, (4, 5)),), 6]
##	t += [t]

	def gc(o):
		'''
		'''
		if type(o) is int:
			return []
		return list(o)

	print list(itertree(t, gc, WALK_BREADTH))
	print list(itertree(t, gc, WALK_DEPTH))




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
