#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20060204024020'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pli.pattern.mixin.mapping as mapping


#-----------------------------------------------------------SQLShelve---
##!!!
# XXX should this be live???
class SQLShelve(mapping.Mapping):
	'''
	'''
	# TODO make this create a new dict for the id if one is not
	#      present.... (might be a good idea to use some other id
	#      method...)
	#      one alternative id method is to create a root dict that will
	#      contain names of all the dicts used and their coresponding
	#      id's...
	def __init__(self, interface, name):
		'''
		'''
		self._interface = interface
		self._name = name
		# if such a name does not exist...
		try:
			self._data = interface.get(name)
		except KeyError:
			d = self._data = {}
			interface.write(name, d)
		##!!! sanity check: if the name refereneces a non-dict or non-dict-like...
		##!!!
	def __getitem__(self, name):
		'''
		'''
		if name in self._data:
			return self._interface.get(self._data[name])
		raise KeyError, name
	##!!! make this safe...
	def __setitem__(self, name, value):
		'''
		'''
		interface =  self._interface
		data = self._data
		try:
			# insert the object...
			oid = interface.write(value)
			# update the keys dict...
			data[name] = oid
			interface.write(data)
		except:
##			##!!! rollback...
##			interface.__sql_reader__.sql.connection.rollback()
			raise 'oops!'
		# commit...
		# XXX make this prittier!
		interface.__sql_reader__.sql.connection.commit()
	##!!! REWRITE: might be a tad cleaner...
	def __delitem__(self, name):
		'''
		'''
##		return self._interface.delete(self._data.pop(name))
		interface =  self._interface
		data = self._data
		try:
			data.pop(name)
			interface.write(data)
		except:
##			##!!! rollback...
##			interface.__sql_reader__.sql.connection.rollback()
			raise 'oops!'
		# commit...
		# XXX make this prittier!
		interface.__sql_reader__.sql.connection.commit()
	def __iter__(self):
		'''
		'''
		for name in self._data.keys():
			yield name



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
