#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20080307153553'''
__copyright__ = '''(c) Alex A. Naanou 2007'''


#-----------------------------------------------------------------------

import pli.pattern.proxy.utils as proxyutils
import pli.tags.generic as tags
import pli.pattern.mixin.mapping as mapping


#-----------------------------------------------------------------------
#
# add severela tag types:
# 	- Unique		: no other object is tagged with this.
# 	- One Of		: a set of tags is defined and the object is tagged
#				 	  with one and only one of the tags in set.
#
# TODO need more tag operations:
# 		unite(*tags)		- return objects that contain at least one
# 							  of the tags...
# TODO do an iterative select...
#
#------------------------------------------------------AbstractTagSet---
class AbstractTagSet(object):
	'''
	'''
	# tagset inteface...
	def addtags(self, *tags):
		'''
		'''
		raise NotImplementedError
	def tag(self, obj, *tags):
		'''
		'''
		raise NotImplementedError
	def _rawtag(self, obj, *tags):
		'''

		NOTE: this is not intended for direct use...
		'''
		raise NotImplementedError
	def untag(self, obj, *tags):
		'''
		'''
		raise NotImplementedError
	def relatedtags(self, *tags):
		'''
		'''
		raise NotImplementedError
	def select(self, *tags):
		'''
		'''
		raise NotImplementedError



#-----------------------------------------------------------------------
# the folowing functions use the tagset interface instead of directly
# accessing the _tag and _untag functions.
#-------------------------------------------------------------addtags---
def addtags(tagset, *tags):
	'''
	'''
	if not isinstance(tagset, AbstractTagSet):
		raise TypeError, 'the tagset must be a decendant of AbstractTagSet.'
	return tagset.addtags(obj, *tags)


#-----------------------------------------------------------------tag---
def tag(tagset, obj, *tags):
	'''
	'''
	if not isinstance(tagset, AbstractTagSet):
		raise TypeError, 'the tagset must be a decendant of AbstractTagSet.'
	return tagset.tag(obj, *tags)


#---------------------------------------------------------------untag---
def untag(tagset, obj, *tags):
	'''
	'''
	if not isinstance(tagset, AbstractTagSet):
		raise TypeError, 'the tagset must be a decendant of AbstractTagSet.'
	return tagset.untag(obj, *tags)



#-----------------------------------------------------------------------
class TagSetMixin(AbstractTagSet):
	'''
	this provides a direct and light inteface the the generic tag 
	engine (or a similar inteface).

	NOTE: this is a pure extension to the dict interface.
	NOTE: it is not very safe to use the dict interface for editing 
	      here directly.
	'''
	##!!! is this pretty?
	__tag_engine__ = tags

	# XXX do we need the __XXX__ customization methods here??

	# tagset inteface...
	proxyutils.proxymethods((
			'addtags',
			'tag',
			'untag',
			'tags',
			'relatedtags',
			'select',
		), '__tag_engine__',
		explicit_self=True)

	# NOTE: this is not intended for direct use...
	proxyutils.proxymethod('_rawtag', '__tag_engine__', '_tag',
			doc='NOTE: this was not intended for direct use!',
			explicit_self=True)
	
	# store management inteface...
	proxyutils.proxymethod('isconsistent', '__tag_engine__', 'istagsconsistent',
			doc='check for tag consistency',
			explicit_self=True)
	proxyutils.proxymethod('fix', '__tag_engine__', 'filltaggaps',
			doc='check for tag consistency',
			explicit_self=True)
	


#--------------------------------------------TagSetWithTagChainsMixin---
# XXX do we need chain-specific select???
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
	def _rawtag(self, obj, *tags):
		'''
		'''
		tags, chains = self._splitchains(tags)
		self._addchains(*chains)
		return super(TagSetTagChainMixin, self)._rawtag(obj, *(tags+chains))
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
	def _addchains(self, *chains):
		'''
		'''
		for c in chains:
			# check if chain exists...
			if c not in self:
				t = self.chain2tags(c)
				if self.__chain_tag__ != None:
					self._rawtag(c, *(t+(tags.TAG_TAG, self.__chain_tag__)))
				else:
					self._rawtag(c, *(t+(tags.TAG_TAG,)))
				# links all the tags in a chain...
				self.__tag_engine__.link(self, c, *t)
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

		NOTE: of chains are given, then all the tags in them will be 
		      added to the search.
		'''
		tags, chains = self._splitchains(tags)
		tags = set(tags)
		for chain in chains:
			tags.update(self.chain2tags(chain))
		# collect all related chains...
		res = self.select(self.__chain_tag__, *tags)
		return res
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
class StringTagChainMixin(object):
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


#--------------------------------------------------------------TagSet---
class TagSet(StringTagChainMixin, TagSetTagChainMixin, TagSetMixin, dict):
	'''
	'''
	pass


#------------------------------------------------TagSetWithSplitStore---
##!!! bring this up to date to support tag chains...
# in geniral this should generate a unique string id for each stored
# object and use that id in the tag store while storing the objects by
# id in a seporate dict...
# XXX might be good to make this a mapping (OID is key and object is
#     also unique)...
# XXX might be a good idea to split this into several specific
#     intefaces.... (split out the oid stuff...)
# XXX make this a mapping... (???)
# XXX make split stores by taging a generic feature...
##class TagSetWithSplitStore(AbstractTagSet, mapping.Mapping):
class TagSetWithSplitStore(AbstractTagSet):
	'''
	this will manage two stores for objects and tags.
	'''
	# XXX is this pretty?
	__tag_engine__ = tags

	__tag_store__ = None
	__object_store__ = None
	
	# index the store-defining tags. if an object has one of these tags
	# it will be sotred in the coresponding store and not in the index.
	# format: {<tag>: <store>, ...}
	# XXX what to do if an object has more than one of those?
	# XXX we will need some generic OID system to use here...
	# XXX after this is implemented, kill the __object_store__!
##	__object_store_index__ = None

	# specific inteface...
	##!!! this is the function of the object store, move there...
	def _getoid(self, obj):
		'''
		get a unique ID for an object (OID).

		NOTE: preferably this should return a stable and interpreter 
		      instance independent string, uniquely identifying a 
			  particular object.
		NOTE: this will not work for persistent stores.
		'''
		##!!! this is by far not the best way to go!!
		return str(hash(obj))
	def _getbyoid(self, oid):
		'''
		'''
		return self.__object_store__[oid]
	
	# specific public inteface...
	##!!!
	def remove(self, obj):
		'''
		remove the object form the store.
		'''
		raise NotImplementedError
	
	# tagset inteface...
	##!!! revise... (should this always add to the index?)
	def addtags(self, *tags):
		'''
		'''
		return self.__tag_engine__.addtags(self.__tag_store__, *tags)
	def tag(self, obj, *tags):
		'''
		'''
		oid = self._getoid(obj)
		if oid not in self.__object_store__:
			# add the object to the store...
			self.__object_store__[oid] = obj
		# XXX make this a super call...
		return self.__tag_engine__.tag(self.__tag_store__, oid, *tags)
	def untag(self, obj, *tags):
		'''
		'''
		oid = self._getoid(obj)
		if oid not in self.__object_store__:
			raise TypeError, 'object is not in this tagset.'
		# XXX make this a super call...
		return self.__tag_engine__.untag(self.__tag_store__, oid, *tags)
	# XXX how will this work for cases when an object acts as a tag?
	# XXX can we make an iterator out of this? (an iterative algorithm?)
	def select(self, *tags):
		'''
		'''
		# get the clean objects...
		oids = self.__tag_engine__.select(self.__tag_store__, self.__tag_engine__.OBJECT_TAG, *tags)
		# get all the non-objects...
		res = self.__tag_engine__.select(self.__tag_store__, *tags).difference(oids)

		# replace all oids in res with objets form the object store...
		for oid in oids:
			o = self._getbyoid(oid)
			res.update((o,))
		return res
	def relatedtags(self, *tags):
		'''
		'''
		return self.__tag_engine__.relatedtags(self, *tags)



#-----------------------------------------------------------------------
##!!! should we create tag-specific interfaces??
#-------------------------------------------------------TaggableMixin---
class TaggableMixin(object):
	'''
	provides an object-specific interface to the tagset...
	'''
	# this is the only pice of data needed here, thus this mixin is
	# store specific...
	# defines the tagset to use...
	__tagset__ = None

	@property
	def tags(self):
		'''
		'''
		# select all the tags that tag self...
		return self.__tagset__.select(self, self.__tag_engine__.TAG_TAG)
	
	# NOTE: the foloeing are not a direct transfer, thus can't use the
	#       proxy utils...
	def tag(self, *tags):
		'''
		'''
		return self.__tagset__.tag(self, *tags)
	def untag(self, *tags):
		'''
		'''
		return self.__tagset__.untag(self, *tags)




#-----------------------------------------------------------------------
if __name__ == '__main__':

	ts = TagSet()

	class Obj(object): pass

	TAG = tags.TAG_TAG
	OBJECT = tags.OBJECT_TAG

	o0 = Obj()
	o1 = Obj()
	o2 = Obj()
	o3 = Obj()

	ts.tag(o0, '0', 'a', 'data')
	ts.tag(o1, '1', 'b', 'data')
	ts.tag(o2, '2', 'a', 'data')
	ts.tag(o3, '3', 'data')

	print ts.select(TAG)
	print ts.select(TAG, 'a')
	print ts.select(TAG, 'a', '0')
	print
	print ts.select(OBJECT)
	print
	print ts[TAG]
	print ts[OBJECT]
	print
	print
	print ts.addtags('x', 'y', 'z')


	class TSWSS(TagSetWithSplitStore):
		__tag_store__ = {}
		__object_store__ = {}

	tss = TSWSS()

	tss.tag(o0, '0', 'a', 'data')
	tss.tag(o1, '1', 'b', 'data')
	tss.tag(o2, '2', 'a', 'data')
	tss.tag(o3, '3', 'data')

	print tss.select(TAG)
	print tss.select(TAG, 'a')
	print tss.select(TAG, 'a', '0')
	print
	print tss.select(OBJECT)
	print
	print tss.__tag_store__.keys()
	print tss.__object_store__.keys()
	print
	print
	print tss.addtags('x', 'y', 'z')

	# chains...
	ts.tag(o0, 'aaa:bbb')
	ts.tag(o1, 'aaa:ccc')

	print ts.select('aaa', 'TAGCHAIN')
	print ts.relatedtags('aaa')
	print ts.chains('aaa')
	print ts.chainrelated('aaa')
##	print ts.relatedtags('aaa:bbb')
	



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
