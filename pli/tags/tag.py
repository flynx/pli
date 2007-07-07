#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20070707230607'''
__copyright__ = '''(c) Alex A. Naanou 2007'''


#-----------------------------------------------------------------------

import re

import pli.pattern.mixin.mapping as mapping
import pli.pattern.proxy.utils as putils


#-----------------------------------------------------------------------
# XXX might be a good idea to transfer these to sets...
# XXX add class tagging...
#----------------------------------------------------------------Tags---
##!!! make this clean... (all set methods should work as expected)
class Tags(set):
	'''
	'''
	def __init__(self, obj, tagdb):
		'''
		'''
		self.__tagdb__ = tagdb
		self._obj = obj
	##!!! add support for tag chains...
	def addtags(self, *names):
		'''
		'''
		tagdb = self.__tagdb__
		Tag = tagdb.__tag_constructor__
		for name in names:
			if type(name) in (str, unicode):
				# skip multiple tags...
				if name in self:
					continue
				if name not in tagdb:
					t = Tag(name, tagdb)
				else:
					t = tagdb[name]
				t.tagged.update([self._obj])
				tagdb.tagged.update([self._obj])
				self.update([name])
			elif type(name) in (list, set):
				raise NotImplementedError, 'tag chains are not yet suported...'
			else:
				raise TypeError, 'unsopported tag type of %s (%s)' % (name, type(name))
	##!!! add support for tag chains...
	##!!! do we remove unused tag objrcts???
	def removetags(self, *names):
		'''
		'''
		tagdb = self.__tagdb__
		for name in names:
			if type(name) in (str, unicode):
				if name not in tagdb:
					raise TypeError, 'can\'t remove a non-existant tag "%s".' % name
				else:
					t = tagdb[name]
				if name not in self:
					raise TypeError, 'not tagged by "%s"' % name
				self.remove(name)
				if self._obj in t.tagged and name not in self:
					t.tagged.remove(self._obj)
				if len(self) == 0:
					tagdb.tagged.remove(self._obj)
				##!!! do we remove unused tags???
			elif type(name) in (list, set):
				raise NotImplementedError, 'tag chains are not yet suported...'
			else:
				raise TypeError, 'unsopported tag type of %s (%s)' % (name, type(name))



#-----------------------------------------------------------------------
#------------------------------------------------------------Taggable---
# XXX make this inherit tags form the class...
class Taggable(object):
	'''
	'''
	__tagdb__ = None

	tags = None

	def tag(self, *names):
		'''
		'''
		if self.tags == None:
			self.tags = Tags(self, self.__tagdb__)
		self.tags.addtags(*names)
	def untag(self, *names):
		'''
		'''
		if self.tags == None and names != ():
			raise TypeError, 'no tags to remove.'
		self.tags.removetags(*names)


#-------------------------------------------------TaggableWithDFLTags---
class TaggableWithDFLTags(Taggable):
	'''
	'''
	__dfl_tags__ = None

	def __init__(self, *p, **n):
		'''
		'''
		self.inherittags()
		super(TaggableWithDFLTags, self).__init__(*p, **n)
	def inherittags(self):
		'''
		'''
		tags = self.__dfl_tags__
		if type(tags) in (list, set, tuple):
			self.tag(*tags)



#-----------------------------------------------------------------Tag---
##class Tag(Taggable):
class Tag(TaggableWithDFLTags):
	'''
	'''
	# all tags are tagged with the "tag" tag by default...
	__dfl_tags__ = (
			'tag',
			)

	def __init__(self, name, tagdb, *p, **n):
		'''
		this will avoid the creation of duplicate tags in one tag db...
		'''
		self.__tagdb__ = tagdb
		tagdb[name] = self
		self.name = name
		self.tagged = set()
		super(Tag, self).__init__(name, tagdb, *p, **n)



#-----------------------------------------------------------------------
#-----------------------------------------------------------getbytags---
# NOTE: this should be quite fast as the main work-hourses here a
#       builtin types...
def getbytags(tagdb, *tags, **opts):
	'''
	retrun all the objects from tagdb that are tagged with the given tags.

	if no tags are given, this will return all the objects.

	if a keyword argument "exclude" is given, it's value is used as tags by 
	which objects will be excluded form the results.

	NOTE: excusion may be slow compared to clean incusive search.
	'''
	if 'exclude' in opts:
		exclude = set(opts['exclude'])
		if len(set(tags).intersection(exclude)) > 0:
			raise TypeError, 'inclusion and exclusion tags intersect in: %s.' \
					% (tuple(set(tags).intersection(exclude)),)
	else:
		exclude = set()
	if not set(tags).union(exclude).issubset(tagdb):
		raise TypeError, 'all given tags must be valid (not tags: %s).' \
				% (tuple(set(tags).union(exclude).difference(tagdb)),)

	tags_left = list(tags)
	res = set(tagdb.tagged)

	while len(tags_left) > 0:
		tag = tagdb[tags_left.pop(0)]
		res = set(tag.tagged).intersection(res)

	if len(exclude) > 0:
		for o in res.copy():
			if len(o.tags.intersection(exclude)) > 0:
				res.remove(o)
	return res


#----------------------------------------------------------iterbytags---
# XXX think of a better way to do this... (inificient memory-wise)
def iterbytags(tagdb, *tags, **opts):
	'''
	iterate through all the objects from tagdb that are tagged with the given tags.

	if no tags are given, this will return all the objects.

	if a keyword argument "exclude" is given, it's value is used as tags by 
	which objects will be excluded form the results.

	NOTE: excusion may be slow compared to clean incusive search.
	'''
	if 'exclude' in opts:
		exclude = set(opts['exclude'])
		if len(set(tags).intersection(exclude)) > 0:
			raise TypeError, 'inclusion and exclusion tags intersect in: %s.' \
					% (tuple(set(tags).intersection(exclude)),)
	else:
		exclude = set()
	if not set(tags).union(exclude).issubset(tagdb):
		raise TypeError, 'all given tags must be valid (not tags: %s).' \
				% (tuple(set(tags).union(exclude).difference(tagdb)),)

	tags_left = list(tags)
	res = set(tagdb.tagged)

	# XXX this may consume quite a bit of memory... (the whole inclusive 
	#	  set of data will live through the lifespan of the iterator)
	while len(tags_left) > 0:
		tag = tagdb[tags_left.pop(0)]
		res = set(tag.tagged).intersection(res)

	if exclude != None:
		for o in res:
			if len(o.tags.intersection(exclude)) == 0:
				yield o


#-----------------------------------------------------------------------
#---------------------------------------------------------------TagSet---
# this is the tag database...
class TagSet(mapping.Mapping):
	'''
	'''
	__tag_constructor__ = Tag
	# all the objects that are tagged...
	tagged = None

	def __init__(self, tagdb=None, *tags):
		'''
		'''
		self._parent = tagdb
		if tagdb == None:
			self.tagged = set()
			self._data = {}
			for t in tags:
				self.__tag_constructor__(t, self)
		else:
			available = set()
			for o in iterbytags(tagdb, *tags):
				available = available.union(o.tags)

			self.tagged = getbytags(tagdb, *tags)
			if available == ():
				self._data = dict([ (k, v) for k, v in tagdb.items() ])
			else:
				self._data = dict([ (k, tagdb[k]) for k in available ])
	##!!! might be good to check for tag type here...
	def __setitem__(self, name, value):
		'''
		'''
		if name in self:
			raise TypeError, 'no duplicate tags allowed ("%s").' % name
		self._data[name] = value

	putils.proxymethods(
		(
			'__getitem__',
			'__delitem__',
			'__contains__',
			'__iter__',
		),
		'_data'
	)
	iterbytags = iterbytags
	getbytags = getbytags


#------------------------------------------------TagSetWithAttrAccess---
class TagSetWithAttrAccess(TagSet):
	'''
	'''
	__tagname__ = re.compile('^[a-zA-Z][a-zA-Z0-9_]*$')


	def __setitem__(self, name, value):
		'''
		'''
		if not self.isvalidtagname(name):
			raise TypeError, 'bad tag name ("%s").' % name
		return super(TagSetWithAttrAccess, self).__setitem__(name, value)
	def __getattr__(self, name):
		'''
		'''
		return self.__class__(self, name)

	def isvalidtagname(self, tag):
		'''
		'''
		if self.__tagname__.match(tag):
			return True
		return False




#-----------------------------------------------------------------------
if __name__ == '__main__':

##	tdb = TagSet()
	tdb = TagSetWithAttrAccess(None, 'xxx', 'yyy')

	class A(TaggableWithDFLTags):
		'''
		'''
		__tagdb__ = tdb
		__dfl_tags__ = (
				'object',
				)

		def __init__(self, n):
			'''
			'''
			self.name = n
			super(A, self).__init__(n)

	a = A('aaaa')
	b = A('bbbb')
	c = A('cccc')

	a.tag('a')
	b.tag('a', 'x', 'y')
	print a.tags
	print b.tags

	b.untag('y')

	print b.tags

	print

	print tdb.keys()
	print tdb['a']
	print [o.name for o in tdb['a'].tagged]

	print

	print tdb
	print tdb['tag'].tagged

##	# duplicate tags are not allowed...
##	Tag('tag', tdb)

	print

	print [o.name for o in getbytags(tdb)]
	print [o.name for o in getbytags(tdb, 'a')]
	print [o.name for o in getbytags(tdb, 'tag')]
	print [o.name for o in getbytags(tdb, 'object')]
	print [o.name for o in getbytags(tdb, 'object', 'a')]
	print [o.name for o in getbytags(tdb, 'object', 'a', 'x')]
	print [o.name for o in getbytags(tdb, 'object', 'a', 'x', 'tag')]

	print [o.name for o in tdb.iterbytags('object', 'a', exclude=('x',))]
	print
	print [o.name for o in tdb.iterbytags(exclude=('tag',))]


	print 

	print tdb.keys()
	print [o.name for o in tdb.tagged]
	print tdb.object.keys()
	print [o.name for o in tdb.object.tagged]
	print tdb.object.a.x.keys()
	print [o.name for o in tdb.object.a.x.tagged]





#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
