#=======================================================================

__version__ = '''0.1.12'''
__sub_version__ = '''20040820011700'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------
__doc__ = '''\
PLI: a utility library for the Python language.

It defines a set of generic patters, aspects, utilities and tools. the 
main target of this set of tools is to assist in rapid/concise 
development (composition) of software.
'''

#-----------------------------------------------------------------------
__classifiers__ = '''\
Development Status :: 2 - Pre-Alpha
Intended Audience :: Developers
License :: OSI Approved :: BSD License
Natural Language :: English
Programming Language :: Python
'''

#-----------------------------------------------------------------------
from distutils.core import setup

try:
	import version
	__pkg_version__ = version.__version__
except ImportError:
	import os
	pkg_info = './PKG-INFO'
	ver_str = 'Version:'
	if os.path.exists(pkg_info):
		f = open(pkg_info, 'r')
		for l in f:
			if l.startswith(ver_str):
				__pkg_version__ = l.split(ver_str, 1)[-1].lstrip().rstrip()
				break
	else:
		__pkg_version__ = '0.0.00'


#-----------------------------------------------------------------------
setup(
	  name = 'pli',
      version = __pkg_version__,
	  description = __doc__.split("\n", 1)[0],
	  long_description = __doc__,
	  author = 'Alex A. Naanou',
	  author_email = 'alex_nanou@users.sourceforge.net',
	  url = 'http://pli.sourceforge.net/',
	  license = 'BSD License',
	  platforms = ['any'],
	  classifiers = filter(None, __classifiers__.split("\n")),

##	  package_dir = {'': 'pli'},
	  packages = [
				  'pli',
				  'pli.apps',
				  'pli.apps.xmlrpcserver',
				  'pli.aspect',
				  'pli.config',
				  'pli.event',
				  'pli.misc',
				  'pli.net',
##				  'pli.unit',
				  'pli.pattern',
				  'pli.pattern.proxy',
				  'pli.pattern.state',
				  'pli.pattern.store',
				  'pli.pattern.mixin',
##				  'pli.pattern.tree',
				  'pli.serialize',
				 ],
##	  py_modules = [],
	 )



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
