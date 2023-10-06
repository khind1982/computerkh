import os
import sys

import pqcoreutils.argparse_actions as actions

import argparse
import pytest


@pytest.mark.parametrize("indir,outdir", [
    ('/path/to/input', '/path/to/input/'),
    ('/path/to/input', '/path/to/input/output/new'),
])
def test_EnforceDifferentOutputLocation(indir, outdir):
    """
    Current problems:
    - Enforcing the dev to use 'indir' for the positional parameter

    Possible solutions:
    - Using custom type to indicate input and output
    - Custom hook/parse_args method that intercepts the arguments and does the checking.

    """
    parser = argparse.ArgumentParser()
    parser.add_argument('indir')
    parser.add_argument('outdir',
        action=actions.EnforceDifferentOutputLocation, const='indir')
    with pytest.raises(actions.SameInputOutputError):
        parser.parse_args([indir, outdir])


@pytest.mark.parametrize("indir,outdir", [
    ('/path/to/input', '/path/to/output'),
    ('/path/to/input', '/path/to/inputnew/output')
])
def test_exception_not_raised_when_different_inputs_outputs(indir, outdir):
    """Given a user implementing the EnforceDifferent.. action,
    when the input and output are different, then an exception is not
    raised."""
    parser = argparse.ArgumentParser()
    parser.add_argument('indir')
    parser.add_argument('outdir',
        action=actions.EnforceDifferentOutputLocation, const='indir')
    args = parser.parse_args([indir, outdir])
    assert args.outdir == outdir


def test_EnforceDifferentOutputLocation_raise_TypeError_on_missing_const():
    """Given a user implementing the EnforceDifferent.. action, when they don't
    include the const pointing to the input directory, then tells them that in a
    helpful way."""
    parser = argparse.ArgumentParser()
    parser.add_argument('indir')
    with pytest.raises(TypeError):
        parser.add_argument('outdir',
            action=actions.EnforceDifferentOutputLocation)


def test_custom_action_instantiates_with_user_options():
    """Given a user implementing a custom action from this module,
    when it is instantiated, then all the other user options (metavar, help etc)
    are included as normal."""
    parser = argparse.ArgumentParser()
    outdir = parser.add_argument('outdir', metavar="OUTPUT",
        action=actions.EnforceDifferentOutputLocation,
        const='indir')
    assert outdir.metavar == 'OUTPUT'



# Ideas for other custom actions:
# Calling read_lookup_files (and file_to_lookup) - will need to add to the namespace rather than overwriting the input from cli
# Action for creating output directory; this would call the EnforceSeparateOutput action.
# Would also need to consider what you do if the directory exists and contains files.
