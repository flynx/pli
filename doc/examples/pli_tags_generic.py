#=======================================================================

__version__ = '''0.3.03'''
__sub_version__ = '''20071016025908'''
__copyright__ = '''(c) Alex A. Naanou 2007'''


#-----------------------------------------------------------------------

import pli.tags.generic as tags


#-----------------------------------------------------------------------
if __name__ == '__main__':

	tagdb = {}

	text = '''\
	Cecil, you're my final hope
	Of finding out the true Straight Dope
	For I have been reading of Schrodinger's cat
	But none of my cats are at all like that.
	This unusual animal (so it is said)
	Is simultaneously alive and dead!
	What I don't understand is just why he
	Can't be one or the other, unquestionably.
	My future now hangs in between eigenstates.
	In one I'm enlightened, in the other I ain't.
	If *you* understand, Cecil, then show me the way
	And rescue my psyche from quantum decay.
	But if this queer thing has perplexed even you,
	Then I will *and* I won't see you in Schrodinger's zoo.
					-- Randy F., Chicago, "The Straight Dope, a compendium
					   of human knowledge" by Cecil Adams


	'''

	from pli.functional import curry

	# setup for convenient testing :)
	tag = curry(tags.tag, tagdb)
	untag = curry(tags.untag, tagdb)
	select = curry(tags.select, tagdb)
	istagsconsistent = curry(tags.istagsconsistent, tagdb)
	filltaggaps = curry(tags.filltaggaps, tagdb)


	class Word(object):
		def __init__(self, word):
			self.text = word
			tag(self, *word)


	import time

	t = time.time()
	
	# test run setup...
	profile = False

	if profile:
		n = 10
	else:
		n = 1000

	def setup_words(text, n=1):
		'''
		'''
		words = []
		for word in (text*n).split():
			if word.isalpha():
				words += [Word(word)]
		return words

	if profile:
		import profile
		profile.run("words = setup_words(text, n)")
	else:
		words = setup_words(text, n)

	tt = time.time()

	print 'valid word count:', len(words)

	print 'words containing "t" and "h":', len(select('h', 't', 'object'))
	print 'words containing "t", "e" and "h":', len(select('h', 't', 'e', 'object'))

	ttt = time.time()

	print 'constructed in:', tt-t, '-', 'rough select time:', (ttt-tt)/2

	print 

	print 'store is consistent:', istagsconsistent()
	print 'gaps filled:', len(filltaggaps())


	# test filltaggaps...
	print 'removing key "a" and all direct relations... (rels: %s)' % len(tagdb['a'])
	orig_a = tagdb['a']
	del tagdb['a']
	print 'removing key "e" and all direct relations... (rels: %s)' % len(tagdb['e'])
	orig_e = tagdb['e']
	del tagdb['e']
	print 'store is consistent:', istagsconsistent()
	print 'keys added:', len(filltaggaps())
	print 'store is consistent:', istagsconsistent()
	# NOTE: losing the inter-relations between the removed nodes is
	#       unavoidable...
	#       for example, if 'a' was tagged with 'e' then this relation
	#       would be lost due to the removal of both 'a' and 'e'
	print 'restored %s relations for "a" (lost relations to: %s).' \
			% (len(tagdb['a']), tuple(orig_a.difference(tagdb['a'])))
	print 'restored %s relations for "e" (lost relations to: %s).' \
			% (len(tagdb['e']), tuple(orig_e.difference(tagdb['e'])))




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
