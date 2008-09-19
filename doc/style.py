#=======================================================================

__version__ = '''0.1.00'''
__sub_version__ = '''20070717183115'''
__copyright__ = '''(c) Alex A. Naanou 2003-2007'''


#-----------------------------------------------------------------------
__doc__ = '''
this module is to document the recommended coding style in this project.

NOTE: this is partly derived from python style PEP8 <http://python.org/peps/pep-0008.html>
      thus this is to be considered as a more specific extension to the PEP.
NOTE: in cases not defined by this text fall back to the PEP8.
NOTE: the rest of this module illustrates the styling and can be used as 
      an example.


General format:
    - code should if possible be no more than 72 chars wide.
    - all comments must be no more than 71 chars wide and if possible justified,
      unless positional commenting of very long lines of code.
    - all section separators must be exactly 72 chras wide.


Commenting culture:
    - keep your comments current. the aim of comments is to help the
      user, not to confuse him (never make anyone debug your comments
      when what is needed is to understand your code!).
    - keep your comments short. write just what is relevant and do not
      make anyone search for what you are trying to say.
    - be relevant. comment on the code/task at hand and not something
      that is not in the direct vicinity, module or universe.
    - be descriptive. describe what you are doing but only if it
      will take more time to get it form the code than form your 
      comment (by the average user and not by you!).
      making the user read the same code twice in two languages is not 
      vary polite.
    - warn and instruct if needed. it is a good idea to write out all
      the issues that are relevant to a particular piece of code.
      if you have a known bug ALWAYS write it out, with all the info
      and references to the affected and if known the affecting code.


Commenting style:
    - comments must always precede the commented code, and not follow it.
    - there should be no blank lines separating the comment and the commented code.
    - use a '#' for general commenting of code.
    - use '##' for temporary and commented-out code.
    - use '# TODO ' to indicate normal priority todo tasks/reminders.
    - High Priority Commenting (HP):
        - use '##!!!' for general todo markers (may not be followed by text).
        - use '##!!' as a start of HP remarks and notes 
          (may be used inside comments).
        - use '##!! REWRITE !!##' style markers to indicate ASAP tasks/notes.
          use the case of the message to indicate importance.
          Ex:
            ##!! REWRITE !!##
            ##!! TEST !!##
            ##!! OPTIMIZE !!##
            ##!! revise !!##
            ...
    - it is recommended to avoid comments on the same line as the code.
      Ex:
          foo = 1+2 # assign to foo.
    - all comments must be no more than 71 chars wide and if possible justified,
      unless positional commenting of very long lines of code.


Sections (outlining):
    - each module may be composed of different levels of sections.
    - a section in general may contain only one element (e.g. class, function ... etc.)
    - if necessary separate parts of very long class definitions into 
      sub sections using blank lines.
    - group all related sections into one module or section if possible.
    - blank lines and sections:
        - each main section should end with exactly 3 blank lines.
        - each sub section should end with two blank lines.
        - the code must follow section separator directly on the next
          line with the exception of the declarative sections (e.g. imports,
          constants, data, ...etc) which should be headed by a blank line.
        - all definition sections (e.g. classes,  functions, ...etc)
          should have no blanks between the code and the section header.
        - if any comments, remarks or warnings need to be present for a
          section, they should directly follow the section separator and precede
          the section code.
    - module sections:
        - the first section in a file is the version and copyright info.
          this is obligatory, unless the module contains temporary, demo
          or test code.
        - the second section is the documentation section (this must
          exist in every release module).
        - the third section is the imports (optional).
        - the optional data section.
          NOTE: a data section should stat with a blank line.
        - then the module contents section.
        - optional test (if __name__ == '__main__') section.
        - the last section in the module should define editor related
          configuration (e.g. vim modlines ... etc.)
    - the section header should contain the name of the element defined within
      Ex:
        #---------------------------------------------------------ElementName---
        or
        #=======================================================================
        #-----------------------------------------------------------ClassName---
    - Section Separators:
        - Main sections:
            #-----------------------------------------------------------------------
            #---------------------------------------------------------ElementName---
            
            #-----------------------------------------------------------------------
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - -ElementName- -

            #=======================================================================

        - Sub sections:
            #---------------------------------------------------------ElementName---
            
            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - -ElementName- -

        - sction separators:
            #-----------------------------------------------------------------------

            #- - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - - -

            #.......................................................................

            #. . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . .


Element Naming Style:
    this is a general naming style used, note that some code dependent rules may be applied.

    Naming by Function/Pattern:
        it is recommended that all elements that represent a given pattern
        contain the pattern name in its name
        Ex:
            class MySuperClassFramework(object):
                ...
            or
            class MethodProxy(moo):
                ...
    
    classes:
        - utility
            a utility class is an element that is used as a function (factory) in the code.
            these may be all lowercase (like classmethod or staticmethod).
        - base/structure
            these are named as follows: first capital and every new word starts capital.
            (Ex: MyClassName)
    
    public/user methods and functions:
        all lowercase without word separators, preferably no longer than 8 chars.
        if the name must be longer or is not intended to be used very often then it 
        is acceptable to use underscores as separators.
        avoid long public names for often used methods/functions at all cost!
        (fall back to PEP8 when writing libs..)

    variables:
        all lowercase names with underscore as word separator.
        - global constants
            all capital with '_' as word separator (Ex: MY_GLOBAL_CONST_VAR)
        - private (method)
            use a leading underscore '_'
        - private (class)
            use a leading underscore '_' (avoid '__' if possible due to problems with inheritance)
        - private (instance)
            use a leading underscore '_' (avoid '__' if possible due to problems with inheritance)


General Coding Style:


Doc Strings:


Packages:


Modules:


Classes:


Methods:




Library code specifics:




Release Process:


Testing:



'''

#-----------------------------------------------------------------------
# NOTE: the ordering of the sections shown here is not strict, though it
#       is recommended to follow these guidelines:
#           - data section, first private then public.
#           - functions, again first private then public.
#           - classes, as before private and then public.
#
#       a general exception is semantically organized code. then each
#       separate section should follow the above guidelines.
#
#       but if such sections exist in a module, it is a good idea to
#       ask yourself a question if it would be more logical to split
#       this module into several self-contained modules or a package.
#
#       P.S. it is not a good idea to keep data/state as a module
#       variable. constants are OK but avoid storing state in the
#       library modules.
#-----------------------------------------------------------------------

# some constants defined...
CONSTAT_a = 'a'
CONSTAT_B = 'B'



#-----------------------------------------------------------------------
#-------------------------------------------_module_internal_function---
def _module_internal_function(args):
    '''
    '''
    pass



#-----------------------------------------------------------------------
#-----------------------------------------------------public_function---
def public_function():
    '''
    '''
    pass


#--------------------------------------------------------------dowork---
def dowork():
    '''
    '''
    pass



#-----------------------------------------------------------------------
#-------------------------------------------------------------MyClass---
# here is an example of a class definition...
class MyClass(object):
    '''
    my simple example class.
    '''
    # class private data...
    # some private state used here...
    _private_state = None

    # class public data...
    # NOTE: all class level data should be documented, and avoid
    #       comments that simply read the next line...
    #       ...try to always use meaningful names.
    # this is something that this class will sometime use...
    public_something = None

    # private methods...
    def _privatemethod(self):
        '''
        this method is intended for internal use or possibly for use 
        by library extensions.
        '''
        pass
    def _another_nonpublic_method(self):
        '''
        here is another acceptable non-public method name.
        '''
        pass

    # public methods...
    def publicmethod(self, arg1, arg2):
        '''
        and here is a good public method.
        '''
        pass


#--------------------------------------------------------MyOtherClass---
class MyOtherClass(MyClass):
    '''
    '''
    # MyClass interface extensions...
    def publicmethod(self, arg1, arg2):
        '''
        '''
        pass

    # specific methods...
    def yetanothermethods(self):
        '''
        this name is not so good...
        '''
        pass
    def another_method():
        '''
        this is a better name version for the above, unless this methods 
        is to be used often, then think of something 8-12 chars long.
        '''
        pass



#-----------------------------------------------------------------------
if __name__ == '__main__':
    print __doc__



#=======================================================================
#                                  vim:set ts=4 sw=4 nowrap expandtab :
