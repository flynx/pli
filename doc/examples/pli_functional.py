#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20040825201035'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

'''
this example illustrates a functional loop to call each member of a list.
'''

#-----------------------------------------------------------------------

from pli.functional import curry, rcurry, apply


#-----------------------------------------------------------------------
# this example demonstrates the use of curry, rcurry and apply, as well
# as pythons own map functions...
# NOTE: this might be a bit difficult to grasp at first...
# NOTE: considering that pythons' apply function is depricated here we
#       use the one defined in pli.functional...
#
# here we will basicly create a list of callables and call each element
# in a function one-liner :)
#
#----------------------------------------------------------------func---
# the function we are going to call...
def func(*arg):
	print ' '.join(arg)


#-----------------------------------------------------------------------
# generate the list of functions...
number_of_funcs = 6
# this can be done quite a bit simpler in pythonic syntax.... (but...
# I could not help myself :)))) )
list_of_funcs = map(
					curry(rcurry, func), 
					map(
						lambda i: '#' + str(i), 
						range(number_of_funcs)
				))

# if you had not yet guessed what the above "line" does here is the
# pythonic version:
##list_of_funcs = [ rcurry(func, '#' + str(i)) for i in range(number_of_funcs) ]
# and this will add the word pythonic to the beginning of the line :)
##list_of_funcs = [ curry(rcurry(func, '#' + str(i)), 'pythonic:') for i in range(number_of_funcs) ]
# though I must admit that this does not look much simpler...


#-----------------------------------------------------------------------
# The Loop:
map(rcurry(apply, 'this is', 'the call', 'of', 'element') ,list_of_funcs)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
