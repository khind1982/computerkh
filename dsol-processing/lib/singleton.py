#!/usr/local/bin/python2.6
# -*- mode: python -*-

#import sys, os
#syspath.append(os.path.join(os.path.dirname(__file__) + '/../lib/python'))

# An implementation of the Singleton design pattern. It ensures that only
# one instance of the class is ever created. Useful as a configuration 
# manager in a larger application, to hold a reference to a logger interface,
# etc. Any class of which there should only ever be a single living instance
# is probably a good candidate for being implemented as a singleton. This
# implementation is from http://code.activestate.com/recipes/52558/

class Singleton(object):
    """ A python singleton """

    class __impl:
        """ Implementation of the singleton interface """

        def spam(self):
            """ Test method, return singleton id """
            return id(self)

    # storage for the instance reference
    __instance = None

    def __init__(self):
        """ Create singleton instance """
        # Check whether we already have an instance
        if Singleton.__instance is None:
            # Create and remember instance
            Singleton.__instance = Singleton.__impl()

        # Store instance reference as the only member in the handle
        self.__dict__['_Singleton__instance'] = Singleton.__instance

    def __getattr__(self, attr):
        """ Delegate access to implementation """
        return getattr(self.__instance, attr)

    def __setattr__(self, attr, value):
        """ Delegate access to implementation """
        return setattr(self.__instance, attr, value)




# class Singleton(object):
#     __single = None # the one, true Singleton

#     def __new__(classtype, *args, **kwargs):
#         # Check to see if a __single exists already for this class
#         # Compare class types instead of just looking for None so
#         # that subclasses will create their own __single objects
#         if classtype != type(classtype.__single):
#             classtype.__single = object.__new__(classtype, *args, **kwargs)
#         return classtype.__single

#     def __init__(self,name=None):
#         self.name = name

#     def display(self):
#         print self.name,id(self),type(self)
