#=======================================================================
#-----------------------------------------------------------------------

__version__ = '''0.0.00'''
__sub_version__ = '''20031106031445'''
__copyright__ = '''(c) Alex A. Naanou 2003'''



#-----------------------------------------------------------------------
__doc__ = '''
'''

#-----------------------------------------------------------------------
# System Concepts:
#	Stream
#		a recursive data format (container) that supports the stream 
#		read and write interfaces/protocols.
#	StreamWriter
#		Stream -> Data
#		an entity that reads data from a stream and writes it out.
#	StreamReader
#		Data -> Stream
#		an entity that read data and writes it to a stream. 
#
#
# Basic Operation:
#
#			StreamReader
#		  ---------------->
#	Data					Stream
#		  <----------------
#			 StreamWriter
#
#
#
#		  -------------------- Serialize ------------------->
#
#				 StreamReader			   StreamWriter
#			   ---------------->		 ---------------->
#	PythonData					 Stream						 Data
#			   <----------------		 <----------------
#				  StreamWriter				StreamReader
#
#		  <------------------ Deserialize -------------------
#
#
# Data Format:
# 	all data is a stream.
#
# 	any stream can either be mutable or immutable (defined in
# 	constructor), this is only used for read write operations as on the 
# 	inside, a stream may be all mutable (for optimization.)
#
# 	a stream is not editable!.
#
#	a chained stream can be a receiver, a transmitter or a channeler
#	(receive and transmit).
#
# 	Stream Data Processors:
# 		ReferenceStream: (???)
# 			this is a reference to another stream in the registry.
#
# 		NumberStream:
# 			this is a stream that can contain one or more basic values.
# 			corresponds to pythons:
# 				int
# 				float
# 				complex
#
# 		StringStream:
# 			this is a stream that can contain one or more basic values.
# 			corresponds to pythons:
# 				string
# 				unicode
# 				code
#
# 		SequenceStream:
# 			this can contain zero or more streams (e.g. "stream of streams").
# 			corresponds to pythons:
# 				tuple
# 				list
#
# 		MappingStream:
# 			this contains zero or more pairs of the form:
# 				<ElementStream> : <any>
# 			corresponds to pythons:
# 				dict
#
# 		ObjectStream:
# 			this is a Stream with additional stores/attributes (e.g. all data
# 			is stored in named streams)
# 			essential attributes:
# 				type
# 				module
# 				namespace
# 				...
# 			optional attributes:
# 				name
# 				...
# 			corresponds to pythons:
# 				type
# 				classobj
# 				object
# 				class
# 				instance
# 				function
#
# 		FunctionStream:
#
# Usage Patterns:
# 	Stream chaining
# 		StreamReader -> StreamWriter
# 		StreamReader -> GenericStream
# 		GenericStream -> StreamWriter
#
#
# Stream Interface:
# 	open			-- will open a sub-stream.
# 	close			-- will close a sub-stream.
# 	insert			-- will insert an element into the current stream.
# 	set				-- will set a stream attribute (__setattr__).
# 	
#
#

#=======================================================================

import stream


#---------------------------------------------------------StreamError---
class StreamError(Exception):
	'''
	'''
	pass



#-----------------------------------------------------------------------
#------------------------------------------------------StreamRegistry---
class StreamRegistry(object):
	'''
	this will keep track of objects in a stream.
	'''
	pass


#--------------------------------------------------------------Stream---
# TODO add support for stream object registry... (???)
class Stream(stream.Stream):
	'''
	this is an abstract stream object.
	'''
	##!! revise the dispatcher interface in the following !!##
	# Stream Magic Methods...
	# NOTE: in the folowing methods the dispatch attribute must resolve
	#       to the stream managers dispatcher object...
	#       this will permit nested stream managers (e.g. serialize all
	#       objects using the Pickle format but the objects of type X
	#       which are to be serialized into XML, or use diferent xml
	#       formats for diferent object types... etc.)
	#       NOTE: for the above to work properlyit may be good to pass 
	#             the "reference" to the serialized object or file
	#             upwards to the conatining stream...
	def __open__(self, parent_stream, *pargs, **nargs):
		'''
		this method is called opun stream open.
		'''
		# call the dispatch...
##		self.dispatch('open', type(self), parent_stream, *pargs, **nargs)
		self.dispatch.open(type(self), parent_stream, *pargs, **nargs)
	def __close__(self):
		'''
		this method is called on stream close.
		'''
		# call the dispatch...
##		self.dispatch('close', type(self))
		self.dispatch.close(type(self))
	def __insert__(self, *pargs, **nargs):
		'''
		this method is called on object insert.
		'''
		# call the dispatch...
##		self.dispatch('insert', type(self), *pargs, **nargs)
		self.dispatch.insert(type(self), *pargs, **nargs)



#-----------------------------------------------------------------------
# these objects must call the *contexts* interface functions...
#--------------------------------------------------------NumberStream---
class NumberStream(Stream):
	'''
	'''


#--------------------------------------------------------StringStream---
class StringStream(Stream):
	'''
	'''


#------------------------------------------------------SequenceStream---
class SequenceStream(Stream):
	'''
	'''


#-------------------------------------------------------MappingStream---
class MappingStream(Stream):
	'''
	'''


#--------------------------------------------------------ObjectStream---
class ObjectStream(Stream):
	'''
	'''


#-----------------------------------------------------ReferenceStream---
# this should hold information on the location of the stream, its type
# and data needed for the stream to be properely processed...
# modes:
# 	1. create a reference inside the current stream (needs: target id
# 	   (from stream registry)).
# 	2. create a stream object using an "external" stream processor
# 	   (needs: ...).
#
##!! revise !!##
class ReferenceStream(Stream):
	'''
	this is a spetial object to be used as a link to a diferent stream object.
	'''



#=======================================================================
#---------------------------------------------StreamProcessorDispatch---
# Search Order:
# 	1. specific type processor in/for meta-stream
# 	2. meta-stream processor
# 	3. Err: unsupported object type.
#
class StreamProcessorDispatch(object):
	'''
	'''
	def __init__(self):
		'''
		'''
		pass
	# dispatch interface methods...
	def register_processor(self, stream_type, obj):
		'''
		'''
	# stream interface methods...
	def open(self, stream_type, stream_length=None, stream_id=None, *pargs, **nargs):
		'''
		'''
		pass
	def close(self, stream_type):
		'''
		'''
		pass
	def insert(self, stream_type, *pargs, **nargs):
		'''
		'''
		pass
	# default processors...
	##!!!



#-----------------------------------------------------------------------
#--------------------------------------------------DataToStreamReader---
class DataToStreamReader(object):
	'''
	this is a generic stream constructor class (data -> stream).
	'''
	def __call__(self, *pargs, **nargs):
		'''
		this will initiate the read process and start writing to the target stream.

		'''
		if not hasattr(self, 'target_stream'): 
			raise StreamError, 'stream reader not chained to a reciving stream.'
	def chain(self, stream):
		'''
		'''
		self.target_stream = stream
	def unchain(self):
		'''
		'''
		del self.target_stream


#--------------------------------------------------StreamToDataWriter---
class StreamToDataWriter(ReferenceStream):
	'''
	this is a generic stream writer class (stream -> data).
	'''

	# this is the generic stream processor...
	dispatch = StreamProcessorDispatch()

	def __init__(self):
		'''
		'''
		# TODO generate a better stream_id
		super(StreamWriter, self).__init__(self, parent=None, sream_id=id(self))



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
