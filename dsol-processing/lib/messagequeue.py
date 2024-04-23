# -*- mode: python -*-

from commonUtils.listUtils import uniq_sort
from decorators import singleton

# A dict that can be used to store log messages for the operator.
# Useful for recording errors that cause documents to be omitted
# from the output, but which shouldn't be considered serious enough
# to halt execution.

@singleton
class MessageQueue(object):
    def __init__(self):
        self.messages = {}

    def __len__(self):
        return len(self.messages)

    def add_message(self, msg_name, message, priority="Normal"):
        # Add a new message to the queue.
        # This can then have a list of IDs
        # associated with it.
        # e.g. msg_name = parsefailed, message = "Record failed to parse"
        # Then associate record IDs:
        # msgq.parsefailed.append('123456')
        self.messages[msg_name] = Message(msg_name, message, priority)
        return self.messages[msg_name]

    def append_to_message(self, msg_name, message):
        while True:
            try:
                self.messages[msg_name].append(message)
                return
            except KeyError:
                self.messages[msg_name] = Message(msg_name) # message)

    def print_messages(self, banner=None):
        if len(self) == 0:
            return
        if banner is not None:
            print banner
        for message in self.messages.keys():
            self.messages[message].print_message()
            #print self.messages[message]


class Message(object):
    def __init__(self, msg_name, priority="Normal"):
        self.msg_name = msg_name
        #self.message = message
        self.priority = priority
        # A list to hold any variable data, such as record IDs,
        # file location, etc, as may be required by the semantics
        # of the message.
        self.var_data = []

    def append(self, data):
        self.var_data.append(data)

    def print_message(self):
        print self.msg_name
        for item in uniq_sort(self.var_data):
            print '\t%s' % item

    def __str__(self):
        #return "%s: %s, %s" % (self.msg_name, self.message, [item for item in self.var_data])
        return "%s: %s" % (self.msg_name, [item for item in self.var_data])
