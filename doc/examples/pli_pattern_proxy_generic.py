#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20060621183212'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.pattern.proxy.generic as proxy


#-----------------------------------------------------------------------
#---------------------------------------------------MonitorCangeProxy---
class MonitorCangeProxy(proxy.InheritAndOverrideProxy):
	'''
	this class will monitor the changes made to the target object.
	'''
	def __setattr__(self, name, value):
		print 'changing value of attr %s of object %s from %s to %s.' \
				% (name, proxy.getproxytarget(self), getattr(self, name), value)
		super(MonitorCangeProxy, self).__setattr__(name, value)
	def __delattr__(self, name):
		print 'deleting attr %s from object %s' % (name, proxy.getproxytarget(self))
		super(MonitorCangeProxy, self).__delattr__(name)


if __name__ == '__main__':

	class O(object):
		'''
		'''
		a = 0
		def __init__(self):
			'''
			'''
			self.b = 1
		def meth(self, x=1):
			'''
			'''
			self.b += x
			print self.a, self.b, x

	o = O()

	p = MonitorCangeProxy(o)

	print p.a
	print p.b
	
	p.meth()
	p.meth()
	p.meth()

	print p.a
	print p.b
	print o.a
	print o.b
	
	

#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
