#=======================================================================

__version__ = '''0.0.19'''
__sub_version__ = '''20040501170358'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

from __future__ import generators

import os
import sys
import imp


#-----------------------------------------------------------------------

PY_SUFFIXES = imp.get_suffixes() 


#-----------------------------------------------------------------------
#-----------------------------------------------ImportDependencyError---
class ImportDependencyError(Exception):
	'''
	'''



#-----------------------------------------------------------------------
#--------------------------------------------------------_load_module---
# NOTE: this is a potential log/aspect point...
def _load_module(package_dir, mod_name, name_prefix=None):
	'''
	'''
	mod_dat = ()
	mod_legal_name = name_prefix in (None, '') \
						and mod_name or name_prefix + '.' + mod_name
	# import...
	try:
		# restrict the import path to avoid uncontrolled imports...
		mod_dat = imp.find_module(mod_name, [package_dir])
		# check if the module is loaded...
		if mod_legal_name in sys.modules:
			return mod_name, sys.modules[mod_name]
		# load the module...
##		module = imp.load_module(mod_name, *mod_dat)
		module = imp.load_module(mod_legal_name, *mod_dat)
		# cleanup...
		if len(mod_dat) > 1 and mod_dat[0] != None:
			mod_dat[0].close()
		return mod_name, module 
	except ImportError:
		# cleanup... (is this needed???)
		if len(mod_dat) > 1 and mod_dat[0] != None:
			mod_dat[0].close()
		return mod_name, None


#--------------------------------------------------ispythonimportable---
def ispythonimportable(package_dir, name):
	'''
	this will test if the module name is importable from package_dir.
	'''
	mod_path = os.path.join(package_dir, name)
	# is directory and contains __init__.py?
	if os.path.isdir(mod_path) and \
			True in [ os.path.exists(os.path.join(mod_path, '__init__' + ext[0])) \
					  for ext in PY_SUFFIXES ]:
		return True
	else:
		# is file -> is .py[cod]...
		return True in [ os.path.exists(os.path.join(mod_path, ext[0])) \
						 for ext in PY_SUFFIXES ]
	return False


#---------------------------------------------------------packageiter---
def packageiter(package_dir, disable_file='disabled.txt', \
				disabled_packages=None, notimportable=None, ignore_modules=()):
	'''\

	This will return importable (and enabled) package names (without importing).
	this will return the names of all packages/modules under a given path (package_dir),
	not containing the "disabled.txt" file (disable_file), one per iteration.

	optional side-effects:
		disabled_packages	: if given, will contain the names of disabled modules
							  (e.g. modules that contained the "disabled.txt" file 
							  (see above)).
		NOTE: the above two parameters MUST either be of list type or None.
	'''
	# some sanity checks...
	if disabled_packages != None and type(disabled_packages) != list:
		raise TypeError, 'disabled_packages must either be of list type or None (got type "%s").' % type(disabled_packages)
	if notimportable != None and type(notimportable) != list:
		raise TypeError, 'notimportable must either be of list type or None (got type "%s").' % type(notimportable)
	# start the work...
	loaded_packages = {}
	for mod in os.listdir(package_dir):
##		# skip __init__.*
##		if mod.startswith('__init__.'):
##			continue
		# get mod name...
		mod_name = mod.split('.', 1)[0]
		# 
		if mod_name in ignore_modules:
			continue
		# include each name only once...
		if mod_name not in loaded_packages.keys() + ['']:
			# skip disabled plugins...
			if os.path.exists(os.path.join(package_dir, mod_name, disable_file)):
				if disabled_packages != None:
					disabled_packages += [mod_name]
				continue
			if ispythonimportable(package_dir, mod_name):
				yield mod_name
			elif notimportable != None:
				notimportable += [mod_name]
##			yield mod_name


#---------------------------------------------------getpackagedepends---
def getpackagedepends(package_dir, mod_name, dependency_file='depends.txt', forbidden_chars=' -+=&*()^%$#@!~`,.'):
	'''
	'''
	# see if the dependency file exists...
	if not os.path.exists(os.path.join(package_dir, mod_name, dependency_file)):
		return []
	dep_file = open(os.path.join(package_dir, mod_name, dependency_file))
	# parse dependency file...
	deps = [ s.lstrip().split('#')[0].rstrip() \
				for s in dep_file \
				if s.split('#')[0].lstrip() != '' ]
	dep_file.close()
	# check for correctness...
	if [ s for s in deps if True in [ c in s for c in forbidden_chars ] ]:
		raise ImportDependencyError, 'dependency file format error.'
	return deps



#-----------------------------------------------------------------------
#---------------------------------------------------importpackageiter---
# TODO make this return more specific error data (e.g. name, exception,
#      traceback...).
def importpackageiter(package_dir, disable_file='disabled.txt', err_names=None,\
						disabled_packages=None, notimportable=None, \
						ignore_modules=(), name_prefix=None):
	'''\

	This is an import iterator. 
	this will import all packages/modules under a given path (package_dir),
	not containing the "disabled.txt" file (disable_file), one per iteration, and
	will return a tuple containing the module name and its object.

	optional side-effects:
		err_names			: if given, will contain the names of modules that 
							  generated ImportError.
		disabled_packages	: if given, will contain the names of disabled modules
							  (e.g. modules that contained the "disabled.txt" file 
							  (see above)).
		NOTE: the above two parameters MUST either be of list type or None.
	'''
	# some sanity checks...
	if err_names != None and type(err_names) != list:
		raise TypeError, 'err_names must either be of list type or None (got type "%s").' % type(err_names)
	# start the work...
	for mod_name in packageiter(package_dir, disable_file, disabled_packages, notimportable, ignore_modules):
		mod_name, module = _load_module(package_dir, mod_name, name_prefix)
		if module != None:
			yield mod_name, module 
		elif err_names != None:
			err_names += [mod_name]
		


#-------------------------------------------importdependspackagesiter---
# TODO make this a generic dependency checker (objutils ???)
def importdependspackagesiter(package_dir, disable_file='disabled.txt',\
								dependency_file='depends.txt', err_names=None,\
								disabled_packages=None, notimportable=None, \
								ignore_modules=(), name_prefix=None):
	'''\
	
	This will import the modules in order of dependency.
	'''
	# helper function...
	def _loaddependsiter(path, name, wait_lst, loaded_packages, err_names=None):
		'''
		'''
		if name not in loaded_packages:
			name, mod = _load_module(path, name, name_prefix) 
			if mod == None and err_names != None:
				err_names += [name]
			else:
				loaded_packages[name] = mod
				yield name, mod
		dependees = wait_lst.pop(name, [])
		for name in dependees:
			# if module does not need anything else load
			if [ m for m in wait_lst.values() if name in m ]:
				# skip...
				continue
			for n, m in _loaddependsiter(path, name, wait_lst, loaded_packages, err_names):
				yield n, m
	# start the work...
	loaded_packages = {}
	wait_lst = {}
	for mod_name in packageiter(package_dir, disable_file, disabled_packages, notimportable, ignore_modules):
		# get deps...
		deps = getpackagedepends(package_dir, mod_name, dependency_file)
		# if all dependencies are loaded load package...
		needs = [ i for i in deps if i not in loaded_packages ]
		# check if we depend on a faulty package...
		err_needs = [ i for i in needs if i in err_names ]
		if err_names != None and err_names:
			raise ImportDependencyError, 'failure in dependencies (failed: %s).' % err_names
		if needs:
			# wait list...
			for mod in needs:
				if mod in wait_lst:
					wait_lst[mod] += [mod_name]
				else:
					wait_lst[mod] = [mod_name]
		else:
			for n, m in _loaddependsiter(package_dir, mod_name, wait_lst, loaded_packages, err_names):
				yield n, m
	# check if the remainig data in wait list is looping deps...
	if wait_lst:
		# TODO do a more thorough check...
		raise ImportDependencyError, 'cyclic or unresolved demendencies in: %s.' % wait_lst



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
