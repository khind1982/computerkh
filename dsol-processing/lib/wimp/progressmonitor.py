import datetime
import os

class ProgressMonitor(object):
    def __init__(self, logdir, bookshelf):
        self.logdir = logdir
        self.bookshelf = bookshelf

    def get_progress(self):
        return os.listdir(self.logdir)

    # We need to keep self.progress to preserve the API after changing
    # from using a single log file to record all PQIDs to using a single
    # file per PQID.
    @property
    def progress(self):
        return self.get_progress()

    def update_with_bookid(self, bookid):
        with open(os.path.join(self.logdir, bookid), 'w') as log:
            log.write("%s\n" % str(datetime.datetime.now()))
            b_numbers = [
                man.b_number for man
                in self.bookshelf.get_book(bookid).manifestations
                if not man.covers
            ]
            for b_number in b_numbers:
                log.write("%s\n" % b_number)
            