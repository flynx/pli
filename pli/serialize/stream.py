#=======================================================================

__version__ = '''0.0.02'''
__sub_version__ = '''20031109230144'''
__copyright__ = '''(c) Alex A. Naanou 2003'''



#-----------------------------------------------------------------------
__doc__ = '''

A Stream is an interface, designed to iterativly transfer nested data 
from a stram writer (active) to a stream reader (passive).

this interface supports insertion of streams of different types.
'''

#-----------------------------------------------------------------------
#	open
#		-> inc counter
#		-> push stream
#		-> call __open__
#	close
#		-> call __close__
#		-> close all not open	##!!!
#	insert
#		-> inc counter
#		-> call __insert__
#		-> close all not open	##!!!
#
#
#
#											| fill
#						|					+-------
#	s = S(None, 2)		o __init__()		| 0
#	             		|					|
#	s.insert()			o insert()			| 1
#						|					|
#						o test			-+	|
#						|				 |	|
#						|				-+	|
#	s.open(S, 1)		o---+ open()		| 2 0
#						|	|				|
#	s.insert()			|	o insert()		| 2 1
#						|	|				|
#						|	o test		-+	|
#						|	|			 |	|
#						|	o close()	 |	|
#						|	|			 |	|
#						|<--+			 |	|
#						|				 |	|
#						o close()		 |	|
#						|				-+	|
#											|
#
#
#--------------------------------------------------------------Stream---
class Stream(object):
	'''
	this is an abstract/generic stream class.
	'''
	def __init__(self, parent, stream_length=None, stream_id=None):
		'''
		this will open self for writing.
		'''
		self._stream_parent = parent
		self._stream_id = stream_id
		self._stream_open = True
		self._stream_length = stream_length
		self._stream_fill = 0
		self._stream_stack = [self]
		# Q: should we call self.__open__ here???
		##!!!
	# utility methods...
	def _stream_update_stack(self):
		'''
		close all nested streams that need to be closed...

		NOTE: this may close the root streaam if needed...
		'''
		stack = self._stream_stack
		cur = stack[-1]

##		while cur._stream_fill == cur._stream_length:
##			# close self...
##			if cur._stream_open:
##				cur.close()
##				cur = stack[-1]
##			else:
##				break
		# remove all closed streams...
		while not cur._stream_open:
			if len(stack) == 1:
				##!! CHECK !!##
				break
##				raise TypeError, '???'
			# auto close...
			del stack[-1]
			cur = stack[-1]
	# interface methods...
	def open(self, stream_type, stream_length=None, stream_id=None, *pargs, **nargs):
		'''
		this will open a new nested stream.
		'''
		stack = self._stream_stack
		# create a stream object... 
		obj = stream_type(self, stream_length, stream_id)
		# add the object to the parents straem stack...
		obj._stream_fill += 1
		stack += [obj]
		return obj.__open__(self, *pargs, **nargs)
	def close(self):
		'''
		this will close the first unclosed stream stream.
		'''
		stack = self._stream_stack
		# sanity check...
##		if len(stack) == 0:
##			raise TypeError, 'stream stack is empty. (this is a bug)'
		# start our work...
		cur = stack[-1]
		if cur != self:
			# close a nested stream...
			cur.close()
			del stack[-1]
			return
		# sanity check (self close condition)...
		if len(stack) > 1:
			raise TypeError, 'stream stack is not empty, can\'t close.'
		# close self...
##		if self._stream_open == False:
##			raise TypeError, 'stream already closed.'
		self._stream_open = False
		self.__close__()
	# Q: does this need to have the same interface as the open method?
##	def insert(self, stream_type, stream_length=None, stream_id=None, *pargs, **nargs):
	def insert(self, *pargs, **nargs):
		'''
		this will insert a new object into the stream.
		'''
		# sanity check...
		if len(self._stream_stack) == 1 and not self._stream_open:
			raise TypeError, 'can\'t write to a closed stream.'
		cur = self._stream_stack[-1]
		if cur != self:
			# insert an obj into a nested stream...
			return cur.insert(*pargs, **nargs)
		# insert obj into self...
		res = self.__insert__(*pargs, **nargs)
		self._stream_fill += 1
		return res
	def __getattr__(self, name):
		'''
		deligate the attribute requests to the parent...
		'''
		return getattr(self._stream_parent, name)
	# Stream Magic Methods...
	def __open__(self, parent_stream, *pargs, **nargs):
		'''
		this method is called opun stream open.
		'''
	def __close__(self):
		'''
		this method is called on stream close.
		'''
	def __insert__(self, *pargs, **nargs):
		'''
		this method is called on object/streamm insert.
		'''



#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
