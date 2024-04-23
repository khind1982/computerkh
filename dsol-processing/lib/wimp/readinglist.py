class ReadingList(object):
    def __init__(self, bookids=None, bookshelf=None, progressmonitor=None):
        self.bookshelf = bookshelf
        self.progressmonitor = progressmonitor
        self.bookids = self._get_list(bookids)

    def finished_book(self, bookid):
        self.progressmonitor.update_with_bookid(bookid)
        self.update_list()

    def next_on_list(self):
        return self.bookids[0]

    def book(self, bookid):
        if bookid in self.bookids and bookid in self.bookshelf.bookids:
            return self.bookshelf.get_book(bookid)

    def update_list(self, bookids=None):
        return self._get_list(bookids)

    def _get_list(self, bookids=None):
        if bookids is None:
            bookids = self.bookshelf.all_books()
            sort = True
        else:
            sort = False
        return self._maybe_sorted([
            x for x in bookids
            if not x in self.progressmonitor.get_progress()
        ], sort)

    @staticmethod
    def _maybe_sorted(iterable, sort=True):
        if sort is True:
            return sorted(iterable)
        else:
            return iterable

    def __iter__(self):
        return iter(self.bookids)

    def __contains__(self, item):
        return True if item in self.bookids else False
