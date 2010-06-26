#=======================================================================

__version__ = '''0.4.07'''
__sub_version__ = '''20100626165718'''
__copyright__ = '''(c) Alex A. Naanou 2009-'''


#-----------------------------------------------------------------------
__doc__ = '''\
This module implements a basic object tagging engine.

This involves tag manipulation (tagging and untagging) and tag based 
searches. 

In this system there is almost no distinction between the tag and the 
tagged object, other than that they are tagged by two different system 
tags: "tag" and "object". Both are stored in the same store and treated 
alike. There are also no restrictions to the format of either tag
or the tagged object, though it is recommended for the tags to be
str/unicode objects, so as to harness some optimisations within Python
and supporting libraries.

There are also basic structural consistency verification and restoration
routines implemented here.



The Tag Store
-------------

A dict-compatible object used to store objects and tags.

Semantics:
	A key is an entity that "relates" to it's values.

	for tags we say that the key tags it's values.

	When the object is tagged, the whole chain (including the object)
	is treated as a set of related tags. The tag is recorded as a key
	and the rest are recorded in a set as a value to that key. This is
	done for each tag in the given set.

	NOTE: for tags the relation is asymmetrical.

Results:
	+ trivial and fast search.
	+ trivial, though not the fastest addition, and essentially no
	  need for balancing (unless the store is tampered with manually).
	- redundant linkage within the tag store.


NOTE: there is no distinction between tagged abjects and tags other
      than the two special tags "tag" and "object". They are both
      treated the same and stored in one structure.
NOTE: the system tags are configurable.


Container structure:
	{ 
		<tag>: set([
			<tag>,
			...]),
		...
		<object>: set([]),
		...
	}



Selectors
---------

A selector is a means of filtering the data in the store. 

There are two types of selectors: 
	- concatenative, returning tagsets, and
	- non-concatenative returning direct data.


Selector operations:
	tagset.all(*tags) -> tagset
		select items where each is tagged with ALL of the given tags.

	tagset.any(*tags) -> tagset
		select items where each item is tagged with ANY (at least one)
		of the given tags. 

	tagset.none(*tags) -> tagset
		select items where each item is NOT tagged with any of the given
		tags.

	tagset.tags([object]) -> set
		select the tags tagging the object.
		
		if no object is given then return all the tags.

	tagset.objects() -> set
		select all the object in the current tagset.

	tagset.relatedtags(*tags) -> set
		select the tags related to the given. 
		
		related tags are those that also tag the seletced objects.

		i.e. tags sutable for further specialization via .all(...)


	tagset.chains(*tags) -> set
		XXX

	tagset.chainrelated(*tags) -> set
		XXX

	tagset.chain2tags(chain) -> list
		XXX

	tagset.tags2chain(*tags) -> str
		XXX

NOTE: concatinative selectors also filter tags (XXX need to describe this
	  in more detail!)



General notes
-------------

It is expected that the number of tags will grow far slower than the 
number of objects (after stabilizing the objects in a live system
will exhibit linear growth, while tags will almost plateau at some point).

In this approach, the number of objects will be extremely large.

The two sub-groups (tags and objects) have slight differences. Tags
tend to be highly interlinked while objects rarely exhibit linkage
with each other.

Most searches will be tag oriented, possibly with a final filtration
by tag or object.

The current architecture favors concatenative selectors, this each selector
will construct a new store of the same type as the parent.


'''

#-----------------------------------------------------------------------

import copy

import pli.objutils as objutils


#-----------------------------------------------------------------------
#
# XXX need tagchain support!!! (used by tree)
#
#
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# TODO add an iterative select that goes good on memeory (different
#      algorithm)...
# TODO make the TAG_TAG and OBJECT_TAG tags optional and/or 
#      confugurable...
#      the problem here is the lack of ability to control these tags;
#      in cases it might be usefull to be able to add a third system
#      tag or remove one...
#      ....this may be done as a seporate layer
# TODO use None instead of an empty set for keys that still have no
#      relations...
#
#
#-----------------------------------------------------------------------
#------------------------------------------------------------TagError---
class TagError(Exception):
	pass



#-----------------------------------------------------------------------
#-----------------------------------------------------AbstractLinkSet---
class AbstractLinkSet(object):
	'''
	'''
	__stored_set_constructor__ = None
	__tagset__ = None


#------------------------------------------------------AbstractTagSet---
class AbstractTagSet(AbstractLinkSet):
	'''
	'''
	__tag_tag__ = 'TAG'
	__object_tag__ = 'OBJECT'

##	__reverse_links__ = None
	objutils.createonaccess('__reverse_links__', dict)



#-----------------------------------------------------------------------
#--------------------------------------------------------LinkSetMixin---
class LinkSetMixin(object):
	'''
	'''
	# XXX shows signs of exponential time increase on very large sets of
	#     data... need to revise.
	# XXX this may go bad with a very large number of args...
	def link(self, obj, *objs):
		'''
		link the given objects.
		'''
		tagdb = self.__tagset__
		tt = [obj] + list(objs)
		tdbset = self.__stored_set_constructor__

		for t in set(tt):
			# remove one occurrence of self...
			tt_c = tt[:]
			tt_c.remove(t)

			if t in tagdb:
				tagdb[t].update(tt_c)
			else:
				tagdb[t] = tdbset(tt_c)
		return self
	def unlink(self, obj, *objs):
		'''
		remove the links between objects.

		NOTE: if an element is present more than once then remove the self link too.
		NOTE: this will not remove orphaned tags.
		'''
		tagdb = self.__tagset__
		tt = [obj] + list(objs)

		for t in tt:
			if t not in tagdb:
				# ignore invalid tags... (XXX should we complain here?)
				continue
			# remove one occurrence of self...
			tt_c = tt[:]
			tt_c.remove(t)
			# remove the reqired tags...
			tagdb[t].difference_update(tt_c)
			# remove tag if it has no relations... (XXX)
			if len(tagdb[t]) == 0:
				del tagdb[t]
		return self
	def links(self, obj):
		'''
		return all the links to the object.

		NOTE: this is the same as tagdb[obj].
		'''
		tagdb = self.__tagset__
##		# sanity check...
##		if obj not in tagdb:
##			raise KeyError, 'object %s not in tagdb (%s).' % (obj, tagdb)
		return tagdb[obj]


#---------------------------------------------------------BasicTagSetMixin---
##!!! revise...
class BasicTagSetMixin(AbstractTagSet):
	'''
	defines basic taging operations.
	'''
	def addtags(self, *tags):
		'''
		add empty tags to tag store.
		'''
		tag_tag = self.__tag_tag__
		tagdb = self.__tagset__
		tdbset = self.__stored_set_constructor__
		for tag in tags:
			if tag not in tagdb:
				tagdb[tag] = tdbset()
				# XXX should this tag the tag with __tag_tag__???
				self._tag(tag, tag_tag)
	def _tag(self, obj, *tags):
		'''
		raw version of the tag(...). this does not enforce the use of system tags.

		WARNING: not recommended for direct use.
		'''
		tagdb = self.__tagset__
		revlinks = self.__reverse_links__
		tdbset = self.__stored_set_constructor__
		# add tags...
		for t in tags:
			if t not in tagdb:
				tagdb[t] = tdbset()
			tagdb[t].add(obj)
		# add object to db...
		if obj not in tagdb:
			tagdb[obj] = tdbset()
		# add reverse links...
		if obj not in revlinks:
			revlinks[obj] = tdbset()
		revlinks[obj].update(tags)
		return self
	def tag(self, obj, *tags):
		'''
		tag an object...

		this maintains two special tags:
			tag_tag		: tags all the tags (self.__tag_tag__).
			object_tag	: tags all the objects (self.__object_tag__).

		NOTE: neither the "object" nor the "tag" tags are user modifiable. 
		'''
		tag_tag = self.__tag_tag__
		obj_tag = self.__object_tag__
		tagdb = self.__tagset__
		# do special tags...
		# can't manually use the tag and object tags...
		if tag_tag in tags or obj_tag in tags or obj in (tag_tag, obj_tag):
			raise TypeError, 'can\'t use either "object" or "tag" tags manually.'
		# the tag tag...
		for t in tags:
			if tag_tag not in tagdb.get(t, ()):
				self._tag(t, tag_tag)
		# XXX two loops is not good... may be a good idea to make _tag an
		#     iterator/generator....
		self._tag(obj, *tags)
		# the object tag...
		if obj_tag not in tagdb.get(obj, ()):
			self._tag(obj, obj_tag)
			if tag_tag not in tagdb.get(obj_tag, ()):
##				self.link(tag_tag, tag_tag)
				self._tag(tag_tag, tag_tag)
		return self
	def untag(self, obj, *tags):
		'''
		remove the tag relation.
		'''
		tag_tag = self.__tag_tag__
		obj_tag = self.__object_tag__
		tagdb = self.__tagset__
		revlinks = self.__reverse_links__
		# do special tags...
		# can't manually use the tag and object tags...
		if tag_tag in tags or obj_tag in tags or obj in (tag_tag, obj_tag):
			raise TypeError, 'can\'t use either "object" or "tag" tags manually.'
		# now remove the links...
		revlinks[obj].difference_update(tags)
		for tag in tags:
			tagdb[tag].remove(obj)
		return self


#--------------------------------------------TagSetBasicSelectorMixin---
# XXX possible hack: the obj_tag is not tagged as a tag.... 
class TagSetBasicSelectorMixin(AbstractTagSet):
	'''
	'''
	def tags(self, obj=None):
		'''
		return the tags tagging the object.

		NOTE: this removes all the relations that are not tags.
		NOTE: without arguments this will return all available tags.
		'''
		tag_tag = self.__tag_tag__
		obj_tag = self.__object_tag__
		tagdb = self.__tagset__
		if tag_tag not in tagdb:
			return set()
		if obj is None:
			# XXX possible hack: the obj_tag is not tagged as a tag.... 
			return tagdb[tag_tag].copy().union((obj_tag,))
		return self.__reverse_links__[obj].intersection(tagdb[tag_tag].union([obj_tag]))
	##!!! revise...
	def relatedtags(self, *tags):
		'''
		return the related tags to the given.

		two tags are related if they both tag the same object. thus this will 
		return the tags suitable for further specialization.

		NOTE: to get all the objects use "select(tagdb, tag, tags, __object_tag__)"
			  with the same tags...
		'''
		obj_tag = self.__object_tag__
		tagdb = self.__tagset__
		revlinks = self.__reverse_links__
		# get all the valid data...
		objs = self.all(*tags).objects()
		res = set()
		# gather all the related tags...
		for o in objs:
			res.update(revlinks[o])
		# remove the objects and input tags...
		res.difference_update((obj_tag,) + tags + tuple(objs))
		return res
##	# XXX should this be a prop?
##	@property
	def objects(self):
		'''
		return all the objects in the current tagset.
		'''
		object_tag = self.__object_tag__
		tagset = self.__tagset__
		if object_tag in tagset:
			return tagset[object_tag].copy()
		return set()



#----------------------------------------------------TagSetUtilsMixin---
##!!! make this reverse-link-aware...
# XXX add rebuilding of reverse-links 
class TagSetUtilsMixin(TagSetBasicSelectorMixin):
	'''

	NOTE: this needs to be mixed in with BasicTagSetMixin.
	'''
	def _rebuild_system_tags(self, other):
		'''
		'''
		other_tagdb = other.__tagset__
		tagdb = self.__tagset__
		# rebuild system tags...
		tagdb[self.__tag_tag__] = set( t for t in other_tagdb[other.__tag_tag__] 
											if t in tagdb 
												or t == other.__tag_tag__ ) 
		tagdb[self.__object_tag__] = set( t for t in other_tagdb[other.__object_tag__] 
											if t in tagdb 
												or t == other.__object_tag__ ) 
		return self
	def _rebuild_reverse_links(self, other):
		'''
		'''
		self.__reverse_links__ = self.__reverse_links__.__class__( (k, v.intersection(self)) for k, v in other.__reverse_links__.items() 
											if k in self ) 
		return self

	def istagsconsistent(self):
		'''

		a store is consistent if:
		- all tags in relations are present in store keys.
		- if no orphan tags are allowed (???) each tag in keys MUST also be
		  present in relations (related to).
		- if all relations are symetrical.
		'''
		for i in self.itertaggaps():
			# if we get in here, it means that we have a problem...
			return False
		return True
	##!!! make this reverse-link-aware...
	def itertaggaps(self):
		'''
		find store inconsistencies and return the conflicting keys and relations.

		this can not detect the folowing:
			- missing orphaned keys (no data).
			- interlinking between missing keys (no data).
			- inconsistencies in relations (no way to destinguish this from
			  good data).
		'''
		tagdb = self.__tagset__
		keys = set(tagdb.keys())
		for tag, rel in tagdb.items():
			# XXX ignore orphans... (to check for them use strict equality)
			# check for gaps (missing tagdb keys)...
			if not keys.issuperset(rel):
				yield tag, rel.difference(keys)
			# check for missing symetric relations...
##			##!!! can this be faster? ...is there a better algorithm?
##			for r in rel:
##				if r not in tagdb or tag not in tagdb[r]:
##					##!!! this may return duplicate with the above data...
##					yield tag, set([r])
	# XXX should this restore the tag to self??
	# TODO make this an interactive generator so as to have more control 
	#      over what is fixed and how...
	##!!! make this reverse-link-aware...
	def filltaggaps(self):
		'''
		fix inconsistencies using the data returned by itertaggaps.

		NOTE: this will restore the data that can be detected and restored 
			  only (no domain semantic checks are made at this level).
		NOTE: this is maximalistic. will fill the holes rather than cut off 
			  the excess.
		'''
		# NOTE: this is split in two so as to not iterate and modify the
		#       store at the same time...
		tagdb = self.__tagset__
		tdb_diff = {}
		tdbset = self.__stored_set_constructor__
		# build the diff correcting the errors...
		for key, dif in self.itertaggaps():
			for k in dif:
				if k in tdb_diff:
					tdb_diff[k].update((key,))
				else:
					tdb_diff[k] = tdbset((key,))
		# apply the diff created above...
		for k, rel in tdb_diff.items():
			# add a link to self (XXX this should be in _iter_store_gaps)
			rel.update((k,))
			if k in tagdb:
				tagdb[k].update(rel)
			else:
				tagdb[k] = rel
		# return the diff...
		return tdb_diff
	def removetaggaps(self):
		'''
		'''
		ts = self.__tagset__
		for key, dif in self.itertaggaps():
			ts[key].difference_update(dif)
	def iterorphans(self):
		'''
		iterate orpahed tags.
		'''
		obj_tag = self.__object_tag__
		tag_tag = self.__tag_tag__
		tagdb = self.__tagset__
		for k, v in tagdb.items():
			if v == None or len(v.difference((tag_tag, obj_tag))) == 0:
				# XXX do we need this check???
				##!!! is .tags needed here???
				if len(self.tags(k).difference((tag_tag, obj_tag))) == 0:
					yield k
	def gc(self):
		'''
		interactive garbage collector.

		this will iterate through the orphans and remove them.

		to skip the removal send the string 'skip' to the generator instance.

		Example:
			
			g = gc(tagdb)

			for tag in g:
				if 'a' in tag:
					g.send('skip')


		WARNING: this will remove orphaned tags and objects. this list will
				 include tags added by addtags(..) but not yet used.
		'''
		tag_tag = self.__tag_tag__
		tagdb = self.__tagset__
		for tag in self.iterorphans():
			if (yield tag) != 'skip':
				del tagdb[tag]
				# cleanup the tags...
				if tag in tagdb[tag_tag]:
					tagdb[tag_tag].remove(tag)


#-----------------------------------------------------TagSetDictMixin---
class TagSetDictMixin(AbstractTagSet):
	'''
	'''
	# proxy all data access to self.
	__tagset__ = property(fget=lambda s: s)

	objutils.createonaccess('__reverse_links__', dict)


#-----------------------------------------------------TagSetInitMixin---
class TagSetInitMixin(AbstractTagSet):
	'''
	'''
	objutils.createonaccess('__tagset__', dict)


#-----------------------------------------------------------------------
# all basic tag selectors should return tagsets...
# XXX this is really ugly, need to revise/rewrite...
##!!! this needs to be a mapping -- constructor interface...
class TagSetSelectorMixin(TagSetUtilsMixin):
	'''
	'''
	##!!! should these in case of tag conflicts return empty tagsets or just err?
	def _all(self, *tags):
		'''
		selects all objects tagged with all the tags.
		'''
		tagdb = self.__tagset__
		# if no tags are given return evrything we've got! :)
		if len(tags) == 0:
			return set()
		# a small optimisation: order the tags to intersect out as mach as
		# possible as early as possible... (XXX check for better strategies)
		l = list(tags)
		l.sort(lambda a, b: cmp(len(tagdb[a]), len(tagdb[b])))
		# first cross the biggest and smallest...
		tag, tags = l[0], l[1:]
		# now do the real work...
		visited = set(l)
		res = set(tagdb[tag])
		# this does the folowing:
		# - for each tag select all the tagged objects.
		# - intersect the set with the tagged objects of each of the next tags.
		# - remove all the tags of the path (XXX not sure if this should be
		#   done at this stage...)
		for t in tags:
			res.intersection_update(tagdb[t])
		return res.difference(visited)
	##!!! on coflict this produces a result not containing system tags (tagset.__init__ problem)...
	def all(self, *tags):
		'''
		all that are tagged with all of the tags.
		'''
		tags = set(tags)
		ts = self.__tagset__
		try:
			intersection = self._all(*tags)
			# build a result tagset...
			res = self.__class__([ (k, ts[k].copy()) 
											for k in ts.keys()
											if k in intersection 
												or len(ts[k].intersection(intersection)) > 0 ])
		except KeyError:
##			raise TagError, 'tag "%s" not present in current tagset.' % t
			return self.__class__()
		res._rebuild_system_tags(self)
		res._rebuild_reverse_links(self)
		res.removetaggaps()

		return res
	##!!! this loses all the tags but the ones given as args...
	def any(self, *tags):
		'''
		all that are tagged with any of the tags.
		'''
		# take only the tags present in self and ignore the rest...
		# XXX should we err if a tag s not present??
		tags = set(tags).intersection(self)
		ts = self.__tagset__

		objects = set()
		[ objects.update(ts[t]) for t in tags ]

		res = self.__class__([ (k, ts[k].copy()) 
										for k in ts.keys()
										if k in tags 
											or len(tags.intersection(ts[k])) > 0
											or k in objects ])
##												or ts[k].issubset(objects) ])

		res._rebuild_system_tags(self)
		res._rebuild_reverse_links(self)
		res.removetaggaps()

		return res
	##!!! still needs fixing: produces orphans...
	def none(self, *tags):
		'''
		all that are tagged with none of the tags.
		'''
		tags = set(tags)
		ts = self.__tagset__

		objects = set()
		[ objects.update(ts[t]) 
			# skip tags not present in self...
			for t in tags.intersection(self) ]

		# NOTE: if a tagset is inconsistent, i.e. some tags are not
		# 		present in keys bot still tag an object that object
		# 		will get cut out...
		# 		XXX this might be a good place to err...
		res = self.__class__([ (k, ts[k].copy()) 
										for k in ts.keys() 
										if (k not in tags
												and len(tags.intersection(ts[k])) == 0
												and k not in objects)
											or not ts[k].issubset(objects) ])

		res._rebuild_system_tags(self)
		res._rebuild_reverse_links(self)
		res.removetaggaps()

		return res

		


#---------------------------------------------------------TagSetMixin---
class TagSetMixin(BasicTagSetMixin, TagSetSelectorMixin, TagSetUtilsMixin):
	'''
	'''
	pass



#-----------------------------------------------------------------------
# tagchian mechanics...
# XXX move this to a different module...
#--------------------------------------------TagSetWithTagChainsMixin---
# XXX do we need chain-specific select???
##!!! revise !!!##
##class TagSetTagChainMixin(LinkSetMixin):
class TagSetTagChainMixin(object):
	'''
	a chain is a tuple of tags.

	the tag chain structure is as follows:

		title <------->	Terminator
		   \			   /
			\			  /
			 \			 /
			  v			v
			(title, Terminator)

	- all the chain elements tag the chain (all-one).
	- all chain elements are linked (all-all).

	NOTE: this must be mixed with a valid tagset.
	NOTE: by default the chains are represented as tuples.
	'''
	# the tag tagging the tagchains...
	# NOTE: if this is None, do not tag chains
	__chain_tag__ = 'TAGCHAIN'

	# tag interface...
	def addtags(self, *tags):
		'''
		'''
		tags, chains = self._splitchains(tags)
		# process chains...
		self._addchains(*chains)
		super(TagSetTagChainMixin, self).addtags(*tags)
		##!!! return??
	def tag(self, obj, *tags):
		'''
		'''
		tags, chains = self._splitchains(tags)
		self._addchains(*chains)
		return super(TagSetTagChainMixin, self).tag(obj, *(tags+chains))
	def _tag(self, obj, *tags):
		'''
		'''
		tags, chains = self._splitchains(tags)
		self._addchains(*chains)
		return super(TagSetTagChainMixin, self)._tag(obj, *(tags+chains))
	# XXX this may be usefull for garbage collection...
##	def untag(self, obj, *tags):
##		'''
##		'''
##		tags, chaintags, chains = self._splitchains(tags)
##		# XXX process chains...
##		##!!!
##		super(TagSetTagChainMixin, self).untag(obj, *tags)
##		##!!! return??
	# chain-specific helpers...
	def _ischain(self, tag):
		'''
		test if a tag is tagchain compatible.
		'''
		if type(tag) is tuple:
			return True
		return False
	def _splitchains(self, tags):
		'''
		split the tags and chains.

		returns: <tags>, <chians>
		'''
		t = ()
		c = ()
		ischain = self._ischain
		for tag in tags:
			if ischain(tag):
				c += (tag,)
			else:
				t += (tag,)
		return t, c
	##!!! need to rethink this...
	def _addchains(self, *chains):
		'''
		'''
		for c in chains:
			# check if chain exists...
			if c not in self:
				t = self.chain2tags(c)
				if self.__chain_tag__ != None:
					self._tag(c, *(t+(self.__tag_tag__, self.__chain_tag__)))
				else:
					self._tag(c, *(t+(self.__tag_tag__,)))
				# links all the tags in a chain...
				##!!! see if this is correct... (was .link(...))
				self._tag(c, *t)
##				##!!! revise...
##				self.link(c, *t)
	# tag-chain specific methods...
	@staticmethod
	def chain2tags(chain):
		'''
		return the tags in chain.
		'''
		# XXX check if cahin is a chain????
		return tuple(chain)
	@staticmethod
	def tags2chain(*tags):
		'''
		'''
		return tags
	def chains(self, *tags):
		'''
		return all the chains that contain tags.

		NOTE: if chains are given, then all the tags in them will be 
		      added to the search.
		'''
		tags, chains = self._splitchains(tags)
		tags = set(tags)
		for chain in chains:
			tags.update(self.chain2tags(chain))
		# collect all related chains...
		res = self.all(self.__chain_tag__, *tags).get(self.__chain_tag__, set())
		return res
	##!!!
	def chainrelated(self, *tags):
		'''
		return all the tags that are related via chains.
		'''
		chains = self.chains(*tags)
		res = set()
		for chain in chains:
			res.update(self.chain2tags(chain))
		return res.difference(tags)


#-------------------------------------------------StringTagChainMixin---
# XXX add consistency checking...
##!!! need to migrate this to the new interface !!!##
##class StringTagChainMixin(object):
class StringTagChainMixin(TagSetTagChainMixin):
	'''
	changes tagchain format to the folowing string syntax:

		<tag>:<tag>[:...]

	NOTE: this must be mixed with a valid tagset with chain support.
	'''
	def _ischain(self, tag):
		'''
		test if a tag is tagchain compatible.
		'''
		if type(tag) in (str, unicode) \
				and ':' in tag \
				and False not in [ len(t) > 0 for t in tag.split(':') ]:
			return True
		return False
	@staticmethod
	def chain2tags(chain):
		'''
		return the tags in chain.
		'''
		# XXX check if cahin is a chain????
		return tuple(chain.split(':'))
	@staticmethod
	def tags2chain(*tags):
		'''
		'''
		return ':'.join(tags)



#-----------------------------------------------------------------------
#--------------------------------------------------------------TagSet---
##class TagSet(TagSetInitMixin, TagSetMixin):
class TagSet(StringTagChainMixin, TagSetInitMixin, TagSetMixin):
	'''
	'''
	__stored_set_constructor__ = set


#----------------------------------------------------------DictTagSet---
##class DictTagSet(TagSetDictMixin, TagSetMixin, dict):
class DictTagSet(StringTagChainMixin, TagSetDictMixin, TagSetMixin, dict):
	'''
	'''
	__stored_set_constructor__ = set



#-----------------------------------------------------------------------
if __name__ == '__main__':

	from pli.testlog import logstr
	from pli.functional import curry

	txt = '''
	some text that will be tagged.

	the tagging will be like this:
	- each word is an object.
	- each word is tagged with the letters that it contains.

	just in case, a tag can also be an object and vice versa.
	'''

	
	logstr('''

	ts = DictTagSet()

	ts.tag('X', 'a', 'b', 'c')

	>>> ts

	ts = DictTagSet()

	! ts.tag('X', 'a')
	! ts.tag('X', 'b')
	! ts.tag('X', 'c')

	>>> ts

	! ts.tag('Y', 'c', 'd')

	# test of types that can be used as tags... (sanity check)
	! ts.tag('Z', 'string', u'unicode', True, False, 1, 1.1)
	! ts.tag('ZZ', ()) 
	### NOTE: tags MUST be hashable, so the following will fail.
	##! ts.tag('ZZ', [], {}) 

	>>> ts


	# unite:
	##!!! should yield a tagset only containing X
	ts.any('a', 'b')

	# _intersect:
	ts._all('a')

	# intersect:
	ts.all('a')

	# exclude:
	ts.none('a')


##	ts.untag('X', 'a')


	---

	>>> ts


	ts.istagsconsistent()
		-> True
	tuple(ts.itertaggaps())
		-> ()
	tuple(ts.iterorphans())
		-> ()

	words = DictTagSet() 
	! [ words.tag(w, *tuple(w)) for w in txt.split() ]

##	>>> words
##	words.__tagset__['t']

##	words.all('t', 'x')

	##!!! Q: sould the resultin tagset be tag complete?
	##!!!    ...i.e. .tags(obj) should return all the tags in any sub-tagset 
	##!!!    or only the relevant tags for that subset? (see next couple of lines)
	>>> words.any('a', 'x').tags('that')
	>>> words.tags('that')

	>>> words.any('a', 'x').tags('a')

	>>> words.tags('a')

##	>>> words.any('t', 'x').none('c')

	>>> words.objects()

	>>> words.any('a').objects()

	>>> words.tags()

	>>> words.tags('that')

	>>> words.tags('t')

	##!!! is this correct???
	>>> words.all()

	>>> words.relatedtags('a', 't')

	>>> words.relatedtags('a', 't', 'e')

	>>> words.relatedtags('a', 't', 'e', 'g')

	>>> words.relatedtags('a', 't', 'e', 'g', 'd')
	>>> words.all('a', 't', 'e', 'g', 'd').tags()
	>>> words.all('a', 't', 'e', 'g', 'd').objects()

	>>> words.all('a', 't', 'e', 'g', 'd').none('.').objects()
	>>> words.all('a', 't', 'e', 'g', 'd').none('.', 'a').objects()


	>>> words.all('t', 'e').tags()
	>>> words.all('t', 'e').any('l', 'j').objects()

	# errors -- tag conflicts...
	# XXX should these err or just return empty tagsets???
	>>> words.all('t', 'e').any('l').any('j').objects()
	>>> words.all('t', 'e').all('l').all('j').objects()
	>>> words.all('t', 'e').all('l').all('j').tags()
	>>> words.all('t', 'e').all('l')
	>>> words.all('t', 'e').all('l').any('j')
	>>> words.all('t', 'e').all('l').any('j').tags()
	>>> words.all('t', 'e').all('l').none('j').tags()
	>>> words.all('t', 'e').all('l').all('j')

	
	---

	# test tagchain functionality...
	
	words = DictTagSet() 

	words.tags2chain('a', 'b', 'c')
		-> 'a:b:c'
	words.chain2tags('a:b:c')
		-> ('a', 'b', 'c')

	! words.tag('that', 'T:H:A:T')
	! words.tag('this', 'T:H:I:S')
	! words.tag('that', 't', 'h', 'a', 't')
	! words.tag('that', 't', 'h', 'i', 's')

	words.tags('that')
	words.all('A').objects()

	words.chains()
	words.chains('A')
	words.chains('T:H')

	words.all('T:H:A:T').objects()
		-> set(['that'])

	>>> words.all('t', 'h', 'a').objects()

	words.all('T:H:I:S').objects()
		-> set(['this'])

	# NOTE: this will return a tagset and not a list of objects.
	>>> words.all('T:H:I:S', words.__object_tag__)

	''')



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
