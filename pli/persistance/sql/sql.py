#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20050824025606'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------




#-----------------------------------------------------------------------
#-------------------------------------------------------transactioned---
# XXX transaction decorator...
def transactioned():
	'''
	'''
	return



#-----------------------------------------------------------------------
#------------------------------------------------------------SQLError---
class SQLError(Exception):
	'''
	'''
	pass


#-----------------------------------------------------------------------
#--------------------------------------------------------------_WHERE---
##!!! THINK OF A BETTER WAY TO DO THIS !!!##
# XXX should the condition return the WHERE kw??
class _WHERE(object):
	'''
	compile and check a condition string...
	'''
	##!!! wrap values !!!##
	def __init__(self, *p, **n):
		'''
		'''
		if len(p) == 1 and type(p[0]) is str:
			self.condition = p[0]
		if len(p) == 0:
			self.condition = ' AND '.join([ '"%s" = %s' % (k, v) for k, v in n.items() ])
	def __str__(self):
		'''
		'''
		c = self.condition
		return str(c)
	def __repr__(self):
		'''
		'''
		return str(self.condition)



#-----------------------------------------------------------------------
#-----------------------------------------------------------------SQL---
# XXX Revise extensibility to other SQL dialects...
# TODO rename to pgSQL
class SQL(object):
	'''
	'''
	# the condition clause processor...
	where = _WHERE

	def __init__(self, connection, cursor):
		'''
		'''
		self.connection = connection
		self.cursor = cursor
	# utility methods
	def checksqlname(self, name):
		'''
		'''
		return '"%s"' % name.replace('"', '\\"')
	##!!! REWRITE !!!##
	def py2sql(self, value):
		'''
		translate a value into an apropriate sql type.
		'''
		t = type(value)
		if t in (int, float, long):
			return str(value)
		if t in (str, unicode):
			##!!! WRONG !!!##
			return '\'%s\'' % value
		if value is None:
			return 'NULL'
		raise TypeError, 'can\'t convert objects of type %s.' % t
	##!!!
	def sql2py(self, value):
		'''
		'''
		pass
	# SQL expression generators
	# TODO add other expressions... (CREATE, DROP, ...)
	# TODO make these dialect independent...
	# TODO add filter support for select (e.g. rename columns... etc.)
	# TODO write more docs...
	##!!! TODO more pedantic input checking!
	def select_sql(self, columns, source, 
						condition=None, 
						order=None, 
						# XXX the next two appear to PostgresSQL
						#     specific... REVISE!
						count=None, 
						offset=None):
		'''

		SQL Syntax Reference:
			
		'''
		# cahe some names...
		py2sql = self.py2sql
		checksqlname = self.checksqlname

		# construct the source...
		##!!! CAN THIS BE ANOTHER SELECT HERE????
		source = checksqlname(source)

		# construct columns...
		# NOTE: columns can be:
		# 		- list
		# 		- dict (???)
		# 		- combination (???)
		if type(columns) is not str:
			columns = ', '.join([ checksqlname(n) for n in columns ])

		# process the condition...
		if condition is None:
			condition = ''
		elif type(condition) is self.where:
			condition = '\n\tWHERE ' + str(condition)
		else:
			condition = '\n\tWHERE ' + str(self.where(condition))

		# order...
		# XXX do we need direction here???
		if order != None:
			order = '\n\tORDER BY %s' % checksqlname(order)
		else:
			order = ''

		# count...
		if count != None:
			count = '\n\tLIMIT %s' % py2sql(count)
		else:
			count = ''

		# offset...
		if offset != None:
			offset = '\n\tOFFSET %s' % py2sql(offset)
		else:
			offset = ''

		return 'SELECT %(columns)s \n\tFROM %(source)s%(where)s%(count)s%(offset)s%(order)s ;' \
					% {'columns': columns, 
						'source': source, 
						'where': condition,
						'count': count,
						'order': order,
						'offset': offset,}
	# TODO make setting defaults possible... (e.g. clo_x=DEFAULT)
	# TODO support complex expression... (???)
	##!!! TODO more pedantic input checking!
	def insert_sql(self, table, *p, **n):
		'''
		generate an insert query.

		Format:
			insert_sql(<table_name>[, <value>[, ...]][, <column>=<value>[, ...]]) -> QUERY

		SQL Syntax Reference:
			INSERT INTO table [ ( column [, ...] ) ]
				{ DEFAULT VALUES | VALUES ( { expression | DEFAULT } [, ...] ) | query }
		'''
		# cahe some names...
		py2sql = self.py2sql
		checksqlname = self.checksqlname

		# prepare data...
		table = checksqlname(table)
		columns = n.keys()
		values = (tuple([ n[k] for k in columns ]) + p) or ''
		# sqlify the values...
		if values == '':
			columns = ' DEFAULT'
		else:
			values = '( %s ) ' % ', '.join([ py2sql(v) for v in values ])
			# sqlify the columns...
			if len(columns) == 0:
				columns = ''
			else:
				columns = ' ( %s )' % ', '.join([ checksqlname(n) for n in columns ])
		# generate the query...
		return 'INSERT INTO %s%s VALUES %s;' % (table, columns, values)
	# TODO support complex expression... (???)
	# TODO a more elaborate condition... (maybe a whwre method?)
	##!!! TODO more pedantic input checking!
	def update_sql(self, table, condition, *p, **n):
		'''
		
		Format:

		SQL Syntax Reference:
			UPDATE [ ONLY ] table SET column = { expression | DEFAULT } [, ...]
				[ WHERE condition ]
		'''
		# sanity checks...
		if len(n) == 0:
			raise SQLError, 'must update at least one column (none given)'
		# cahe some names...
		py2sql = self.py2sql
		checksqlname = self.checksqlname

		# prepare data...
		table = checksqlname(table)

		columns = ', '.join([ '%s = %s' % (checksqlname(k), py2sql(v)) for k, v in n.items() ])

		# process the condition...
		if condition is None:
			condition = ''
		elif type(condition) is self.where:
			condition = '\n\tWHERE ' + str(condition)
		else:
			condition = '\n\tWHERE ' + str(self.where(condition))

		# XXX should the condition return the WHERE kw??
		return 'UPDATE %s SET %s%s ;' % (table, columns, condition)
	##!!! TODO more pedantic input checking!
	def delete_sql(self, table, condition=None):
		'''

		Format:

		SQL Syntax Reference:
			DELETE FROM [ ONLY ] table [ WHERE condition ]
		'''
		# cahe some names...
		py2sql = self.py2sql
		checksqlname = self.checksqlname

		# prepare data...
		table = checksqlname(table)

		# process the condition...
		if condition is None:
			condition = ''
		elif type(condition) is self.where:
			condition = '\n\tWHERE ' + str(condition)
		else:
			condition = '\n\tWHERE ' + str(self.where(condition))

		return 'DELETE FROM %(table)s%(where)s ;' \
				% {'table': table,
					'where': condition}
	# methods
	# XXX make all of the following packable into transactions!!!
	# XXX do we need to process the result here???
	def select(self, columns, source, condition=None, 
						order=None, count=None, offset=None):
		'''
		'''
		cur = self.cursor()
		cur.execute(self.select_sql(columns, source, condition, order, count, offset))
		return cur
	def insert(self, table, *p, **n):
		'''
		'''
		cur = self.cursor()
		cur.execute(self.insert_sql(table, *p, **n))
		return cur
	def update(self, table, condition, *p, **n):
		'''
		'''
		cur = self.cursor()
		cur.execute(self.update_sql(table, condition, *p, **n))
		return cur
	def delete(self, table, condition=None):
		'''
		'''
		cur = self.cursor()
		cur.execute(self.delete_sql(table, condition))
		return cur



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
