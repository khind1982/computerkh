# -*- mode: python -*-

# Abstract out the creation of the audit files. A step towards trying
# to make the transformaion app seem a little more designed, and a little
# less evolved...

class DeliveryAudit(object):
    def __init__(self, cfg):
        # If this is a resumed session, set the flag to 'a' to append to
        # what was already written in the first attempt. Otherwise, set
        # it to 'w' to start a new file.
        if cfg['resumePreviousRun']:
            flag = 'a'
        else:
            flag = 'w'
            
        # If cfg['auditlog'] is None, no audit log was requested by the
        # user, so we can simply set the logger to write to /dev/null
        if cfg['auditlog'] is None:
            filename = '/dev/null'
        else:
            filename = cfg['auditlog']
        self.audit_file = open(filename, flag)


    def write(self, string):
        self.audit_file.write(string)

    def close(self):
        self.audit_file.close()
