import os

from glob import glob

from wimp.book import Book

class BookShelf(object):
    def __init__(self, bookroot, working_dir, books=None):
        self.bookroot = bookroot
        self.working_dir = working_dir
        if books is None:
            self.books = self._get_all_books()
        else:
            self.books = {}

    def all_books(self):
        return sorted(self.books.keys())

    def get_book(self, bookid):
        return self.books[bookid]

    def delivery(self, bookid):
        return self.books(bookid).delivery

    @property
    def bookids(self):
        return [self.books[book].bookid for book in self.books]

    def _get_all_books(self):
        while True:
            try:
                return self._all_books # pylint: disable = E1101
            except AttributeError:
                setattr(
                    self, '_all_books',
                    {
                        os.path.basename(bookid): Book(bookid, self.working_dir)
                        for bookid
                        in glob('%s/[BD]*/hin-*' % self.bookroot)
                    }
                )
