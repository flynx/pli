#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20060125163136'''
__copyright__ = '''(c) Timothy N. Tsvetkov'''


#-----------------------------------------------------------------------

def bsort(l, cmp=None):
	if cmp != None:
		for i in range(0, len(l)):
			for j in range(i, len(l)):
				if cmp(l[i], l[j]) > 0:
					l[i], l[j] = l[j], l[i]
	else:
		for i in range(0, len(l)):
			for j in range(i, len(l)):
				if l[i] > l[j]:
					l[i], l[j] = l[j], l[i]
	return l



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
