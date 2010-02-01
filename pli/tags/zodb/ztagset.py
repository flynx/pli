#=======================================================================

__version__ = '''0.4.07'''
__sub_version__ = '''20091008172914'''
__copyright__ = '''(c) Alex A. Naanou 2009-'''


#-----------------------------------------------------------------------
__doc__ = '''\
this module provides ZODB persistence compatibility for tagset's
high-level containers.
'''

#-----------------------------------------------------------------------

import ZODB
import persistent

import pli.pattern.proxy.utils as putil
import pli.pattern.mixin.mapping as mapping
import pli.tags2.tagset as tagset
import pli.objutils as objutils

import zodbutils
import zset as zset



#-----------------------------------------------------------------------
#--------------------------------------------------------ZTagSetMixin---
# XXX should we inherit from persistent.Persistent here???
class ZTagSetMixin(tagset.TagSetMixin, persistent.Persistent):
	'''
	'''
	objutils.createonaccess('__tagset__', persistent.mapping.PersistentMapping)
	objutils.createonaccess('__reverse_links__', persistent.mapping.PersistentMapping)
	__stored_set_constructor__ = zset.zset


#---------------------------------------------------------ZDictTagSet---
class ZDictTagSet(mapping.DictLike, ZTagSetMixin):
	'''

	NOTE: this is almost identical to pli.tags2.tagset.DictTagSet.
	'''
	# proxy the mapping interface...
	putil.proxymethods((
			'__getitem__',
			'__setitem__',
			'__delitem__',
			'__iter__',

			# XXX should these be like this?
			'__str__',
			'__repr__',
		), '__tagset__')



#-----------------------------------------------------------------------
if __name__ == '__main__':

	##!!! make tests modular and identical to pli.tags2.tagset

	from pprint import pprint

	txt = '''
	some text that will be tagged.

	the tagging will be like this:
	- each word is an object.
	- each word is tagged with the letters that it contains.

	just in case, a tag can also be an object and vice versa.
	'''

	words = ZDictTagSet() 
	[ words.tag(w, *tuple(w)) for w in txt.split() ]


	pprint(words)
	pprint(words.all('a')['a'])
	pprint(type(words.all('a').__tagset__))

	pprint(words.any('a', 'x').tags('that'))
	pprint(words.tags('that'))

	pprint(words.any('a', 'x').tags('a'))

	pprint(words.tags('a'))

##	pprint(words.any('t', 'x').none('c'))

	pprint(words.objects())

	pprint(words.any('a').objects())

	pprint(words.tags())

	pprint(words.tags('that'))

	pprint(words.tags('t'))

	##!!! is this correct???
	pprint(words.all())

	pprint(words.relatedtags('a', 't'))

	pprint(words.relatedtags('a', 't', 'e'))

	pprint(words.relatedtags('a', 't', 'e', 'g'))

	pprint(words.relatedtags('a', 't', 'e', 'g', 'd'))
	pprint(words.all('a', 't', 'e', 'g', 'd').tags())
	pprint(words.all('a', 't', 'e', 'g', 'd').objects())

	pprint(words.all('a', 't', 'e', 'g', 'd').none('.').objects())
	pprint(words.all('a', 't', 'e', 'g', 'd').none('.', 'a').objects())


	pprint(words.all('t', 'e').tags())
	pprint(words.all('t', 'e').any('l', 'j').objects())

	# errors -- tag conflicts...
	# XXX should these err or just return empty tagsets???
	pprint(words.all('t', 'e').any('l').any('j').objects())
	pprint(words.all('t', 'e').all('l').all('j').objects())
	pprint(words.all('t', 'e').all('l').all('j').tags())
	pprint(words.all('t', 'e').all('l'))
	pprint(words.all('t', 'e').all('l').any('j'))
	pprint(words.all('t', 'e').all('l').any('j').tags())
	pprint(words.all('t', 'e').all('l').none('j').tags())
	pprint(words.all('t', 'e').all('l').all('j'))




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
