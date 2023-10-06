import argparse
import pathlib


class SameInputOutputError(Exception):
    ...


class EnforceDifferentOutputLocation(argparse.Action):
    """A custom action to be used with argument parsing. If this
    action is used an exeception will be raised if the user tries to
    specify the same input and output on the command line.
    Values is a tuple containing the input and output parameters"""
    def __init__(self, option_strings, dest, nargs=None, **kwargs):
        if nargs:  # pragma: no cover
            raise ValueError("nargs not allowed")
        super().__init__(option_strings, dest, **kwargs)
        try:
            self.const = kwargs['const']
        except KeyError as e:
            raise TypeError from e

    def __call__(self, parser, namespace, values, option_string=None):
        indir = pathlib.Path(getattr(namespace, self.const))
        outdir = pathlib.Path(values)
        if (outdir == indir or indir in outdir.parents):
            raise SameInputOutputError(
                f'Output directory ({indir}) cannot '
                f'be the same as input directory ({values})')
        setattr(namespace, self.dest, values)
