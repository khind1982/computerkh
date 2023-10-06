"""Utility functions supporting the pqcoreutils utilities.

See? Meta."""

import sys


def export(fn):
    """A decorator for marking functions as exportable.

    Maintains a module's __all__ attribute dynamically, making splat
    imports somewaht safe and clean. We don't have to use a leading '_'
    character to denote a 'private' function."""
    mod = sys.modules[fn.__module__]
    if hasattr(mod, '__all__'):
        mod.__all__.append(fn.__name__)
    else:
        mod.__all__ = [fn.__name__]
    return fn
