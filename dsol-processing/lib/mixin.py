#!/usr/local/bin/python2.6
# -*- mode: python -*-

import sys, os, types
sys.path.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

# Implements mixins for Python. Useful when you don't want the horrors of 
# multiple inheritance, or you want to share functionality between classes
# and maintain an OO approach.

# http://www.linuxjournal.com/node/4540/print, listing 4.
def mixin(pyClass, mixInClass, makeAncestor=0):
    if makeAncestor:
        if mixInClass not in pyClass.__bases__:
            pyClass.__bases__ = (mixInClass,) + pyClass.__bases__
    else:
        # Recursively traverse the mix-in ancestor
        # classes in order to support inheritance
        baseClasses = list(mixInClass.__bases__)
        baseClasses.reverse()
        for baseClass in baseClasses:
            mixin(pyClass, baseClass)
        # Install the mix-in methods into the class
        for name in dir(mixInClass):
            if not name.startswith('__'):
                # skip private members
                member = getattr(mixInClass, name)
                if type(member) is types.MethodType:
                    member = member.im_func
                # Attach the function to the class object as a method.
                # This means we can call mixin functions just like any
                # other method - the interpreter correctly passes an
                # implicit instance as the first argument. No need any
                # more to explicitly pass an instance (in fact, doing so
                # will raise an exception)
                setattr(pyClass, name, types.MethodType(member, pyClass))


# Not sure of the utility of these two functions, so keeping them
# around in case I ever feel like trying to figure out how they can be
# used...

# def unmix(cla):

#     """Undoes the effect of a mixin on a class. Removes all attributes that
#     were mixed in -- so even if they have been redefined, they will be
#     removed.
#     """
#     for m in cla._mixed_: #_mixed_ must exist, or there was no mixin
#         delattr(cla, m)
#     del cla._mixed_



# def mixedin(base, module):

#     """Same as mixIn, but returns a new class instead of modifying
#     the base.
#     """
#     class newClass: pass
#     newClass.__dict__ = base.__dict__.copy()
#     mixIn (newClass, module)
#     return newClass
