#=======================================================================

__version__ = '''0.3.07'''
__sub_version__ = '''20070804203341'''
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
# TODO add an iterative select...
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
# store-level functions...
#----------------------------------------------------istagsconsistent---
# a store is consistent if:
# - all tags in relations are present in store keys.
# - if no orphan tags are allowed (???) each tag in keys MUST also be
#   present in relations (related to).
#
# algorithm:
#	union of all relations must be a subset of the union of all keys.
#
# NOTE: use strict equality to check for orphans...
#
# XXX should this ignore orphaned tags???
def istagsconsistent(tagdb):
	'''
	'''
	rel = set()
	for r in tagdb.values():
		rel.update(r)
	# XXX ignore orphans... (to check for them use strict equality)
	if rel.issubset(set(tagdb.keys())):
		return True
	return False


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
		if not keys.issuperset(rel):
			yield tag, rel.difference(keys)


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
	# bild the diff correcting the errors...
	for key, dif in itertaggaps(tagdb):
		for k in dif:
			if k in tdb_diff:
				tdb_diff[k].update((key,))
			else:
				tdb_diff[k] = set((key,))
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
# XXX what should this return??
# XXX shows signs of exponential time increase on very large sets of
#     data... need to revise.
def link(tagdb, obj, *tags):
	'''
	add the tags to store.
	'''
	tt = set((obj,) + tags)

	for t in tt:
		if t in tagdb:
			tagdb[t].update(tt)
		else:
			tagdb[t] = tt.copy()


#--------------------------------------------------------------unlink---
##!!! test !!!##
# XXX what should this return??
# XXX should this remove orphaned tags???
def unlink(tagdb, obj, *tags):
	'''
	remove tags from store.
	'''
	tt = set((obj,) + tags)

	for t in tt:
		if t not in tagdb:
			# ignore invalid tags... (XXX should we complain here?)
			continue
		# remove the reqired tags...
		tagdb[t].difference_update(tt)
		# remove tag if it has no relations... (XXX)
		if len(tagdb[t]) == 0:
			del tagdb[t]



#-----------------------------------------------------------------------
# user interface functions...
#-----------------------------------------------------------------tag---
# XXX what should this return??
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
	if 'tag' in tags or 'object' in tags or obj in ('tag', 'object'):
		raise TypeError, 'can\'t use either "object" or "tag" tags manually.'
	# the tag tag...
	for t in tags:
		if 'tag' not in tagdb.get(t, ()):
			link(tagdb, t, 'tag')
		# XXX revise: there should be a better and faster way to do this...
		# link the object and tag...
		link(tagdb, obj, t)
	# the object tag...
	if 'object' not in tagdb.get(obj, ()):
		link(tagdb, obj, 'object')
		if 'tag' not in tagdb.get('object', ()):
			link(tagdb, 'tag', 'tag')
			# XXX the probem here is that 'object' is a tag but the
			#     'tag' is not an object... the current store does not
			#     support assymetric linking.
##			link(tagdb, 'object', 'tag')

##	# no do the work that the user actually requested... 
##	# XXX revise! (see above..)
##	link(tagdb, obj, *tags)


#---------------------------------------------------------------untag---
# XXX what should this return??
##!!! test !!!##
##!!! what should we do here with the special tags here???
def untag(tagdb, obj, *tags):
	'''
	remove the tag relation.
	'''
	# do special tags...
	# can't manually use the tag and object tags...
	if 'tag' in tags or 'object' in tags or obj in ('tag', 'object'):
		raise TypeError, 'can\'t use either "object" or "tag" tags manually.'
	##!!!
	# now remove the chain...
	unlink(tagdb, obj, *tags)


#---------------------------------------------------------relatedtags---
# XXX seam relatively straightforward.... revise for efficiency...
def relatedtags(tagdb, tag, *tags):
	'''
	return the related tags to the given.

	two tags are related if they both tag the same object. thus this will 
	return the tags sutable for further specialization.

	NOTE: to get all the objects use "select(tagdb, tag, tags, 'object')"
	      with the same tags...
	'''
	# get all the valid data...
	objs = select(tagdb, tag, 'object', *tags)
	res = set()
	# gather all the related tags...
	for o in objs:
		res.update(tagdb[o])
	# remove the objects and input tags...
	res.difference_update((tag, 'object') + tags + tuple(objs))
	return res


#--------------------------------------------------------------select---
def select(tagdb, tag, *tags):
	'''
	select a set of data using tags.

	NOTE: this will return both tags and tagged objects. to control this
	      use the "tag" and "object" tags...
	NOTE: the 'tag' and 'object' tags are related thus 'tag' is also an 
	      object. (this can be resolved, but the solution will introduce 
		  an inconsistency).
	'''
	# a small optimisation: order the tags to cut out as mach as
	# possible as early as possible... (XXX check for better strategies)
	l = [tag] + list(tags)
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
def iselect(tagdb, tag, **tags):
	'''
	an iterative version of select.

	NOTE: this is slower per-item than select(), thus if the whole set 
	      is needed use the non itarative version.
	'''
	raise NotImplementedError



#-----------------------------------------------------------------------
if __name__ == '__main__':
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
	print select(ts1, 'tag')
	print 
	print relatedtags(ts1, 'object')
	print relatedtags(ts1, 'a')
	print relatedtags(ts1, 'a', 'c')
	print select(ts1, 'a', 'c', 'object')




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
