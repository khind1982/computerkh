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
import os

from io import BytesIO

import lxml.etree as et


class XMLSchemaValidator:
    """Base XML Schema validator."""

    def __init__(self, schema_file, logfile=None):  # noqa: ignore=D107
        self.schema = self._prepare_schema(schema_file)
        self._set_logfile(logfile)

    def _prepare_schema(self, schema_file):
        s = et.parse(schema_file)
        return et.XMLSchema(s)

    def _set_logfile(self, logfile):
        if logfile:
            self.logfile = logfile
        else:
            self.logfile = os.path.join(os.path.expanduser('~'),
                                        'transform-validation.log')

    def validate(self, doc, book):
        """Validate the passed doc.

        Success is indicated when no exception is raised.
        """
        # Converts doc to a bytes object by passing it to et.tostring,
        # then parses it with a parser that won't strip out CDATA tags, and
        # finally sends it through the XMLSchema instance's assertValid method.
        try:
            self.schema.assertValid(
                et.parse(BytesIO(
                    et.tostring(doc)), parser=et.XMLParser(strip_cdata=False)))
        except et.DocumentInvalid as exc:
            self.log_error(book, exc)
            raise

    def log_error(self, book, exc):
        """Write a log message to the logfile."""
        t_f = '%Y:%m:%d %H:%M:%S'
        ts = datetime.datetime.strftime(datetime.datetime.now(), t_f)
        with open(self.logfile, 'a') as logf:
            logf.write(
                "%s : Validation error: %s :: %s\n" % (ts, book[0], exc))


class IngestSchemaValidator(XMLSchemaValidator):
    """Subclass for handling validation against the Ingest Schema.

    Receives the path to the directory containing the schema files,
    and the minor version number to use.
    """

    def __init__(self, schema_path, minor_version, logfile=None):  # noqa: ignore=D107

        schema_file = self._get_schema_file(schema_path, minor_version)
        super().__init__(schema_file, logfile)

    def _get_schema_file(self, schema_path, minor_version):
        return os.path.join(schema_path, 'Ingest_v5.1.%s.xsd' % minor_version)
