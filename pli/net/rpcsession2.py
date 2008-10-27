#=======================================================================

__version__ = '''0.4.00'''
__sub_version__ = '''20081022134745'''
__copyright__ = '''(c) Alex A. Naanou 2008'''


#-----------------------------------------------------------------------

import time
import random
import sha

import pli.objutils as objutils
import pli.logictypes as logictypes

from pli.logictypes import ANY, isident


#-----------------------------------------------------------------------

SID_CHARS = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
			'abcdefghijklmnopqrstuvwxyz' \
			'0123456789' \
			## '._-@#'


#-----------------------------------------------------------------------
#
# Q: is the dispatch model the only/best possible here?
#
#
#-----------------------------------------------------------------------
#--------------------------------------------------------SessionError---
class SessionError(Exception):
	'''
	'''



#-----------------------------------------------------------------------
#-------------------------------------------------------------Session---
# use this for ACL and basic session event handlers...
# TODO split this into several mixins...
class BaseSession(object):
	'''
	this is the generic RPC session class.

	this provides basic password support.
	'''
	def __hashpassword__(self, text):
		'''
		process the password text.

		NOTE: this should produce stable results.
		'''
		return text
	# LL password and security...
	def _setpassword(self, password):
		'''
		'''
		if password in (None, ''):
			self._password = None
		else:
			self._password = self.__hashpassword__(password)
	def checkpassword(self, password):
		'''
		'''
		if hasattr(self, '_password') and self._password not in ('', None):
			return self._password == self.__hashpassword__(password)
		return True
	
	# User level password and security...
	def changepassword(self, old_pswd, new_pswd):
		'''
		'''
		# check the old password...
		if not self.checkpassword(old_pswd):
			raise SessionError, 'can\'t change password.'
		# change the password...
		self._setpassword(new_pswd)
	
	# low level event handlers...
	# XXX rename into __<name>__
	def _onSessionOpen(self):
		'''
		'''
		# fire the event...
		if hasattr(self, 'onSessionOpen'):
			self.onSessionOpen()
	# XXX rename into __<name>__
	def _onSessionClose(self):
		'''
		'''
		# fire the event...
		if hasattr(self, 'onSessionClose'):
			self.onSessionClose()
	
	# Session event handlers 
	# NOTE: these are here for documentation only...
	# XXX rename into __<name>__
##	def onSessionOpen(self):
##		'''
##		this is called on session open.
##		'''
	# XXX rename into __<name>__
##	def onSessionClose(self):
##		'''
##		this is called on session open.
##		'''


#------------------------------------SessionWithSHA1PasswordHashMixin---
class SessionWithSHA1PasswordHashMixin(object):
	'''
	this mixin uses the sha1 hash to hash and store passwords.
	'''
	def __hashpassword__(self, text):
		'''
		produce a sha1 hash from the text.
		'''
		return sha.sha(text).hexdigest()


#----------------------------------SessionWithResettablePasswordMixin---
class SessionWithResettablePasswordMixin(object):
	'''
	add a method for semi-automatic password resetting.
	'''
	def _resetpassword(self, chars=SID_CHARS, plen=8):
		'''
		set the password to a randomly generated text and return it.
		'''
		password = ''.join(random.sample(chars, plen))
		self._setpassword(password)
		return password


#------------------------------------SessionWithPropertyPasswordMixin---
class SessionWithPropertyPasswordMixin(object):
	'''
	add a .password property.

	this will enable direct password writing but, only if the password is
	either not set or is empty.

	NOTE: if the password is set use .changepassword(...) method to change it.
	'''
	password = property(
				doc='''password attribute.
				
				NOTE: this is write only, the hash can not be read.
				NOTE: writing to this is only possible if the password is empty.''',
				fset=lambda s, v: (not hasattr(s, '_password') \
										or s._password not in ('', None)) \
									and s._setpassword(v))
	

#-------------------------------------------SessionWithSessionNSMixin---
# XXX add filter to write some attrs to __session_ns__
# XXX add interface methods...
class SessionWithSessionNSMixin(object):
	'''
	'''
	# temporary session namespace... (created on login and removed on
	# logout)
	__session_ns__ = None

	def __getattr__(self, name):
		'''
		'''
		if self.__session_ns__ != None and name in self.__session_ns__:
			return self.__session_ns__[name]
		raise AttributeError, '%s object has no attribute "%s"' % (self, name)
	def __getstate__(self):
		'''
		this is a generic getstate...
		'''
		# remove the __session_ns__ contents...
		d = self.__dict__.copy()
		if '__session_ns__' in d:
			del d['__session_ns__']
		return d
	def __setstate__(self, data):
		'''
		this is a generic setstate mothod...
		'''
		self.__dict__.update(data)
	
	# low level event handlers...
	# XXX rename into __<name>__
##	def _onSessionOpen(self, manager):
	def _onSessionOpen(self):
		'''
		'''
		# set the temporary namespace...
		self.__session_ns__ = {}
##		super(SessionWithSessionNSMixin, self)._onSessionOpen(manager)
		super(SessionWithSessionNSMixin, self)._onSessionOpen()
	# XXX rename into __<name>__
##	def _onSessionClose(self, manager):
	def _onSessionClose(self):
		'''
		'''
		# delete the temporary namespace...
		if hasattr(self, '__session_ns__'):
			del self.__session_ns__
		# fire the event...
##		super(SessionWithSessionNSMixin, self)._onSessionClose(manager)
		super(SessionWithSessionNSMixin, self)._onSessionClose()


#------------------------------SessionWithSessionNSAndAttrFilterMixin---
class SessionWithSessionNSAndAttrFilterMixin(SessionWithSessionNSMixin):
	'''
	'''
	# attrs that will get written to session ns...
	__session_attrs__ = ()

	def __setattr__(self, name, val):
		'''
		'''
		if name in self.__session_attrs__:
			if self.__session_attrs__ == None:
				self.__session_attrs__ = {}
			self.__session_ns__[name] = val
		else:
			super(SessionWithSessionNSAndAttrFilterMixin, self).__setattr__(name, val)


#-------------------------------------------------------------Session---
class Session(SessionWithSHA1PasswordHashMixin,
					SessionWithResettablePasswordMixin,
					SessionWithPropertyPasswordMixin,
					SessionWithSessionNSAndAttrFilterMixin, 
					BaseSession):
	'''
	'''
	pass


#-----------------------------------------------------------------------
# TODO write mixins with the folowing features:
# 		- session events (split from existing)
# 		- RPC
# 		- password check (split out of existing???)
#--------------------------------------------------BaseSessionManager---
class BaseSessionManager(object):
	'''
	this class provides the generic RPC session interface.

	configuration attributes:
		XXX

	methods:
		XXX

	NOTE: __prepare_data__ depends on __new_sid__ output format.
	'''
	# data containers...
	# this will define the session object container (must be dict-like).
	# format: 
	# 	{OID: <obj>}
	__session_objects__ = None
	# define the active session container object (defaults to dict). 
	# format: 
	# 	{SID: (OID: <obj>)}
	# NOTE: it is not recommended to modify this manualy.
	__active_sessions__ = None

	# configuration...
	# if this is set password checking will be enabled...
	# NOTE: for this to function the session object must have a
	#       "checkpassword" method (see the Session class for details).
	__password_check__ = True
	# if True will prevent opening two connection for one session object.
	__unique_session__ = True
	##!!! think about this...
##	# if this is true then if a name is not found as an attribute it
##	# will be requested using the item protocol...
##	__item_protocol_in_path__ = True

	# session object event names (methods)...
	__session_open_event_name__ = '_onSessionOpen'
	__session_close_event_name__ = '_onSessionClose'
	# call argument name that contains the SID... 
	__sid_kw__ = 'SID'
	# sid length (not counting the __sid_prefix__)
	__sid_length__ = 40
	__sid_seed__ = 10
	# prefix to be added to sid (to ease recognition)...
	__sid_prefix__ = 'SID:'
	# charactes allowed in a SID... 
	__sid_chars__ = SID_CHARS
	# methods accesible from the root directly... (used by .dispatch(...))
	__system_methods__ = (
			'login',
			'logout',
			'isalive'
			)

	def __init__(self):
		'''
		'''
		if self.__active_sessions__ is None:
			self.__active_sessions__ = {}
		# XXX termsuper?
	# interface methods...
	##!!! add sanity checks... (path==None?)
	##!!! add default call if path is []
	def dispatch(self, path, *p, **n):
		'''
		dispatch method.

		NOTE: this is first level dispatch, this essentially calls the 
		      system method, if applicable, else, normolizes the input
			  (.__prepare_data__(...) method) and calls ._dispatch(...).
		'''
		##!!! add sanity checks... (path==None?)
		# check type of call (system or session)...
		if path[0] in self.__system_methods__:
			return getattr(self, path[0])(*p, **n)
		# get the sid / normolize inputs...
		SID, path, p, n = self.__prepare_data__(path, *p, **n)
		# check session object age...
		if not self.isalive(SID):
			self.__session_manager_error__('SID does not exist.', SID)
			raise SessionError, 'no such session.'
		# do the actual dispatch...
		return self._dispatch(SID, path, *p, **n)
	# do the session method call...
	# XXX rename into __<name>__
	def _dispatch(self, SID, path, *p, **n):
		'''
		second level dispatch.

		get the object and call it.

		this does the folowing:
			- get the session.
			- prepare the path if .__prepare_path__ is defined.
			- get the object via the .__get_by_path__ method.
			- call the object and return the result.
		'''
		# get the session context...
		session = self.__active_sessions__[SID][1]
		# prepare the path...
		if hasattr(self, '__prepare_path__'):
			path = self.__prepare_path__(session, path)
		# make the call...
		return self.__get_by_path__(session, path)(*p, **n)
	# system methods...
	def login(self, OID, password='', *p, **n):
		'''
		'''
		obj = self.__getsession__(OID)
		# check password...
		if self.__password_check__ \
				and hasattr(obj, 'checkpassword') \
				and not obj.checkpassword(password):
			self.__session_manager_error__('wrong password.', OID, password=password)
			raise SessionError, 'no such context (%s).' % OID
		# check if already loged in... (XXX keep here?)
		if (OID, ANY) in self.__active_sessions__.values() \
				and self.__unique_session__ \
				or (hasattr(obj, '__unique_session__') \
					and obj.__unique_session__):
			raise SessionError, 'can\'t open two sessions for this object (%s).' % OID
		# generate SID...
		while True:
			SID = self.__new_sid__(self.__sid_length__, self.__sid_seed__, self.__sid_prefix__)
			if SID not in self.__active_sessions__:
				break
		# register session as active... 
		self.__active_sessions__[SID] = (OID, obj)
		# fire open event... (XXX keep here?)
		if hasattr(obj, self.__session_open_event_name__):
			getattr(obj, self.__session_open_event_name__)()
		# done...
		return SID
	def logout(self, SID, *p, **n):
		'''
		'''
		# ignore bad sids...
		if SID not in self.__active_sessions__:
			return
		obj = self.__active_sessions__[SID][1]
		# fire open event... (XXX keep here?)
		if hasattr(obj, self.__session_close_event_name__):
			getattr(obj, self.__session_close_event_name__)()
		# remove the session...
		del self.__active_sessions__[SID]
	def isalive(self, SID):
		'''
		'''
		if SID in self.__active_sessions__:
			return True
		return False
	# internal methods...
	def __getsession__(self, OID):
		'''
		'''
		# get session context...
		obj = self.__session_objects__.get(OID, None)
		# check session object...
		if obj is None:
			self.__session_manager_error__('oid does not exist.', OID)
			raise SessionError, 'no such context (%s).' % OID
		return obj
##	def _get_session_by_sid(self, SID):
##		'''
##		'''
##		pass
	def __new_sid__(self, length=20, seed=8, prefix=None):
		'''
		will generate a session id...
		'''
		res = []
		# generate pool...
		while len(res) < (length * seed):
			res += random.sample(self.__sid_chars__, seed * 2)
		random.shuffle(res)
		res = ''.join(random.sample(res, length))
		if prefix != None:
			res = prefix+res
		return res
	##!!! possible problem with an expired sid that does not get noticed... 
	##!!! (need a more clever way to destingwith a sid)
	def __prepare_data__(self, path, *p, **n):
		'''
		get the SID out of the input data.

		NOTE: this enables different input formats, where SID can be given 
		      in the path as well as in the args...
		NOTE: None will be returned in place of SID if none is found.
		NOTE: this will return None in place of SIDs that are not in __active_sessions__.
		'''
		sid = n.pop(self.__sid_kw__, None)
		prefix = self.__sid_prefix__ or ''
		# XXX is this correct???
		if sid is None:
			# guessing if the first arg is a sid... (if
			# prefix is either None or '' we can't guess
			# reliably enough) 
##			if len(p) > 0 and p[0] in self.__active_sessions__\
##						or (prefix != '' and type(p[0]) in (str, unicode) \
##								and len(p[0]) == self.__sid_length__ + len(prefix) \
##								and set(p[0][len(prefix):]).issubset(self.__sid_chars__) \
##								and p[0].startswith(prefix)):
			if len(p) > 0 and (p[0] in self.__active_sessions__\
						or (type(p[0]) in (str, unicode) \
								and len(p[0]) == self.__sid_length__ + len(prefix) \
								and set(p[0][len(prefix):]).issubset(self.__sid_chars__) \
								and p[0].startswith(prefix))):
					# possibly we have a sid...
					##!!! are there other criteria?
					sid, p = p[0], p[1:]
		return sid, path, p, n 
##	def __prepare_path__(self, session, path):
##		'''
##		'''
##		return path
	# XXX need a version of this supporting both attr and item
	#     protocols... (???)
	def __get_by_path__(self, session, path):
		'''
		get an object by path using the attribute protocol.
		'''
		obj = session
		for name in path:
			obj = getattr(obj, name)
		return obj
	# XXX think of a format...
	def __session_manager_error__(self, reason, *p, **n):
		'''
		'''
		print '### error:', reason, p, n



#-----------------------------------------------------------------------
#-------------------------------SessionManagerWithItemPathGetterMixin---
class SessionManagerWithItemPathGetterMixin(object):
	'''
	'''
	def __get_by_path__(self, session, path):
		'''
		get an object by path.

		NOTE: this will use pure item access protocol.
		'''
		obj = session
		for name in path:
			obj = obj[name]
		return obj


#--------------------------SessionManagerWithItemNAttrPathGetterMixin---
class SessionManagerWithItemNAttrPathGetterMixin(object):
	'''
	'''
	def __get_by_path__(self, session, path):
		'''
		get object by path using either the attribute or the item protocol.

		if a path element is not an identifier or is not accessible ad an attr 
		the use the attr protocol, else, use the item protocol.

		NOTE: in this approach attributes have greater priority and shadow
		      items with the same name/key.
		'''
		obj = session
		for name in path:
			if isident(name):
				obj = getattr(obj, name, obj[name])
			else:
				obj = obj[name]
		return obj


#-----------------------------SessionManagerWithBasicPathTestingMixin---
class SessionManagerWithBasicPathTestingMixin(object):
	'''
	'''
	# XXX rename this...
	__special_name_exceptions__ = (
			# XXX is this correct??
			'__doc__',
			'__str__',
			)

	def __prepare_path__(self, session, path):
		'''
		'''
		npath = objutils.termsuper(SessionManagerWithBasicPathTestingMixin, self).__prepare_path__(session, path)
		if npath != None:
			path = npath
		for i in path:
			if i.startswith('_') and i not in self.__special_name_exceptions__:
				self.__session_manager_error__(('%s atempted read of private attr: %s.' % (session, i)), path)
				raise SessionError, 'can\'t read path elements starting with "_" (got: %s).' % i
		return path


#--------------------------------SessionManagerWithSessionWraperMixin---
class SessionManagerWithSessionWraperMixin(object):
	'''
	'''
	__session_wrapper__ = None

	def __getsession__(self, SID):
		'''
		'''
		session = super(SessionManagerWithSessionWraperMixin, self).__getsession__(SID)
		if self.__session_wrapper__ != None:
			session = self.__session_wrapper__(session)
		return session


#--------------------------------SessionManagerWithRequestWraperMixin---
class SessionManagerWithRequestWraperMixin(object):
	'''
	'''
	__session_request_wrapper__ = None

	def __get_by_path__(self, session, path):
		'''
		'''
		if self.__session_request_wrapper__ != None:
			session = self.__session_request_wrapper__(session)
		return super(SessionManagerWithRequestWraperMixin, self).__get_by_path__(session, path)


#------------------------------SessionManagerWithSessionCheckingMixin---
class SessionManagerWithSessionCheckingMixin(object):
	'''

	this needs at least __check_session__ defined.
	'''
	def _dispatch(self, SID, *p, **n):
		'''
		'''
		self.__check_session__(SID)
		return super(SessionManagerWithSessionCheckingMixin, self)._dispatch(SID, *p, **n)
	def login(self, OID, *p, **n):
		'''
		'''
		# check if we are loged-in...
		if (OID, ANY) in self.__active_sessions__.values():
			# check all sessions for this object if they exist...
			[ self.__check_session__(sid) for sid, (oid, _) \
					in self.__active_sessions__.items() \
					if oid == OID ]
		# do login...
		SID = super(SessionManagerWithSessionCheckingMixin, self).login(OID, *p, **n)
		# check the object session...
		self.__check_session__(SID)
		return SID
	def isalive(self, SID):
		'''
		'''
		try:
			self.__check_session__(SID)
			return super(SessionManagerWithSessionCheckingMixin, self).isalive(SID)
		except SessionError:
			return False
	
	def __check_session__(self, SID):
		'''
		this can be expected to do the following:
		- logout the session and raising SessionError.
		  this behavior will result in .isalive(...) returning false.
		- raise other exceptions.
		- modify the session object.
		'''
		raise NotImplementedError
	def __check_sessions__(self):
		'''

		NOTE: this is not called automaticly (usually called on timer).
		'''
		for SID in self.__active_sessions__:
			self.__check_session__(SID)


#-------------------------------SessionManagerWithSessionTimeoutMixin---
class SessionManagerWithSessionTimeoutMixin(SessionManagerWithSessionCheckingMixin):
	'''
	'''
	# this sets the session global timeout (idle time before session
	# close), if None timeout checks will be disabled.
	__timeout__ = 1800.0
	# timout mode...
	# values:
	# 	min		- minimal value of session and manager timeout has effect.
	# 	session	- session timeout has priority.
	__timeout_mode__ = 'session'

	def __check_session__(self, SID):
		'''

		NOTE: this will logout the session if the time is up.
		NOTE: on logout this will raise a session error.
		'''
		# cache some data...
		now = time.time()
		timeout = self.__timeout__
		# if timeout is disabled abort...
		if timeout == None:
			return
		session = self.__active_sessions__.get(SID, None)
		if session == None:
			# session does not exist...
			self.__session_manager_error__('no such session.', SID)
			raise SessionError, 'no such session.'
		# get the actual session object...
		session = session[1]
		# check object timeout...
		stimeout = getattr(session, '__timeout__', None)
		if stimeout is not None:
			# check mode...
			if self.__timeout_mode__ == 'min':
				# select minimal timeout...
				timeout = min(timeout, stimeout)
			elif self.__timeout_mode__ == 'session':
				# session timeout has priority...
				timeout = stimeout
			else:
				# sanity check...
				raise TypeError, 'unsupported timeout mode.'
		# we see the object for the first time...
		##!!! possible bug: if the session deletes it's ._last_accessed it will get timeout extension...
		if not hasattr(session, '_last_accessed'):
			session._last_accessed = now
		# kill the session on timeout...
		elif session._last_accessed + timeout < now:
			# XXX this is not correct... (use a special base-class to set access time and make this use it)
			del self.__active_sessions__[SID][1]._last_accessed
			self.logout(SID)
			self.__session_manager_error__('session timeout.', SID)
##			# XXX should this fail here??
##			raise SessionError, 'session timeout.'
			return
		# set last accessed...
		self.__active_sessions__[SID][1]._last_accessed = now


#----------------------------SessionManagerWithPersistentSessionMixin---
class SessionManagerWithPersistentSessionMixin(object):
	'''

	provides persistent session capability.

	persistent session -- a session that will never be loged out.
	'''
	# NOTE: this is the same format as __active_sessions__ (see above)
	__persistent_sessions__ = None

	def __init__(self):
		'''
		'''
		if self.__active_sessions__ != None:
			raise Warning, 'defining the __active_sessions__ attr in the class'\
							' is not compatible with SessionManagerWithPersistentSessionMixin.'
		super(SessionManagerWithPersistentSessionMixin, self).__init__()
##		if self.__persistent_sessions__ == None:
##			self.__persistent_sessions__ = {}
		# setup a dict chain...
		self.__active_sessions__ = logictypes.livedictchainto(self, '__persistent_sessions__')

	def logout(self, SID):
		'''
		'''
		if self.__persistent_sessions__ is not None \
				and SID in self.__persistent_sessions__:
			return
		return super(SessionManagerWithPersistentSessionMixin, self).logout(SID)
	def isalive(self, SID):
		'''
		'''
		if self.__persistent_sessions__ is not None \
				and SID in self.__persistent_sessions__:
			return True
		return super(SessionManagerWithPersistentSessionMixin, self).isalive(SID)

	@objutils.classinstancemethod
	def regpersistent(self, SID, session):
		'''

		NOTE: for this to work on classes the .__persistent_sessions__ needs to
		      be defined and not None.
		'''
		if self.__persistent_sessions__ == None:
			self.__persistent_sessions__ = {}
		self.__persistent_sessions__[SID] = (None, session)
	@objutils.classinstancemethod
	def unregpersistent(self, SID):
		'''

		NOTE: for this to work on classes the .__persistent_sessions__ needs to
		      be defined and not None.
		'''
		del self.__persistent_sessions__[SID]


#-------------------------------SessionManagerWithDefaultSessionMixin---
class SessionManagerWithDefaultSessionMixin(SessionManagerWithPersistentSessionMixin):
	'''

	redirects all calls without a SID to a default session.
	'''
	__default_sid__ = None

	def __prepare_data__(self, path, *p, **n):
		'''
		'''
		SID, path, n, p = super(SessionManagerWithDefaultSessionMixin, self).__prepare_data__(path, *p, **n)
		if SID == None:
			SID = self.__default_sid__
		return SID, path, n, p

	@objutils.classinstancemethod
	def regdefault(self, SID, session):
		'''
		'''
		self.__default_sid__ = SID
		self.regpersistent(SID, session)
	@objutils.classinstancemethod
	def unregdefault(self, session):
		'''
		'''
		self.__default_sid__ = None
		self.unregpersistent(SID, session)


#--------------------------------SessionManagerWithGlobalMethodsMixin---
# XXX might be a good idea to make the source of global methods
#     customizable...
class SessionManagerWithGlobalMethodsMixin(object):
	'''

	this needs at least __is_global_method__ defined.

	global method format:
		<session-manager>.<method>(SID, session, path, obj, *p, **n) -> <res>

	NOTE: this was not intended to be used directly.
	NOTE: this does not define a particular scheme to define global methods.
	'''
	def _dispatch(self, SID, path, *p, **n):
		'''
		'''
		if self.__is_global_method__(path[-1]):
			return self.__call_global__(SID, path, *p, **n)
		return super(SessionManagerWithGlobalMethodsMixin, self)._dispatch(SID, path, *p, **n)

	def __is_global_method__(self, name):
		'''
		'''
		raise NotImplementedError
	def __call_global__(self, SID, path, *p, **n):
		'''
		'''
		session = self.__active_sessions__[SID][1]
		obj = self.__get_by_path__(session, path[:-1])
		return getattr(self, path[-1])(SID, session, path, obj, *p, **n)


#----------------------------SessionManagerWithListGlobalMethodsMixin---
class SessionManagerWithListGlobalMethodsMixin(SessionManagerWithGlobalMethodsMixin):
	'''
	'''
	__global_methods__ = ()

	def __is_global_method__(self, name):
		'''
		'''
		if name in self.__global_methods__:
			return True
		return False



#-----------------------------------------------------------------------
# pre-built classes...
#------------------------------------------------SimpleSessionManager---
class SimpleSessionManager(SessionManagerWithSessionTimeoutMixin, 
							SessionManagerWithDefaultSessionMixin,
							BaseSessionManager):
	'''
	'''
	pass


#------------------------------------------------------SessionManager---
class SessionManager(SessionManagerWithBasicPathTestingMixin,
						SessionManagerWithSessionWraperMixin,
						SessionManagerWithRequestWraperMixin,
						SessionManagerWithSessionTimeoutMixin, 
						SessionManagerWithDefaultSessionMixin,
						SessionManagerWithListGlobalMethodsMixin,
						BaseSessionManager):
	'''
	'''
	pass



#-----------------------------------------------------------------------
# other extensions...



#-----------------------------------------------------------------------
if __name__ == '__main__':

	##!!! there seams to be a bug with the login with password...

	class O(object):
		def test(self):
			return 123
		def meth(self, *p, **n):
			print 'o.meth', p, n
			return 123
		def _meth(self):
			print 'o._meth'
			return 123

	class S(BaseSession):
		def meth(self, *p, **n):
			print 'o.meth', p, n
			return 123
		def _meth(self):
			print 'o._meth'
			return 123

	s = S()
	s._setpassword('123')

	class DFL(object):
		def meth(self, *p, **n):
			print 'dfl.meth', p, n
			return 123
		def _meth(self):
			print 'dfl._meth'
			return 123

	class TestSessionManager(SessionManager):
		__session_objects__ = {
			'test': O(),
			'test2': s
		}
		__timeout__ = 1

##	TestSessionManager.regdefault('0', DFL())

	sm = TestSessionManager()

	sm.regdefault('0', DFL())

	# direct call...
	sid = sm.login('test')
	sid2 = sm.login('test2', '123')

	print sid

	# benchmark a minimal clean request...
	n = 10000
	t0 = time.time()
	for i in xrange(n):
		sm.dispatch(['test'], sid)
	t1 = time.time()

	# nice latency, about 4200 requests per second on a 1GHz Centrino CPU
	print 'requests per second:', float(n)/(t1-t0)

	# relogin after we were loged-out on timeout...
	sid2 = sm.login('test2', '123')

	sm.dispatch(['meth'], sid)
	sm.dispatch(['meth'], sid2)
##	sm.dispatch(['_meth'], sid)
	sm.dispatch(['meth'], 5, SID=sid, moo='boo')
	sm.dispatch(['meth'])
##	sm.dispatch(['_meth'])

	print sm.dispatch(['isalive'], sid)
	print sm.dispatch(['isalive'], '0')

	sm.logout('0')
	print sm.dispatch(['isalive'], '0')

	sm.dispatch(['logout'], sid)

	print sm.dispatch(['meth'], 1, 2, m=6)

	# in this case the system can not reliably say that the argument is
	# a SID or not (as it is not in active sessions), thus it considers
	# it a normal positional argument. (partialy fixed)
	# XXX this may be a problem... (when a session timesout and the
	#     methods will be resolved to the default context and the SID
	#     will be passed as arg... (no errors!)
##	sm.dispatch(['meth'], sid)
	# this gives a correct error...
##	sm.dispatch(['meth'], SID=sid)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
