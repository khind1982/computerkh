"""Classes that wrap the lxml.etree.XMLSchema class.

We provide a little bit of application-specific convenience, and
we also add simple logging of validation errors.

The XMLSchemaValidator base class expects the full path to the target
schema file as its first argument. The second argument is the path to
use as the log file.

The IngestSchemaValidator class adds a little bit of convenience - it
expects the path to the directory containing the local copies of the
Ingest Schema, and the minor version number to identify the exact file
to load and use for validation.

It is, of course, possible to use the base XMLSchemaValidator class
to validate against the Ingest Schema, but you will have to pass in
the full path to the file you want.
"""
import datetime
import functools
import os
import sys

from collections import defaultdict
from io import BytesIO
from typing import Union

import lxml.etree as et

from .misc import fn_pipeline


Validator = Union["XMLSchemaValidator", "IngestSchemaValidator", "NullValidator"]


class NullableValidator(type):
    """Metaclass to allow runtime selection of Validator implementation.
    If the user calls XMLSchemaValidator with null=True, return a NullValidator;
    otherwise return an instance of XMLSchemaValidator."""

    def __call__(cls, *args, **kwargs) -> Validator:
        if kwargs.pop("null", False):
            return NullValidator()
        obj: Validator = cls.__new__(cls, *args, **kwargs)  # type: ignore[call-overload,arg-type]
        getattr(obj, "__init__")(*args, **kwargs)
        return obj


class XMLSchemaValidator(metaclass=NullableValidator):
    """Base XML Schema validator."""

    def __init__(self, schema_file, logfile=None, *, errors=None):  # noqa: ignore=D107
        self.schema_file = schema_file
        self.schema = self._prepare_schema(schema_file)
        self._set_logfile(logfile)
        self.errors = errors or defaultdict(list)

    def _prepare_schema(self, schema_file):
        return et.XMLSchema(et.parse(schema_file))

    def _set_logfile(self, logfile):
        if logfile:
            self.logfile = logfile
        else:
            self.logfile = os.path.join(os.path.expanduser("~"), "validation.log")

    def validate(self, doc, docid, huge_tree=False):
        """Validate the passed doc.

        Success is indicated when no exception is raised.
        """
        # Converts doc to a bytes object by passing it to et.tostring,
        # then parses it with a parser that won't strip out CDATA tags, and
        # finally sends it through the XMLSchema instance's assertValid method.
        # TODO: Create new keyword argument - add args to line 79 as appropriate
        # e.g. huge_tree=True
        try:
            fn_pipeline(
                et.tostring,
                BytesIO,
                functools.partial(
                    et.parse,
                    parser=et.XMLParser(strip_cdata=False, huge_tree=huge_tree),
                ),
                self.schema.assertValid,
            )(doc)
        except et.DocumentInvalid as exc:
            self.errors[docid].append(exc)
            self.log_error(docid, exc)
            raise

    def log_error(self, docid, exc):
        """Write a log message to the logfile."""
        t_f = "%Y:%m:%d %H:%M:%S"
        ts = datetime.datetime.strftime(datetime.datetime.now(), t_f)
        with open(self.logfile, "a") as logf:
            logf.write("%s : Validation error: %s :: %s\n" % (ts, docid, exc))

    def error_report(self):
        for doc, errors in self.errors.items():
            print(f"ERROR: {doc}", file=sys.stderr)
            for error in errors:
                print(error, file=sys.stderr)
            print("-------------------------------", file=sys.stderr)


class IngestSchemaValidator(XMLSchemaValidator):
    """Subclass for handling validation against the Ingest Schema.

    Receives the path to the directory containing the schema files,
    and the minor version number to use.
    """

    def __init__(self, schema_path, minor_version, logfile=None):  # noqa: ignore=D107
        schema_file = self._get_schema_file(schema_path, minor_version)
        super().__init__(schema_file, logfile=logfile)

    def _get_schema_file(self, schema_path, minor_version):
        return os.path.join(schema_path, "Ingest_v5.1.%s.xsd" % minor_version)


class NullValidator(metaclass=NullableValidator):
    """A null validator that silently consumes calls to the validate and
    error_report methods.  It can be used as a drop-in replacement for a normal
    validator, when the user wants to turn off schema validation."""

    def __init__(self, *args, **kwargs):
        pass

    def validate(self, *args, **kwargs):
        pass

    def error_report(self, *args, **kwargs):
        pass
