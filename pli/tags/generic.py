#=======================================================================

__version__ = '''0.3.07'''
__sub_version__ = '''20080307125708'''
__copyright__ = '''(c) Alex A. Naanou 2007'''


#-----------------------------------------------------------------------



#-----------------------------------------------------------------------
#
# XXX will need to make this adaptable to OOBTree (string keys)...
#     ...most likely will concern adding an overlay over the store.
# XXX try to make this linear.... (currently it appears to eat time at
#     non-linear, possibly quadratic rates with the increase of data-sets)
#     ...mostly, this concerns the tagging; selecting appears to be
#     less affected...
#
#     does not appear to be the algorithm (considering how stupid it is)...
#     the bottleneck appears to be the Python set (and possibly the
#     memory manager)...
# XXX this is essentially a relation management... thus, it might be
#     good to seporate the "relation" and "tagging" specifics into two
#     modules...
#
#
#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
#
# TODO add an iterative select that goes good on memeory (different
#      algorithm)...
# TODO generic methods to check for tags, or if a tag exists... etc.
# TODO make the TAG_TAG and OBJECT_TAG tags optional and/or 
#      confugurable...
#      the problem here is the lack of ability to control these tags;
#      in cases it might be usefull to be able to add a third system
#      tag or remove one...
#      ....this may be done as a seporate layer
#
# TODO add more basic tag operations:
# 		intersect		- select(...) 			done.
# 		unite			- ???
# 		exclude			- 						done but not here.
# 		pattern			- search (difflib?)
#
#
#
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
	Each value stores the tags/objects related to it's key.

	When the object is tagged, the whole chain (including the object)
	is treated as a set of related tags. The tag is recorded as a key
	and the rest are recorded in a set as a value to that key. This is
	done for each tag in the given set.

Results:
	+ trivial and fast search.
	+ trivial, though not the fastest addition, and essentially no
	  need for balancing (unless the store is tampered with manually).
	- redundant linkage within the tag store.


NOTE: there is no distinction between tagged abjects and tags other
      than the two special tags "tag" and "object". They are both
      treated the same and stored in one structure.

Structure:
	{ <tag>: set([<tag>, ...]), ...}



Notes
-----

It is expected that the number of tags will grow far slower than the 
number of objects (after stabilizing the objects in a live system
will exhibit linear growth, while tags will almost plateau at some point).

In this approach, the number of objects will be extremely large.

The two sub-groups (tags and objects) have slight differences. Tags
tend to be highly interlinked while objects rarely exhibit linkage
with each other.

Most searches will be tag oriented, possibly with a final filtration
by tag or object.



'''

#-----------------------------------------------------------------------

##!!! find a better way to deal with this!
TAG_TAG = 'TAG'
OBJECT_TAG = 'OBJECT'



#-----------------------------------------------------------------------
# helpers...
#--------------------------------------------------------------getset---
def getset(tagdb):
	'''
	get the set constructor form the tagdb.

	the tagdb can control which constructor is used to create internal 
	sets via the "__stored_set_constructor__" attribute.

	default constructor is set.
	'''
	return getattr(tagdb, '__stored_set_constructor__', set)



#-----------------------------------------------------------------------
# store-level functions...
#----------------------------------------------------istagsconsistent---
# a store is consistent if:
# - all tags in relations are present in store keys.
# - if no orphan tags are allowed (???) each tag in keys MUST also be
#   present in relations (related to).
# - if all relations are symetrical.
def istagsconsistent(tagdb):
	'''
	'''
	for i in itertaggaps(tagdb):
		# if we get in here, it means that we have a problem...
		return False
	return True


#---------------------------------------------------------itertaggaps---
# XXX should this ignore orphaned tags???
def itertaggaps(tagdb):
	'''
	find store inconsistencies and return the conflicting keys and relations.

	this can not detect the folowing:
		- missing orphaned keys (no data).
		- interlinking between missing keys (no data).
		- inconsistencies in relations (no way to destinguish this from
		  good data).
	'''
	keys = set(tagdb.keys())
	for tag, rel in tagdb.items():
		# XXX ignore orphans... (to check for them use strict equality)
		# check for gaps (missing tagdb keys)...
		if not keys.issuperset(rel):
			yield tag, rel.difference(keys)
		# check for missing symetric relations...
		##!!! can this be faster? ...is there a better algorithm?
		for r in rel:
##			if tag not in tagdb[r]:
			if r not in tagdb or tag not in tagdb[r]:
				##!!! this may return duplicate with the above data...
				yield tag, set([r])


#---------------------------------------------------------filltaggaps---
# XXX should these two be split??
# XXX might be good make this an interactive generator so as to have
#     more control over what is fixed and how...
# XXX should this restore the tag to self??
# XXX might be good to make this explicitly depend on itertaggaps
#    (through arguments)...
def filltaggaps(tagdb):
	'''
	fix inconsistencies using the data returned by itertaggaps.

	NOTE: this will restore the data that can be detected and restored 
	      only (no domain semantic checks are made at this level).
	NOTE: this is maximalistic. will fill the holes rather than cut off 
	      the excess.
	'''
	# NOTE: this is split in two so as to not iterate and modify the
	#       store at the same time...
	tdb_diff = {}
	tdbset = getset(tagdb)
	# build the diff correcting the errors...
	for key, dif in itertaggaps(tagdb):
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



#-----------------------------------------------------------------------
# low-level "naive" functions...
#----------------------------------------------------------------link---
# XXX shows signs of exponential time increase on very large sets of
#     data... need to revise.
# XXX this may go bad with a very large number of args...
def link(tagdb, obj, *objs):
	'''
	link the given objects.
	'''
	tt = [obj] + list(objs)
	tdbset = getset(tagdb)

	for t in set(tt):
		# remove one occurrence of self...
		tt_c = tt[:]
		tt_c.remove(t)

		if t in tagdb:
			tagdb[t].update(tt_c)
		else:
			tagdb[t] = tdbset(tt_c)
	return tagdb


#--------------------------------------------------------------unlink---
##!!! test !!!##
# XXX should this remove orphaned tags???
def unlink(tagdb, obj, *objs):
	'''
	remove the links between objects.

	NOTE: if an element is present more than once then remove the self link too.
	'''
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
	return tagdb


#---------------------------------------------------------------links---
def links(tagdb, obj):
	'''
	return all the links to the object.

	NOTE: this is the same as tagdb[obj].
	'''
##	# sanity check...
##	if obj not in tagdb:
##		raise KeyError, 'object %s not in tagdb (%s).' % (obj, tagdb)
	return tagdb[obj]



#-----------------------------------------------------------------------
# user interface functions...
#-------------------------------------------------------------addtags---
# XXX should this tag the tag with TAG_TAG???
def addtags(tagdb, *tags):
	'''
	add empty tags to tag store.
	'''
	tdbset = getset(tagdb)
	for tag in tags:
		if tag not in tagdb:
			tagdb[tag] = tdbset()


#----------------------------------------------------------------_tag---
# XXX should this be an iterator?
def _tag(tagdb, obj, *tags):
	'''
	raw version of the tag(...). this does not enforce the use of system tags.

	WARNING: not recommended for direct use.
	'''
	# the tag tag...
	for t in tags:
		# XXX revise: there should be a better and faster way to do this...
		# link the object and tag...
		link(tagdb, obj, t)
	return tagdb


#-----------------------------------------------------------------tag---
# XXX this has two effects that might be wrong:
# 		1) an object is tagged by itself (the problem is link())
# 		2) all tags (relations) are symetrical... (might need to have
# 		   exceptions like OBJECT_TAG and TAG_TAG) 
# XXX need a way to control the addition of TAG_TAG and OBJECT_TAG...
#     ...might be good to add a LL layer...
# XXX make error handling related to use of TAG_TAG and OBJECT_TAG
#     optional...
# XXX use the _tag function... (???)
# NOTE: adds TAG_TAG and OBJECT_TAG...
def tag(tagdb, obj, *tags):
	'''
	tag an object...

	this maintains two special tags:
		tag		: tags all the tags.
		object	: tags all the objects.

	NOTE: the tags "objects" and "tag" are meant for searches.
	NOTE: neither the "object" nor the "tag" tags are user modifiable. 
	'''
	# do special tags...
	# can't manually use the tag and object tags...
	if TAG_TAG in tags or OBJECT_TAG in tags or obj in (TAG_TAG, OBJECT_TAG):
		raise TypeError, 'can\'t use either "object" or "tag" tags manually.'
	# the tag tag...
	for t in tags:
		if TAG_TAG not in tagdb.get(t, ()):
			link(tagdb, t, TAG_TAG)
##		# XXX revise: there should be a better and faster way to do this...
##		# link the object and tag...
##		link(tagdb, obj, t)
	# XXX two loops is not good... may be a good idea to make _tag an
	#     iterator/generator....
	_tag(tagdb, obj, *tags)
	# the object tag...
	if OBJECT_TAG not in tagdb.get(obj, ()):
		link(tagdb, obj, OBJECT_TAG)
		if TAG_TAG not in tagdb.get(OBJECT_TAG, ()):
			link(tagdb, TAG_TAG, TAG_TAG)
			# XXX the probem here is that OBJECT_TAG is a tag but the
			#     TAG_TAG is not an object... the current store does not
			#     support assymetric linking.
##			link(tagdb, OBJECT_TAG, TAG_TAG)
	return tagdb


#---------------------------------------------------------------untag---
##!!! test: appears to be broken !!!##
##!!! what should we do here with the special tags here???
# NOTE: uses TAG_TAG and OBJECT_TAG... (mostly error handling)
def untag(tagdb, obj, *tags):
	'''
	remove the tag relation.
	'''
	# do special tags...
	# can't manually use the tag and object tags...
	if TAG_TAG in tags or OBJECT_TAG in tags or obj in (TAG_TAG, OBJECT_TAG):
		raise TypeError, 'can\'t use either "object" or "tag" tags manually.'
	# now remove the links...
	for tag in tags:
		unlink(tagdb, obj, tag)
	return tagdb


#----------------------------------------------------------------tags---
# NOTE: uses both TAG_TAG and OBJECT_TAG...
def tags(tagdb, obj):
	'''
	return the tags tagging the object.

	NOTE: this removes all the relations that are not tags.
	'''
	return links(tagdb, obj).intersection(tagdb[TAG_TAG].union([OBJECT_TAG]))


#---------------------------------------------------------relatedtags---
# XXX seam relatively straightforward.... revise for efficiency...
# NOTE: uses OBJECT_TAG...
def relatedtags(tagdb, *tags):
	'''
	return the related tags to the given.

	two tags are related if they both tag the same object. thus this will 
	return the tags sutable for further specialization.

	NOTE: to get all the objects use "select(tagdb, tag, tags, OBJECT_TAG)"
	      with the same tags...
	'''
	# get all the valid data...
	objs = select(tagdb, OBJECT_TAG, *tags)
	res = set()
	# gather all the related tags...
	for o in objs:
		res.update(tagdb[o])
	# remove the objects and input tags...
	res.difference_update((OBJECT_TAG,) + tags + tuple(objs))
	return res


#--------------------------------------------------------------select---
# XXX make these return a sub-tagset to be able to efficiently chain
#     operations...
# XXX is this a good name at this? (should be something like "intersect"?)
# NOTE: does not use either TAG_TAG or OBJECT_TAG directly...
def select(tagdb, *tags):
	'''
	select a set of data using tags.

	NOTE: this will return both tags and tagged objects. to control this
	      use the "tag" and "object" tags...
	NOTE: the TAG_TAG and OBJECT_TAG tags are related thus TAG_TAG is also an 
	      object. (this can be resolved, but the solution will introduce 
		  an inconsistency).
	'''
	# if no tags are given return evrything we've got! :)
	if len(tags) == 0:
		return tagdb.keys()
	# a small optimisation: order the tags to intersect out as mach as
	# possible as early as possible... (XXX check for better strategies)
	l = list(tags)
	l.sort(lambda a, b: cmp(len(tagdb[a]), len(tagdb[b])))
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
##		visited.update(t)
		res.intersection_update(tagdb[t])
	return res.difference(visited)


#-------------------------------------------------------------iselect---
def iselect(tagdb, *tags):
	'''
	an iterative version of select.

	NOTE: this is slower per-item than select(), thus if the whole set 
	      is needed use the non itarative version.
	'''
	raise NotImplementedError


#---------------------------------------------------------excludeiter---
def excludeiter(tagdb, objs, *tags):
	'''
	yield only objects that are not tagged with tags.
	'''
	for o in objs:
		t = tagdb.get(o, None)
		if t == None:
			raise TypeError, 'object %s is not in the given tagdb.' %s (o,)
		if len(t.intersection(tags)) != 0:
			continue
		yield o


#-------------------------------------------------------------exclude---
def exclude(tagdb, objs, *tags):
	'''
	exclude the objects tagged with tags from the object list.
	'''
	return set(excludeiter(tagdb, objs, *tags))



#-----------------------------------------------------------------------
if __name__ == '__main__':

	from pprint import pprint
	
	ts1 = {}

	# this will make object-tag relations only..
	tag(ts1, 'X', 'a')
	tag(ts1, 'X', 'b')
	tag(ts1, 'X', 'c')

	print ts1

	# this will creat relations between ALL the elements (including
	# inter-tag relations)...
	tag(ts1, 'Y', 'a', 'b', 'c')

	print istagsconsistent(ts1)

	# XXX the two results should be the same...
	print select(ts1, 'a', 'b')

	print 
	# show all the tags except for TAG_TAG as it particepates in the
	# request...
	print select(ts1, TAG_TAG)
	print 
	print relatedtags(ts1, OBJECT_TAG)
	print relatedtags(ts1, 'a')
	print relatedtags(ts1, 'a', 'c')
	print select(ts1, 'a', 'c', OBJECT_TAG)

	print

	print tags(ts1, 'X')
	print links(ts1, 'X')

	print

	print istagsconsistent(ts1)
	print ts1['a']
	print ts1[TAG_TAG]
	print 'removing tags...'
	ts1['a'].remove(TAG_TAG)
	print ts1['a']
	print ts1[TAG_TAG]
	print istagsconsistent(ts1)
	print list(itertaggaps(ts1))
	print filltaggaps(ts1)
	print ts1['a']
	print ts1[TAG_TAG]
	print istagsconsistent(ts1)

	pprint(ts1)
	untag(ts1, 'X', 'a')
	pprint(ts1)
	untag(ts1, 'a', 'a')
	pprint(ts1)
	print istagsconsistent(ts1)

	addtags(ts1, 'aaa', 'bbb')
	print ts1['aaa']

	print exclude(ts1, select(ts1, 'Y'), 'Y')
	print exclude(ts1, select(ts1, 'Y'), 'X')
	



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
