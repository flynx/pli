#=======================================================================

__version__ = '''0.0.03'''
__sub_version__ = '''20040514192432'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------
##!! TEST !!##
#------------------------------------------------------------ACLProxy---
# TODO add support for "kiserver" acl... (see: pli.misc.acl) (??)
# TODO add custom per-attribute source support 
#      ('source' : <obj-ref> | <accessor> | None)
# TODO make the error messages more meaningfull....
# TODO find a better name... (?)
class AccessTranslationProxy(object):
	'''
	this proxy handles ns (attr) translation (both static and dynamic) 
	from the accessor names/keys to the data source, in addition to a 
	basic r/w access control.
	'''
	# this will define the data source object...
	__data_source__ = None
	# if this is true all attributes accessed that aren't in the spec 
	# will raise an error...
	__strict_spec__ = True
	# this will define the attributes and their data courses (??)
	# accessible through this proxy. if set to None will provide full
	# access to the data source (will only use the ACL settings on the
	# source, otherwise will use both)....
	# format:
	# 	{ <public-name> : None |
	# 					  <name> | 
	# 					  { [ 'reader' : <reader> | <name> | None ], 
	# 					    [ 'writer' : <writer> | <name> | None ] } 
	# 	  [, ...] }
	# element value:
	# 	None		-- direct mapping.
	# 	<name>		-- use <name> to access attribute in data source.
	# 	<reader>	-- callable that will return the value.
	# 	<writer>	-- callable that will write the value ( <writer>(data) ).
	__attr_spec__ = None


	# HL (smart) ACL accessors...
	def __getattr__(self, name):
		'''
		'''
		r_name = name
		if hasattr(self, '__attr_spec__') and self.__attr_spec__ != None:
			attr_spec = self.__attr_spec__
			if name not in attr_spec:
				if hasattr(self, '__strict_spec__') and self.__strict_spec__:
					# attr not in spec...
					raise NameError, 'object %s has no attribute "%s"' % (self, name)
			else:
				# check self.__attr_spec__ ....
				spec = attr_spec[name]
				if type(spec) in (str, unicode):
					r_name = spec
				elif type(spec) is dict:
					if 'reader' in spec:
						spec = spec['reader']
						if spec == None:
							# attr is not readable...
							raise NameError, 'object %s has no attribute "%s"' % (self, name)
						elif type(spec) in (str, unicode):
							r_name = spec
						else:
							##!!! should we pass an arg here???
							return spec(r_name)
					##!!! is this affected by __strict_spec__??
					else:
						raise NameError, 'object %s has no attribute "%s"' % (self, name)
		return self.__datareader__(r_name)
	def __setattr__(self, name, val):
		'''
		'''
		r_name = name
		if hasattr(self, '__attr_spec__') and self.__attr_spec__ != None:
			attr_spec = self.__attr_spec__
			if name not in attr_spec:
				if hasattr(self, '__strict_spec__') and self.__strict_spec__:
					# attr not in spec...
					raise NameError, 'attribute "%s" of object %s is not writable.' % (name, self)
			else:
				# check self.__attr_spec__ ....
				spec = attr_spec[name]
				if type(spec) in (str, unicode):
					r_name = spec
				elif type(spec) is dict:
					if 'writer' in spec:
						spec = spec['writer']
						if spec == None:
							# attr is not writable...
							raise NameError, 'attribute "%s" of object %s is not writable.' % (name, self)
						elif type(spec) in (str, unicode):
							r_name = spec
						else:
							##!!! should we pass an arg here???
							return spec(r_name, val)
					##!!! is this affected by __strict_spec__??
					else:
						raise NameError, 'attribute "%s" of object %s is not writable.' % (name, self)
		return self.__datawriter__(r_name, val)
	# LL direct (dumb) data accessors....
	# this is the place to put any far-side (post) acl checks...
	# NOTE: these depend on the data access protocol (default:
	#       attribute access).
	def __datareader__(self, name):
		'''
		'''
		return getattr(self.__data_source__, name)
	def __datawriter__(self, name, val):
		'''
		'''
		return setattr(self.__data_source__, name, val)



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
