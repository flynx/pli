#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20060204023432'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

##!!! THIS MUST BE SYSTEM-WIDE FATAL !!!##
class ConnectionError(Exception):
	'''
	'''
	pass

#-------------------------------------------------------SQLConnection---
class SQLConnection(object):
	'''
	'''
	def __init__(self):
		'''
		'''
		pass
	def connect(self):
		'''
		'''
		pass
	def disconnect(self):
		'''
		'''
		pass


#--------------------------------------------------------PGConnection---
##!!!
import psycopg2 as psycopg

class PGConnection(SQLConnection):
	'''
	'''
	def __init__(self, host, db, user, passwd):
		'''
		'''
		self._host = host
		self._db = db
		self._user = user
		##!!!
		self._passwd = passwd

		self._connection = None
	def connect(self):
		'''
		'''
		con = self._connection = psycopg.connect('host=%s dbname=%s user=%s password=%s' \
											% (self._host, self._db, self._user, self._passwd))
	##!!! REVISE !!!##
	def disconnect(self):
		'''
		'''
		self._connection = None
	
	# HL interface methods
	def connection(self):
		'''
		'''
		try:
			cur = self._connection.cursor()
			cur.execute('SELECT 1;')
			if cur.fetchone() != (1,):
				raise Exception, 'unexpected return...'
		except Exception, e:
			self.connect()
		# return a live connection object...
		return self._connection
	def cursor(self, *p, **n):
		'''
		'''
		return self.connection().cursor(*p, **n)
	def commit(self):
		'''
		'''
		try:
			self._connection.commit()
		except:
			raise ConnectionError, 'connection lost. cannot commit!'
	def rollback(self):
		'''
		'''
		self._connection.rollback()
##		try:
##			self._connection.rollback()
##		except:
##			raise ConnectionError, 'connection lost. cannot commit!'



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
