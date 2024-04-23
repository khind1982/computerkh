import MySQLdb

from time import sleep
import sys

class dbconnector:

    def __init__(self, upd=None, **kwargs):
        self.connection = None
        self.kwargs = kwargs
        if upd is not None:
            self.kwargs['user'] = upd
            self.kwargs['passwd'] = upd
            self.kwargs['db'] = upd
            
        #Set some default values in case they have not been passed as keyword arguments
        defaults = {"host":"localhost", "use_unicode": True, "charset":"latin1"}
        
        for item in defaults.keys():
            if not self.kwargs.has_key(item):
                self.kwargs[item] = defaults[item]
        
    def MakeConnection(self, limit=30):
        """Connect to the MySQL database. Try three times."""
        
        if self.connection is not None:
            return self.connection

        for attempt in range(1,limit):
            try:
                return MySQLdb.connect(**self.kwargs)
            except:
                
                print 'Attempt number ' + str(attempt)
                print 'Problem connecting to the database.' 
                (code, message) = sys.exc_value 
                print "Error code:" , code
                print "Error message:", message
                print 'Will sleep for 60 seconds and then try again.'
                sleep(60)
                continue