#=======================================================================

__version__ = '''0.0.01'''
__sub_version__ = '''20040214022015'''
__copyright__ = '''(c) Alex A. Naanou 2003'''


#-----------------------------------------------------------------------

import re

import pli.functional as func


#-----------------------------------------------------------------------
#--------------------------------------------------------------string---
def string(obj):
	'''
	return true if the object is either str or unicode.
	'''
	return type(obj) in (str, unicode)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
r_string = func.raise_on_false(string, TypeError, 'r_string', 'object is nither str or unicode.')


#-------------------------------------------------------------isemail---
EMAIL = '^\s*[-_a-z0-9.]+@[-_a-z0-9.]+\.\w+\s*$'
_email_pattern = re.compile(EMAIL, re.I)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def isemail(obj):
	'''
	return true if the obj is compatible with the email format spec (see EMAIL).
	'''
	return _email_pattern.match(obj) != None

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
r_isemail = func.raise_on_false(isemail, TypeError, 'r_isemail', 'object does not match email pattern.')


#--------------------------------------------------------------isdate---
DATE_FORMAT = '%Y/%m/%d'
DATE = '[0-9]{4}/[10]?[0-9]/[0-3]?[0-9]'
_date_pattern = re.compile(DATE)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def isdate(obj):
	'''
	return true if the obj is compatible with the date format spec (see DATE_FORMAT and DATE for more details).
	'''
	return _date_pattern.match(obj) != None

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
r_isdate = func.raise_on_false(isdate, TypeError, 'r_isdate', 'object does not match date pattern.')


#-------------------------------------------------------------isphone---
PHONE = '^\s*(?:[87][- ]?[- \(]?[0-9]{3}[- \)]?[- ]?)?[0-9]{3}[- ]?[0-9]{2}[- ]?[0-9]{2}\s*$'
_phone_pattren = re.compile(PHONE)

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
def isphone(obj):
	'''
	return true if the obj is compatible with the phone format spec (see PHONE).
	'''
	return _phone_pattren.match(obj) != None

#- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -
r_isphone = func.raise_on_false(isphone, TypeError, 'r_isphone', 'object does not match phone pattern.')




#=======================================================================
#                                            vim:set ts=4 sw=4 nowrap :
