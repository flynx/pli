#=======================================================================

__version__ = '''0.1.42'''
__sub_version__ = '''20041019040755'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#=======================================================================

import time
import random
import sha

import pli.interface as interface
##!! remove ...
import pli.misc.acl as acl
import pli.misc.passcrypt as passcrypt


#-----------------------------------------------------------------------
#--------------------------------------------------------SessionError---
class SessionError(Exception):
	'''
	'''



#-----------------------------------------------------------------------
#-------------------------------------------------------------Session---
# use this for ACL and basic session event handlers...
# TODO revise security settings!!!
# TODO revise mix-in criteria...
class Session(object):
	'''
	this is the generic RPC session class.

	this provides basic password support.
	'''
	# this is True if this object is public
	# NOTE: for the session object this MUST be True
	# NOTE: this will override the settings of the containers'
	#       private/public attrs...
	__public__ = True

	# setup interface...
	interface.inherit(iname='ISession')
	# private...
	interface.private('__public__')
	interface.private('__private_attrs__')
	interface.private('__public_attrs__')
	interface.private('__selector_class__')
	interface.private('_onSessionOpen')
	interface.private('_onSessionClose')
	interface.private('onSessionOpen')
	interface.private('onSessionClose')
	interface.private('checkpassword')
	interface.private('_setpassword')
	interface.private('password')
	# public...
	interface.add('changepassword', writable=False, deleteable=False)

	# this will define the private attributes
	__private_attrs__ = (
						  '__public__',
						  '__private_attrs__',
						  '__public_attrs__',
						  '__selector_class__',
						  '_onSessionOpen',
						  '_onSessionClose',
						  'onSessionOpen',
						  'onSessionClose',
						  'checkpassword',
						  '_setpassword',
						  'password',
						)

	def __getattr__(self, name):
		'''
		'''
		if hasattr(self, '__session_dict__') and name in self.__session_dict__:
			return self.__session_dict__[name]
		raise AttributeError, '%s object has no attribute "%s"' % (self, name)
	def __getstate__(self):
		'''
		this is a generic getstate...
		'''
		d = self.__dict__.copy()
		if '__session_dict__' in d:
			del d['__session_dict__']
		return d
	def __setstate__(self, data):
		'''
		this is a generic setstate mothod...
		'''
		self.__dict__.update(data)
	# LL password and security...
	def _setpassword(self, password):
		'''
		'''
		self.password = passcrypt.passcrypt_md5(password)
	def checkpassword(self, password):
		'''
		'''
		if hasattr(self, 'password') and self.password not in ('', None):
			return passcrypt.check_password_md5(password, self.password)
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
	def _onSessionOpen(self, manager):
		'''
		'''
		# set the temporary namespace...
##		if not hasattr(self, '__session_dict__'):
		self.__session_dict__ = {}
		# fire the event...
		if hasattr(self, 'onSessionOpen'):
			self.onSessionOpen(manager)
	def _onSessionClose(self, manager):
		'''
		'''
		# delete the temporary namespace...
		if hasattr(self, '__session_dict__'):
			del self.__session_dict__
		# fire the event...
		if hasattr(self, 'onSessionClose'):
			self.onSessionClose(manager)
	# Session event handlers 
	# NOTE: these are here for documentation only...
##	def onSessionOpen(self, manager):
##		'''
##		this is called on session open.
##
##		a session manager object is passed in...
##		'''
##	def onSessionClose(self, manager):
##		'''
##		this is called on session open.
##
##		a session manager object is passed in...
##		'''



#-----------------------------------------------------------------------
#---------------------------------------------------RPCSessionManager---
# TODO split this into diferent functionality primitives...
# 		- *global method call* functionality.
# 		- session
# 		- ...
# TODO global method install/unistall (may be session speciffic...)
# TODO define a help protocol:
# 		__doc__
# 		__attrhelp__
# 		__signaturehelp__
# 		...
#
class RPCSessionManager(object):
	'''
	this class provides the generic RPC session interface.
	'''
	# this will define the active session container object (defaults to dict). 
	__active_sessions__ = None
	# this will define the session object container (dict-like).
	__session_objects__ = None
	# this will define the proxy object that will be used to wrap the
	# session object...
	# this will take the session object as argument and return the
	# proxy.
	__session_proxy__ = None
	# if this is set password checking will be enabled...
	# NOTE: for this to function the session object must have a
	#       "checkpassword" method (see the Session class for details).
	__password_check__ = False
	# define the acl lib...
	__acl_lib__ = acl
	# enable acl for object access (this should be handled by the
	# object its self)....
	__path_acl_check__ = True
	# if set for an object the path form that object and down will not
	# be acl checked by the interface...
	##!!! test !!##
	__acl_check_cutoff__ = False
	# charactes allowed in a SID... 
	# NOTE: canging this in runtime will have no effect...
	__sid_chars__ = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ' \
					'abcdefghijklmnopqrstuvwxyz' \
					'0123456789' \
					'./_-&%@#'
	# this sets the legth of the sid...
	__sid_len__ = 27
	# Global method data:
	# NOTE: there are two interfaces currently supported, one of which
	#       might get depricated...
	# interface_I:
	# this defines the list of accesible global methods...
	__global_methods__ = (
##							'_test_I',
						 )
	# this defines the list of non=system methods available without a 
	# session...
	__public_methods__ = (
						 )
	# this defines system (special-case) methods...
	__system_methods__ = (
							'new_session',
							'close_session',
							'isalive',
						 )
	# interface_II:
	# global method naming convention:
	#      <__globalmethodprefix__> % <public_method_name>
	__globalmethodnameformat__ = 'GLOBAL_%s'

	# this sets the session global timeout (idle time before session
	# close), if None timeout checks will be disabled.
	__timeout__ = 1800.0

	def __init__(self):
		'''
		'''
		if self.__active_sessions__ == None:
			self.__active_sessions__ = {}
		if hasattr(self, '__sid_len__') and self.__sid_len__ < 8:
			print >> sys.stderr, "WARNING: it is recommended that the SID be longer than 8 chars."
	# System methods (external):
	def new_session(self, obj_id, password='', *p, **n):
		'''
		this will create a new session.
		'''
		sid_len = hasattr(self, '__sid_len__') and self.__sid_len__ or 32
		# make sure the sid is unique... (just in case... be pedantic! :) )
		while 1:
			# generate a unique sid...
			sid = self._new_sid(length=sid_len)
			if sid not in self.__active_sessions__:
				# select a session object...
				obj = self.__session_objects__.get(obj_id, None)
##				if obj_id not in self.__session_objects__:
				if obj == None:
					raise SessionError, 'no such object ("%s").' % obj_id
##				obj = self.__session_objects__[obj_id]
				# check password...
				if hasattr(self, '__password_check__') and self.__password_check__ and \
						hasattr(obj, 'checkpassword') and not obj.checkpassword(password):
					raise SessionError, 'no such object ("%s").' % obj_id
				# check uniqueness...
				if hasattr(obj, '__unique_session__') and obj.__unique_session__ and obj in self.__active_sessions__.values():
					raise SessionError, 'can\'t open two sessions for this object (%s).' % obj_id
				# proxy...
				if hasattr(self, '__session_proxy__') and self.__session_proxy__ != None:
					obj = self.__session_proxy__(obj)
				# add to list of active sessions...
				self.__active_sessions__[sid] = obj
				# set the time...
				if self.__timeout__ != None:
					obj._last_accessed = time.time()
				# fire _onSessionOpen event
				if hasattr(obj, '_onSessionOpen'):
					obj._onSessionOpen(self)
				break
		return sid
	def close_session(self, sid, *p, **n):
		'''
		this will close an existing session.
		'''
		if sid not in self.__active_sessions__:
			return
		# fire _onSessionClose event
		obj = self.__active_sessions__[sid]
		if hasattr(obj, '_onSessionClose'):
			obj._onSessionClose(self)
		del self.__active_sessions__[sid]
	def isalive(self, sid):
		'''
		this will test if a session exists.

		NOTE: this does not extend the life of the session object.
		'''
		if sid not in self.__active_sessions__ or \
				self.__timeout__ != None and \
				(time.time() - self.__active_sessions__[sid]._last_accessed) > self.__timeout__:
			self.close_session(sid)
			return False
		return True
	# System methods (internal):
	def dispatch(self, method, *pargs, **nargs):
		'''
		'''
		# system methods...
		if method in self.__system_methods__ + self.__public_methods__:
			return getattr(self, method)(*pargs, **nargs)
		# dispatch...
		else:
			# dispatch the call to a valid session object...
			if len(pargs) < 1:
				raise TypeError, 'argument list too short (must be 1 or more arguments; got %d).' % len(pargs)
			sid = str(pargs[0])
			# check session object age...
			if not self.isalive(sid):
				raise SessionError, 'no such session.'
			path = method.split('.')
			# get the session...
			session_obj = self.__active_sessions__[sid]
			# set access time...
			if self.__timeout__ != None:
				session_obj._last_accessed = time.time()
			# check if we are using a global method...
			if path[-1] in self.__global_methods__:
				# call the global method...
				return self._callglobal(sid, path[:-1], path[-1], *pargs[1:], **nargs)
			if hasattr(self, self.__globalmethodnameformat__ % path[-1]):
				# call the global method...
				return self._callglobal(sid, path[:-1], self.__globalmethodnameformat__ % path[-1], *pargs[1:], **nargs)
			# dispatch the call to the actual object...
			return self._getobject(sid, session_obj, path)(*pargs[1:], **nargs)
	# Utility Methods:
	def _callglobal(self, sid, path, meth, *p, **n):
		'''
		this will call the global method and handel security...
		'''
##		if hasattr(self, '__acl_lib__') and self.__acl_lib__ != None:
##			acl = self.__acl_lib__ 
##		else:
##			global acl
		obj = self._getobject(sid, self.__active_sessions__[sid], path)
		# check acl...
		if acl.isglobalmethodallowed(obj, meth):
			# call the method
			return getattr(self, meth)(sid, path, obj, *p, **n)
	##!!! recheck security !!!##
	def _getobject(self, sid, obj, path):
		'''
		get an object by its path (with ACL).
		'''
		if hasattr(self, '__acl_lib__') and self.__acl_lib__ != None:
			acl = self.__acl_lib__ 
##		else:
##			global acl
		if hasattr(self, '__path_acl_check__') and self.__path_acl_check__:
			acl_check_cutoff = False
			for obj_name in path:
				if not acl_check_cutoff:
					# check if this attr is accessible...
					obj = acl.getattr(obj, obj_name)
					if hasattr(obj, '__acl_check_cutoff__') and obj.__acl_check_cutoff__:
						acl_check_cutoff = True
				else:
					obj = getattr(obj, obj_name)
		else:
			for obj_name in path:
				obj = getattr(obj, obj_name)
		return obj
	def _new_sid(self, length=20, seed=1):
		'''
		will generate a unique session id...
		'''
		if seed == 0 or type(seed) not in (int, long, float):
			raise TypeError, 'the seed can not be: %s' % seed
		# define some data...
		res = ''
		# cache the vars...
		c = self.__sid_chars__
		lc = len(c) - 1
		rr = random.randrange
		# NOTE: this is quite brain-dead so will likely be rewritten...
		while len(res) < length:
			# generate the translation table...
			translation_table = ''.join([c[rr(0,lc)] for i in range(256)])
			# generate the key...
			res += str(sha.new(str(time.time()*seed)).digest()).translate(translation_table)
		# truncate the result to the desired length....
		return res[:length]
	def check_sessions(self):
		'''
		'''
		for session in self.__active_sessions__.keys():
			if not self.isalive(session):
				name = self.__active_sessions__[session].__name__
				##!! rewrite (with logger...) !!##
				print '[%s] session for "%s" terminated on timeout.' % (time.strftime('%Y%m%d%H%M%S'), name)
	# Global Methods:
	# these are generic clobal methods.
	# all global methods must be of the form:
	#     <method>(sid, path, obj, ...) -> res
	#     where:
	#         sid  : session id
	#         path : list of path nodes
	#         obj  : the actual target object.
	# NOTE: these are not intended for direct use...
	# the following two are for testing and illustration of the
	# interface usage...
##	def _test_I(self, sid, path, obj, *p, **n):
##		'''
##		this is here for testing only (interface I)...
##		'''
##		return str({'sid':sid, 'path':path, 'obj':obj, 'p':p, 'n':n})
##	def GLOBAL__test_II(self, sid, path, obj, *p, **n):
##		'''
##		this is here for testing only (interface II)...
##		'''
##		return str({'sid':sid, 'path':path, 'obj':obj, 'p':p, 'n':n})


#-----------------------------------------------BaseRPCSessionManager---
class BaseRPCSessionManager(RPCSessionManager):
	'''
	this class defines the basic object interface for RPCSessionManager.
	'''
	__active_sessions__ = None
	__session_objects__ = None

	# Global method data:
	# this defines the list of accesible global methods...
	__global_methods__ = RPCSessionManager.__global_methods__ + \
						 (
							'hasattr',
							'getattr', 
							'getattrs',
							'setattr',
							'setattrs',
							'get_methods',
							'get_doc',
						 )
	# this defines the list of non-system methods available without a 
	# session...
	__public_methods__ = RPCSessionManager.__public_methods__ + \
						 (
							'listMethods',
##							'methodSignature',
							'methodHelp',
							'new_session'
						 )

	# TODO make acl optional for these.... (ACL is the objects
	#      responsibility (not the interface...))
	# Global Methods:
	def hasattr(self, sid, path, obj, name):
		'''
		'''
		if hasattr(self, '__acl_lib__') and self.__acl_lib__ != None:
			acl = self.__acl_lib__ 
			return acl.hasattr(obj, name)
		else:
			return hasattr(obj, name)
	def getattr(self, sid, path, obj, name):
		'''
		'''
		if hasattr(self, '__acl_lib__') and self.__acl_lib__ != None:
			acl = self.__acl_lib__ 
			# form the result
			return acl.getattr(obj, name)
		else:
			# form the result
			return getattr(obj, name)
	def getattrs(self, sid, path, obj, *names):
		'''
		'''
		if hasattr(self, '__acl_lib__') and self.__acl_lib__ != None:
			acl = self.__acl_lib__ 
			_getattr = acl.getattr
		else:
			_getattr = getattr
##		# get the actual target...
##		obj = self._getobject(sid, self.__active_sessions__[sid], path)
		# form the result
		res = {}
		for name in names:
			# this will return only the allowed attributes...
			try:
				res[name] = _getattr(obj, name)
			except:
				pass
		return res
	def setattr(self, sid, path, obj, name, val):
		'''
		'''
		if hasattr(self, '__acl_lib__') and self.__acl_lib__ != None:
			acl = self.__acl_lib__ 
			return acl.setattr(obj, name, val)
		else:
			return setattr(obj, name, val)
	def setattrs(self, sid, path, obj, data):
		'''
		'''
		if hasattr(self, '__acl_lib__') and self.__acl_lib__ != None:
			acl = self.__acl_lib__ 
			_setattr = acl.setattr
		else:
			_setattr = setattr
		err = False
		for key in data:
			try:
				_setattr(obj, key, data[key])
			except:
				err = True
		if err:
			return False
	def delattr(self, sid, path):
		'''
		'''
		if hasattr(self, '__acl_lib__') and self.__acl_lib__ != None:
			acl = self.__acl_lib__ 
			# form the result
			return acl.delattr(obj, name)
		else:
			return delattr(obj, name)
	##!!! remove dep on __public_attrs__...   (???)
	def get_methods(self, sid, path, obj):
		'''
		'''
		if hasattr(self, '__acl_lib__') and self.__acl_lib__ != None:
			acl = self.__acl_lib__ 
##		else:
##			global acl
		# call the doc makic method if it exists...
		if hasattr(obj, '__method_doc__'):
			##!!!
			return obj.__method_doc__()
		res = {}
		# session/object specific methods...
		if hasattr(obj, '__public_attrs__'):
			lst = list(obj.__public_attrs__)
		else:
			lst = dir(obj)
		for attr in lst:
			try:
				o = acl.getattr(obj, attr)
			except AttributeError:
				continue
			else:
				if callable(o) and acl.isaccessible(o):
					if hasattr(o, '__doc__') and type(o.__doc__) is str:
						res[attr] = o.__doc__
					else:
						res[attr] = ''
		# do global methods (interface I)...
		if hasattr(self, '__global_methods__') or True:
			for meth in self.__global_methods__:
				o = getattr(self, meth)
				if hasattr(o, '__doc__') and type(o.__doc__) is str:
					res[meth] = o.__doc__
				else:
					res[meth] = ''
		# do global methods (interface II)...
		lst = dir(self)
		pattern = self.__globalmethodnameformat__.split('%s')
		for attr in lst:
			if attr.startswith(pattern[0]) and attr.endswith(pattern[-1]):
				o = getattr(self, attr)
				meth = '' not in pattern and attr.split(pattern[0])[-1].split(pattern[-1])[0] or \
						pattern[0] != '' and attr.split(pattern[0])[-1] or \
						pattern[-1] != '' and attr.split(pattern[-1])[0]
				# sanity check...
				if meth == '':
					continue
				if hasattr(o, '__doc__') and type(o.__doc__) is str:
					res[meth] = o.__doc__
				else:
					res[meth] = ''
		return res
	# NOTE: this may change in the future...
	# XXX this appears not to work only for StoreClient.type....
	def get_doc(self, sid, path, obj):
		'''
		this will print the objects __doc__ and the return 
		of the __help__ method if it exists...
		'''
		res = ''
		if hasattr(obj, '__doc__'):
			res = str(obj.__doc__) + '\n\n'
		if hasattr(obj, '__help__'):
			res += str(obj.__help__())
		if res == '':
			res = 'no documentation present for this object.'
		return res
	# Standard XMLRPC methods:
	# NOTE: these are only available outside of a session...
	def listMethods(self):
		'''
		This method returns a list of strings, one for each (non-system)
		method supported by the XML-RPC server
		'''
		return dict.fromkeys(self.__public_methods__ + self.__system_methods__).keys()
	def methodHelp(self, name):
		'''
		This method returns a documentation string for a method.
		'''
		if name in self.__public_methods__ + self.__system_methods__:
			return getattr(self, name).__doc__
	# this is not expected to get implemeted soon... 
##	def methodSignature(self, name):
##		'''
##		'''
##		if name in self.__public_methods__:
##			return	



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
