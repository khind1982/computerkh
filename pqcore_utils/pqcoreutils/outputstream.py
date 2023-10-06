'''Classes for handling output from transform scripts.


There are two basic modes of operation:

    Bundled mode: Produces files suitable for submitting for load
    to PQIS. By default, these will contain up to 5000 documents,
    and will conform to the required naming conventions

    Singleton mode: Produces one output file for each input file. This
    is ideal for testing - each output file is a valid XML document,
    and so can be parsed or linted without having to split the file
    into document-sized chunks.

Also included are classes for constructing output file paths for each
mode. These can be overridden if they are not suitable for a given
data set. The only stipulation is that a custom PathBuilder must
implement the __call__ special method, since instances are treated
as callables by the Writer classes.

The DefaultBundledPathBuilder creates files suitable for loading
to PQIS, following the prescribed naming conventions. The files are
written in the instance's configured output directory.

The DefaultSingletonPathBuilder creates output files in the instance's
output directory, and names them for the input object.'''

import datetime
import os

import lxml.etree as et


class OutputStreamHandler:
    '''Class to handle writing the output documents. There are essentially
    two modes of operation - Singleton or Bundled. In Singleton mode, each
    input record is written to a file in the named output directory. In bundled
    mode, N records are written to file, and the next N to a different file.
    Parameters for bundled mode include the number of records per output file
    (default 5000), and the base name of the files to create.'''

    defaults = {
        'root_dir': None,
        'bundled_output': None,
        'records': 5000,
        'base_file_name_template': 'CH_SS_<product>_<date>_<seq>',
        'path_builder': None,
        'product': None
        }

    def __init__(self, **kwargs):
        ''''''
        # Set defaults
        for k, v in self.defaults.items():
            setattr(self, k, v)

        # And apply any values provided when instantiated.
        # Discard any k/v pairs we don't recognise.
        for k, v in kwargs.items():
            if k in self.defaults.keys():
                setattr(self, k, v)

        # If bundled_output is True, we use a BundledWriter proxy instance.
        # Otherwise, we use a SingletonWriter proxy instance.
        # We also need to configure an appropriate path builder, if one was
        # not provided by the caller.
        if self.bundled_output:
            if not self.path_builder:
                self.path_builder = DefaultBundledPathBuilder(
                    template=self.base_file_name_template,
                    root_dir=self.root_dir, product=self.product)
            self.write_output = BundledWriter(self.path_builder, self.records)
        else:
            if not self.path_builder:
                self.path_builder = DefaultSingletonPathBuilder(
                    root_dir=self.root_dir)
            self.write_output = SingletonWriter(self.path_builder)


class OutputWriter:
    def __init__(self, path_builder):
        self.path_builder = path_builder

    @staticmethod
    def make_dirs(file_path):
        os.makedirs(os.path.dirname(file_path), mode=0o777, exist_ok=True)

    @staticmethod
    def _format_doc(doc):
        return et.tostring(
           doc, pretty_print=True,
           xml_declaration=True,
           encoding='utf-8')


class BundledWriter(OutputWriter):
    '''A class to handle writing bundled output'''
    def __init__(self, path_builder, records):
        super().__init__(path_builder)
        self.record_count = 0
        self.records = records

    def __call__(self, doc, doc_id):
        '''This is the write functionality when we are asked to create bundled
        output. It keeps track of the number of writes performed, and checks
        against the number of records required per file. If it has written the
        right number of records to the current file it is closed and a new one
        opened.'''
        while True:
            try:
                self._fh.write(self._format_doc(doc))
                self.record_count += 1
                if self.record_count % self.records == 0:
                    self._fh.close()
                break
            except (AttributeError, ValueError):
                output_file_path = self.path_builder()
                self.make_dirs(output_file_path)
                # We need to turn buffering off in order to not lose data.
                self._fh = open(output_file_path, 'w+b', 0)


class SingletonWriter(OutputWriter):
    '''Handles writing a single record to a single file.'''
    def __call__(self, doc, doc_id):
        output_file_path = self.path_builder(doc_id)
        self.make_dirs(output_file_path)

        with open(output_file_path, 'w+b') as outf:
            outf.write(self._format_doc(doc))


class DefaultBundledPathBuilder:
    '''Used to create filenames suitable for use with bundled output mode.'''
    call_count = 0
    batch_date = datetime.datetime.strftime(
            datetime.datetime.now(), '%Y%m%d')

    def __init__(self, template, root_dir, product):
        self.template = template
        self.root_dir = root_dir
        self.product = product

    def __call__(self, **kwargs):
        # Construct the path from the root_dir passed in, and the template
        # provided at instantiation. In this case, object_id is the value
        # interpolated into the template in the <product> position. We also
        # keep track of the number of times we've been called, so we can
        # increment the seq_num value, which is used as the final part of
        # constructed filename.

        fn = self.template.replace('<product>', self.product)
        fn = fn.replace('<date>', self.batch_date)
        fn = fn.replace('<seq>', str(self.call_count).zfill(3))
        self.call_count += 1
        return os.path.join(self.root_dir, '%s.xml' % fn)


class DefaultSingletonPathBuilder:
    '''Used to create the file path for use in Singleton mode. The default
    behaviour is to write the output files in the root directory passed to
    the constructor. If different behaviour is required, such as nesting the
    output somehow, provide a path builder that implements the PathBuilder
    protocol (i.e. it must implement the __call__ special method to create
    the output path on demand.)'''
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def __call__(self, object_id):
        # The default behaviour for Singleton output mode is simply to drop
        # the files in the root directory.
        return os.path.join(self.root_dir, '%s.xml' % object_id)
