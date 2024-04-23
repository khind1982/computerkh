#
# Abstraction to make handling gen records a little less clunky.

# Provides dict-style access (self.gen['773']), as well as offering
# more convenient method-based access (self.gen.f_773()). This new
# approach also allows retrieval of just a single named subfield:
# self.gen.f_773('t')

# All this is done using two of Python's "magic methods" - __getitem__
# for dict-style access to the underlying dict object, and __getattr__
# for the newer access. __getattr__ also catches calls to items() and keys(),
# so that self.gen.keys() and self.gen.items() continue to work as before,
# when self.gen was simply a plain builtin dict. Change the implementation,
# but leave the interface alone! Implemented as closures that are then
# attached to the current instance as functions to avoid running __getattr__
# needlessly often.

# Precede field names with 'f_' to use the new access style. This causes
# __getattr__ to define a method as a closure that is then attached to
# the current instance, and explicitly returned to satisfy the current
# caller. Optionally, you can also pass in a single letter string, which
# causes the closure to return the part of the record contained within
# the named subfield.

import re

class GenRecord(object):
    def __init__(self, data):
        # Take the dict object returned by GenFileStream, and convert it to
        # something a little easier to use...
        self._data = data

    @property
    def data(self):
        return self._data

    def __getattr__(self, attr):
        if attr == 'keys' or attr == 'items':
            def _attr():
                return getattr(self._data, attr)()
            # Save the closure on self as attr. No need
            # to run through __getattr__ for future invocations.
            setattr(self, attr, _attr)
            return _attr
        elif attr.startswith('f_'):
            field = attr.split('_')[-1]
            try:
                # Fields that occur only once
                d = {}
                for _field in self._data[field].split('$'):
                    try:
                        d[_field[0]] = _field[1:]
                    except IndexError:
                        pass
                values = d
            except AttributeError:
                # Fields that can occur more than once.
                _list_of_fields = []
                for _field in self._data[field]:
                    d = {}
                    # 490 can have '$' as part of the content, so splitting
                    # on that character won't work. Given that 490 has only one
                    # subfield, $a, we can simply set a value for 'a' in the
                    # dictionary and strip off '$a'.
                    if field == '490':
                        d['a'] = re.sub('$a', '', _field)
                    else:
                        for _subfield in _field.split('$'):
                            d[_subfield[0]] = _subfield[1:]
                    _list_of_fields.append(d)
                values = _list_of_fields
            def _get_field(subfield=None):
                if subfield is not None:
                    try:
                        # Fields that occur only once.
                        # Return the requested subfield
                        return values[subfield]
                    except TypeError:
                        # Fields that occur more than once.
                        # Return a list of the requested subdfields.
                        _return = []
                        for i in values:
                            try:
                                _return.append(i[subfield])
                            except KeyError:
                                _return.append(None)
                        return _return   #  [i[subfield] for i in values]
                else:
                    # If no subfield was specified, return the whole field.
                    return self._data[field]
            setattr(self, attr, _get_field)
            return _get_field

    def __getitem__(self, item):
        if item in self.keys():
            return self._data[item]
