#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20070716030839'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.tags.tag as tag


#-----------------------------------------------------------------------

letters = 'abcdefghijklmnopqrstuvwxyz'

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

#-----------------------------------------------------------------------

tdb = tag.TagTreeWithAttrNodes(None, *letters)
##tdb = tag.TagTreeWithAttrNodes()


#----------------------------------------------------------------Word---
class Word(tag.TaggableWithDFLTags):
	'''
	'''
	__tagdb__ = tdb
	__dfl_tags__ = (
			'word',
			)

	def __init__(self, txt):
		'''
		'''
		super(Word, self).__init__()
		self.text = txt

		self.tag(*txt.lower())


#-----------------------------------------------------------------------
if __name__ == '__main__':
	import time

	t = time.time()

	words = []
	n = 10
	for word in (text*n).split():
		if word.isalpha():
			words += [Word(word)]

	tt = time.time()
	print 'valid word count:', len(words)

	print 'words containing "t" and "h":', len(tdb.h.t.tagged)
	print 'words containing "t", "e" and "h":', len(tdb.h.t.e.tagged)

	ttt = time.time()

	print tt-t, ttt-tt




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
