#=======================================================================

__version__ = '''0.0.05'''
__sub_version__ = '''20070108034905'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import pickle
import sys
import types



#-----------------------------------------------------------------------
#-------------------------------------------------------transactioned---
# XXX transaction decorator...
def transactioned():
	'''
	'''
	return



#-----------------------------------------------------------------------
#-------------------------------------------------registertypehandler---
# XXX can this be made into a generic dispatch decorator???
def registertypehandler(type):
	'''
	'''
	handlers = sys._getframe(1).f_locals['_typehandlers']
	def handler(func):
		handlers[type] = func
		return func
	return handler


#-----------------------------------------------------------SQLWriter---
##!! REVISE !!##
##!!! ADD FUNCTIONS AND OTHER TYPES (fallback to pickle) !!!##
# XXX this is not able to pickle extension types... (fix?)
# TODO make an atomic type handler constructor... (should this be
#      decoratable??)
# TODO make ALL of thefolowing packable into transactions...
# XXX needs more pedantic checking...
# XXX add value check for mutable objects... (if value exists then
# XXX do update...
#     return old id...)
class SQLWriter(object):
	'''
	'''
	_typehandlers = {}

	__object_native_attrs__ = ('__dict__', '__class__')

	def __init__(self, sql):
		'''
		'''
		self.sql = sql
	# atomic type handlers...
	@registertypehandler(int)
	def do_int(self, o, oid=None):
		'''
		'''
		obj_id = self.sql.insert('py_object', type='py_int').lastrowid
		obj_id = self.sql.select('pyoid', 'py_object', self.sql.where(oid=obj_id)).fetchone()[0]
		self.sql.insert('py_int', pyoid=obj_id, value=o)
		return obj_id
	@registertypehandler(long)
	def do_long(self, o, oid=None):
		'''
		'''
		obj_id = self.sql.insert('py_object', type='py_long').lastrowid
		obj_id = self.sql.select('pyoid', 'py_object', self.sql.where(oid=obj_id)).fetchone()[0]
		self.sql.insert('py_long', pyoid=obj_id, value=o)
		return obj_id
	@registertypehandler(float)
	def do_float(self, o, oid=None):
		'''
		'''
		obj_id = self.sql.insert('py_object', type='py_float').lastrowid
		obj_id = self.sql.select('pyoid', 'py_object', self.sql.where(oid=obj_id)).fetchone()[0]
		self.sql.insert('py_float', pyoid=obj_id, value=o)
		return obj_id
##	@registertypehandler(complex)
##	def do_complex(self, o, oid=None):
##		'''
##		'''
##		pass
	@registertypehandler(str)
	def do_str(self, o, oid=None):
		'''
		'''
		obj_id = self.sql.insert('py_object', type='py_str').lastrowid
		obj_id = self.sql.select('pyoid', 'py_object', self.sql.where(oid=obj_id)).fetchone()[0]
		self.sql.insert('py_str', pyoid=obj_id, value=o)
		return obj_id
	@registertypehandler(unicode)
	def do_unicode(self, o, oid=None):
		'''
		'''
		obj_id = self.sql.insert('py_object', type='py_unicode').lastrowid
		obj_id = self.sql.select('pyoid', 'py_object', self.sql.where(oid=obj_id)).fetchone()[0]
		self.sql.insert('py_unicode', pyoid=obj_id, value=o)
		return obj_id
	@registertypehandler(tuple)
	def do_tuple(self, tpl, oid=None):
		'''

		py_tuple row format:
			pyoid(oid)	-> py_object.pyoid

		py_tuple_items row format:
			pyoid(oid)	-> py_tuple.pyoid
			order(int)
			value(oid)	-> py_object.pyoid
		'''
		obj_id = self.sql.insert('py_object', type='py_tuple').lastrowid
		obj_id = self.sql.select('pyoid', 'py_object', self.sql.where(oid=obj_id)).fetchone()[0]
		self.sql.insert('py_tuple', pyoid=obj_id)
		# XXX this might be bad as it will not track the HL object OIDs
		#     and thus might split some mutable objects in two or more
		#     independent versions...
		for i, o in enumerate(tpl):
			# insert the element...
			item_id = self.write(o)
			self.sql.insert('py_tuple_item', order=i, pyoid=obj_id, value=item_id)
		return obj_id
	# mutable handlers...
	@registertypehandler(list)
	def do_list(self, lst, oid=None):
		'''

		py_list row format:
			pyoid(oid)	-> py_object.pyoid

		py_list_items row format:
			pyoid(oid)	-> py_list.pyoid
			order(int)
			value(oid)	-> py_object.pyoid

		NOTE: if object id (oid) is given, the object will be updated.
		'''
		if oid != None:
			# XXX use the strategy of "keep the existing, add the new,
			#     remove the old."
			self.sql.delete('py_list_item', self.sql.where(pyoid=oid))
			obj_id = oid
		else:
			obj_id = self.sql.insert('py_object', type='py_list').lastrowid
			obj_id = self.sql.select('pyoid', 'py_object', self.sql.where(oid=obj_id)).fetchone()[0]
			self.sql.insert('py_list', pyoid=obj_id)
		# insert the list items...
		# XXX this might be bad as it will not track the HL object OIDs
		#     and thus might split some mutable objects in two or more
		#     independent versions...
		for i, o in enumerate(lst):
			item_id = self.write(o)
			self.sql.insert('py_list_item', order=i, pyoid=obj_id, value=item_id)
		return obj_id
	@registertypehandler(dict)
	def do_dict(self, dct, oid=None):
		'''

		py_dict row format:
			pyoid(oid)	-> py_object.pyoid

		py_dict_items row format:
			pyoid(oid)	-> py_dict.pyoid
			key(oid)	-> py_object.pyoid
			value(oid)	-> py_object.pyoid

		NOTE: if object id (oid) is given, the object will be updated.
		'''
		if oid != None:
			# XXX use the strategy of "keep the existing, add the new,
			#     remove the old."
			self.sql.delete('py_dict_item', self.sql.where(pyoid=oid))
			obj_id = oid
		else:
			obj_id = self.sql.insert('py_object', type='py_dict').lastrowid
			obj_id = self.sql.select('pyoid', 'py_object', self.sql.where(oid=obj_id)).fetchone()[0]
			self.sql.insert('py_dict', pyoid=obj_id)
		# insert the items...
		# XXX this might be bad as it will not track the HL object OIDs
		#     and thus might split some mutable objects in two or more
		#     independent versions...
		for k, v in dct.items():
			key_id = self.write(k)
			val_id = self.write(v)
			self.sql.insert('py_dict_item', pyoid=obj_id, key=key_id, value=val_id)
		return obj_id
	@registertypehandler(object)
	def do_object(self, obj, oid=None):
		'''

		NOTE: if object id (oid) is given, the object will be updated.
		'''
		if oid != None:
			# XXX use the strategy of "keep the existing, add the new,
			#     remove the old."
			self.sql.delete('py_object_attribute', self.sql.where(pyoid=oid))
			obj_id = oid
		else:
			obj_id = self.sql.insert('py_object').lastrowid
			obj_id = self.sql.select('pyoid', 'py_object', self.sql.where(oid=obj_id)).fetchone()[0]

		for n in self.__object_native_attrs__:
			# insert the element...
##			name_id = self.write(n)
##			self.sql.insert('py_object_attribute', pyoid=obj_id, name=name_id, value=val_id)
			# the if here is to avoid special cases like None and Guido
			# knows what that may not have a special attr like __dict__
			# in the case of None.... #$%^&* 
			if hasattr(obj, n):
				val_id = self.write(getattr(obj, n))
				self.sql.insert('py_object_attribute', pyoid=obj_id, name=n, value=val_id)
		return obj_id
	# pickle handlers...
	##!!! check if the object is a class with a metaclass other than type...
	@registertypehandler(type)
	def do_class(self, cls, oid=None):
		'''
		'''
		obj_id = self.sql.insert('py_object', type='py_pickled_class').lastrowid
		obj_id = self.sql.select('pyoid', 'py_object', self.sql.where(oid=obj_id)).fetchone()[0]

		# for some reason pickle can't pickle NoneType....
		if cls == types.NoneType:
			cls = None

		self.sql.insert('py_pickled_class', 
							pyoid=obj_id, 
							pickle=pickle.dumps(cls))
		return obj_id
	@registertypehandler(types.FunctionType)
	def do_function(self, cls, oid=None):
		'''
		'''
		obj_id = self.sql.insert('py_object', type='py_pickled_function').lastrowid
		obj_id = self.sql.select('pyoid', 'py_object', self.sql.where(oid=obj_id)).fetchone()[0]

		self.sql.insert('py_pickled_function', 
							pyoid=obj_id, 
							pickle=pickle.dumps(cls))
		return obj_id
	# HL interface methods...
	# XXX make this support the pickle protocols...
	# XXX might be good to make this less strict and not use the
	#     explicit class of the object but rather test for subclass...
	#     ...might be good to make this a multi level test... first
	#     strict, then less strict... etc.
	##!!! REVISE
	def write(self, obj, oid=None):
		'''
		'''
		t = type(obj)
		handler = self._typehandlers.get(t, None)
		if handler is None:
			##!!! do a less strict test...
			return self.do_object(obj, oid)
		return handler(self, obj, oid)
	##!!! REVISE
	def writebyname(self, name, obj):
		'''
		'''
		oid = self.write(obj)
		obj_id = self.sql.insert('py_registry', name=name, pyoid=oid)
		return oid



#-----------------------------------------------------------------------
#--------------------------------------------------------------Object---
# WARNING: do not modify this here!
class Object(object):
	'''
	abstract class used in object reconstruction.
	'''
	pass


#------------------------------------------------registertablehandler---
# XXX can this be made into a generic dispatch decorator???
def registertablehandler(table_name):
	'''
	'''
	handlers = sys._getframe(1).f_locals['_tablehandlers']
	def handler(func):
		handlers[table_name] = func
		return func
	return handler


#-----------------------------------------------------------SQLReader---
##!! REVISE !!##
##!!! ADD FUNCTIONS AND OTHER TYPES (fallback to pickle) !!!##
# TODO add lazy reconstruction option for mutable and deep objects...
# TODO make an atomic type handler constructor... (should this be
#      decoratable??)
# TODO make the table names configurable....
class SQLReader(object):
	'''
	'''
	_tablehandlers = {}

	def __init__(self, sql):
		'''
		'''
		self.sql = sql
	# atomic handlers...
	@registertablehandler('py_int')
	def do_int(self, oid):
		'''
		'''
		# sanity checks...
		# XXX check if object exists (else panic?)
		# get the object...
		o = self.sql.select('value', 'py_int', self.sql.where(pyoid=oid)).fetchone()[0]
		# XXX reconstruct attrs...
		return o
	@registertablehandler('py_long')
	def do_long(self, oid):
		'''
		'''
		# sanity checks...
		# XXX check if object exists (else panic?)
		# get the object...
		o = self.sql.select('value', 'py_long', self.sql.where(pyoid=oid)).fetchone()[0]
		# XXX reconstruct attrs...
		return o
	@registertablehandler('py_float')
	def do_float(self, oid):
		'''
		'''
		# sanity checks...
		# XXX check if object exists (else panic?)
		# get the object...
		o = self.sql.select('value', 'py_float', self.sql.where(pyoid=oid)).fetchone()[0]
		# XXX reconstruct attrs...
		return o
##	@registertablehandler('py_complex')
##	def do_complex(self, oid):
##		'''
##		'''
##		pass
	@registertablehandler('py_str')
	def do_str(self, oid):
		'''
		'''
		# sanity checks...
		# XXX check if object exists (else panic?)
		# get the object...
		o = self.sql.select('value', 'py_str', self.sql.where(pyoid=oid)).fetchone()[0]
		# XXX reconstruct attrs...
		return o
	@registertablehandler('py_unicode')
	def do_unicode(self, oid):
		'''
		'''
		# sanity checks...
		# XXX check if object exists (else panic?)
		# get the object...
		o = self.sql.select('value', 'py_unicode', self.sql.where(pyoid=oid)).fetchone()[0]
		# XXX reconstruct attrs...
		return o
	@registertablehandler('py_tuple')
	def do_tuple(self, oid):
		'''
		'''
		# sanity checks...
		# XXX check if object exists (else panic?)
		# get the object...
		##!!!
		o = list(self.sql.select(('order', 'value'), 'py_tuple_item', self.sql.where(pyoid=oid)).fetchall())
		o.sort()
		o = tuple([ self.get(e) for (i, e) in o ])
		# XXX reconstruct attrs...
		return o
	# mutable handlers...
	@registertablehandler('py_list')
	def do_list(self, oid):
		'''
		'''
		# sanity checks...
		# XXX check if object exists (else panic?)
		# get the object...
		o = list(self.sql.select(('order', 'value'), 'py_list_item', self.sql.where(pyoid=oid)).fetchall())
		o.sort()
		o = [ self.get(e) for (i, e) in o ]
		# XXX reconstruct attrs...
		return o
	@registertablehandler('py_dict')
	def do_dict(self, oid):
		'''
		'''
		# sanity checks...
		# XXX check if object exists (else panic?)
		# get the object...
		o = list(self.sql.select(('key', 'value'), 'py_dict_item', self.sql.where(pyoid=oid)).fetchall())
		o = dict([ (self.get(k), self.get(v)) for (k, v) in o ])
		# XXX reconstruct attrs...
		return o
	@registertablehandler('py_object')
	def do_object(self, oid):
		'''
		'''
		# sanity checks...
		# XXX check if object exists (else panic?)
		# get the object...
		dct = dict(self.sql.select(('name', 'value'), 'py_object_attribute', self.sql.where(pyoid=oid)).fetchall())
		# reconstruct attrs...
		for n, v in dct.items():
			dct[n] = self.get(v)
		cls = dct.pop('__class__')
		# there is only one None object and it is already created...
		if cls in (types.NoneType, None):
			return None
		# generate the object...
		o = Object()
		for n, v in dct.items():
			setattr(o, n, v)
		o.__class__ = cls
		return o
	# pickle handlers...
	@registertablehandler('py_pickled_class')
	def do_class(self, oid):
		'''
		'''
		# sanity checks...
		# XXX check if object exists (else panic?)
		# get the object...
		o = self.sql.select('pickle', 'py_pickled_class', self.sql.where(pyoid=oid)).fetchone()[0]
		o = pickle.loads(o)
		# NoneType is represented as None...
		if o == None:
			return types.NoneType
		# XXX reconstruct attrs...
		return o
	@registertablehandler('py_pickled_function')
	def do_function(self, oid):
		'''
		'''
		# sanity checks...
		# XXX check if object exists (else panic?)
		# get the object...
		o = self.sql.select('pickle', 'py_pickled_function', self.sql.where(pyoid=oid)).fetchone()[0]
		o = pickle.loads(o)
		# XXX reconstruct attrs...
		return o
	# HL interface methods...
	def get_oid(self, name):
		'''
		'''
		try:
			return self.sql.select('pyoid', 'py_registry', self.sql.where(name=name)).fetchone()[0]
		except:
			return None
	
	# XXX make this support the pickle protocols...
	def get(self, oid):
		'''
		'''
		if type(oid) is str:
			oid = self.sql.select('pyoid', self.sql.where(name=oid)).fetchone()[0].rstrip()
		t = self.sql.select('type', 'py_object', self.sql.where(pyoid=oid)).fetchone()[0].rstrip()
		# NOTE: here we compensate for a sideeffect of decorating
		#       methods while the class is not there yet...
		return self._tablehandlers[t](self, oid)



#-----------------------------------------------------------------------
#--------------------------------------------------------SQLInterface---
# TODO special interfaces for item access of lists and dicts...
# TODO special interfaces for object length and partial data (like dict
#      keys, values... etc.)
# TODO compleat the types...
# TODO pass the transation id arround to enable:
# 		1) query collection into one big SQL expression.
# 		2) manage multiple transactions over one or several connections
# 		   at the same time...
# TODO keep in mind the object id of mutable objects.
# NOTE: might be a good idea to track the object id in two layers:
#	 		1) save time (id in the database. unique in the db)	-- sOID
# 			2) restore time (id in runtime)						-- pOID
# 		the idea is to keep a record of both ids to be able to link the
# 		stored object to its' live version.
# 		when only one id is present, it means that the object is either
# 		not yet saved or not yet read from db. if both are present,
# 		then we have both versions of the object.
#
# TODO rename this!
# TODO add transaction hooks and wrappers...
# TODO split this into an abstract sql interface and a caching
#      sql interface...
class AbstractSQLInterface(object):
	'''
	'''
	__sql_reader__ = None
	__sql_writer__ = None

	def __init__(self):
		'''
		'''
		self._liveobjects = {}
	# helpers...
	def __update__(self, oid, obj):
		'''
		be stupid and update.

		overloadable.

		WARNING: not intended for direct use.
		'''
		##!!!
		return self.__sql_writer__.write(obj, oid)
	def __insert__(self, a, b=None):
		'''
		be stupid and insert.

		overloadable.

		WARNING: not intended for direct use.
		'''
		if b == None:
			return self.__sql_writer__.write(a)
		##!!!
		return self.__sql_writer__.writebyname(a, b)
	def __select__(self, oid):
		'''
		be stupid and get.

		overloadable.

		WARNING: not intended for direct use.
		'''
		##!!!!!!
		return self.__sql_reader__.get(oid)
	def __name2oid__(self, name):
		'''
		'''
		return self.__sql_reader__.get_oid(name)
	# interface methods
	# XXX make this simpler!
	def write(self, a, b=None):
		'''

		this can be one of:
			write(obj) -> OID
			write(name, obj) -> OID

		NOTE: in case #2 obj can not be None.
		'''
		if b == None:
			obj = a
			name = b
		else:
			obj = b
			name = a
		# 1) see if object has a sOID, if yes check if it is locked, if
		#    not then update...
		# 2) disect and write/update...
		#
		pOID = id(obj)
		tbl = dict([ (b, a) for a, b in self._liveobjects.keys() ])
		if pOID in tbl.keys():
			# update
			sOID = tbl[pOID]
			return self.__update__(sOID, obj)
		else:
			# write
			if name != None:
				# insert name to registry...
				sOID = self.__insert__(name, obj)
			else:
				sOID = self.__insert__(obj)
			self._liveobjects[(sOID, pOID)] = obj
			return sOID
	# TODO add hook for live obj condition...
	def get(self, sOID):
		'''
		'''
		# 1) see if object is live, if yes see if it is locked or dirty (in
		#    a transaction?), if so then warn.... (???)
		# 2) construct object.
		# 3) save sOID, pOID, ref in self._liveobjects
		#
		name = None
		# get object id by name...
		if not self.isoid(sOID):
			name = sOID
			sOID = self.__name2oid__(sOID)
			if sOID == None:
				raise KeyError, 'object "%s" does not exist in DB.'
		# get the object...
		tbl = dict(self._liveobjects.keys())
		if sOID in tbl.keys():
			##!!! add hook...
##			print 'WARNING: object already open.'
			return self._liveobjects[(sOID, tbl[sOID])]
		obj = self.__select__(sOID)
		self._liveobjects[(sOID, id(obj))] = obj
		return obj
	##!!!
	def delete(self, sOID):
		'''
		'''
		raise NotImplementedError
	# registry specific methods...
	def isoid(self, o):
		'''
		'''
		return type(o) in (int, long)



if __name__ == '__main__':

	import psycopg2 as psycopg
	import sql

	DBHOST = 'localhost'
##	DBHOST = 'mozg.cis.bigur.ru'
	DBDATABASE = 'poker'
	DBUSER = 'f_lynx'
	PASSWORD = '1234567'

	dbcon = psycopg.connect('host=%s dbname=%s user=%s password=%s' \
											% (DBHOST, DBDATABASE, DBUSER, PASSWORD))

	sqlobj = sql.SQL(dbcon)

	sqlinterface = AbstractSQLInterface()

	sqlinterface.__sql_reader__ = SQLReader(sqlobj)
	sqlinterface.__sql_writer__ = SQLWriter(sqlobj)


	i = 2985
	d = sqlinterface.get(i)

##	d = {1:1,2:2,3:3}
##	#sqlinterface.write('aaaa', d)
##	i = sqlinterface.write(d)
##	sqlinterface.__sql_reader__.sql.connection.commit()

	print '>>>', i, sqlinterface.get(i)

	d['xxx'] = 'xxx'
	d['yyy'] = 'yyy'

	i = sqlinterface.write(d)
	sqlinterface.__sql_reader__.sql.connection.commit()

	print '>>>', i, sqlinterface.get(i)

	sqlinterface.__sql_reader__.sql.connection.commit()




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
