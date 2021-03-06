#=======================================================================

__version__ = '''0.0.02'''
__sub_version__ = '''20040825195643'''
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


#-----------------------------------------------------------------------
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
	# this sets the name of the file which if found in the plugin package
	# will prevent it from being imported...
	__disable_file_name__ = 'disabled.txt'
	# this will set the filename for the file parsed for deps...
	__depends_file_name__ = 'depends.txt'
	# this is the list of modules to be ignored by the module search... 
	__ignored_modules__ = ('__init__',)
	# if this is set the plugins will be loaded on module init...
##	__autoload__ = False
	__autoload__ = True
	# this (if not None) is the event to be fired when each plugin is
	# loaded....
	__plugin_load_event__ = onPluginLoad

	def __init__(self, path=None, prefix=None, ignore=None):
		'''
		'''
		self.loaded = {}
		self.errors = []
		self.unimportable = []
		self.disabled = []

		if hasattr(self, '__autoload__') and self.__autoload__:
			self.load(path, prefix, ignore, frame_depth=2)
	# XXX revize the prefix guessing...
	def load(self, path=None, prefix=None, ignore=None, frame_depth=1):
		'''

		NOTE: path can either be a string path to the dir or a root module object...
		'''
		loaded = self.loaded
		errors = self.errors
		unimportable = self.unimportable
		disabled = self.disabled

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
##			f_locals = sys._getframe(frame_depth).f_locals
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
			self.path = path
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

##		# debug data...
##		self._path = path
##		self._prefix = prefix
##		self._ignore = ignore

		if hasattr(self, '__plugin_load_event__'):
			load_event = self.__plugin_load_event__
		else:
			load_event = None
		# the import loop....
		for name, module in importutils.importdependspackagesiter(path, \
																  self.__disable_file_name__, \
																  self.__depends_file_name__, \
																  errors, \
																  disabled, \
																  ignore_modules=(ignore == None and self.__ignored_modules__),\
																  name_prefix=prefix
																 ):
			if load_event != None:
				load_event.fire(name, module)
			loaded[name] = module
##	def reload(self):
##		'''
##		'''
##		##!!!
##		raise NotImplementedError, 'this is not yet supported...'



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
