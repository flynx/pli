#=======================================================================

__version__ = '''0.0.00'''
__sub_version__ = '''20030717142905'''


#-----------------------------------------------------------------------

import sys


#-----------------------------------------------------------------set---
# An evil equivalent for C expression: 'while x=f()'
#
# Usage:
# 	# sample
# 	A=range(10)
# 	while set(x=A.pop()):
# 		print x
#
# NOTE: this was originally posted by: Sebastien Keim at the ASPN Python CookBook
# 	    for the original post see:
# 		  <http://aspn.activestate.com/ASPN/Cookbook/Python/Recipe/202234>
# 	    the original function was modified by me (on: 20030619170645).
# NOTE: this will return the list of values (right sede of the =
#       operator)
#
def set(**kw):
	'''
	provides the abbility to do assignment in an expression

	the folowing C and Python expressions are equivelent:
		if (a=1, b=f())
			//....
	
		if set(a=1, b=f())[-1]:
			#....
	'''
	a = sys._getframe(1)
	a.f_locals.update(kw)
	return kw.values()



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
