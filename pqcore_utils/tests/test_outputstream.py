"""Tests for the output stream handler module"""

import os

import lxml.etree as et

import pqcoreutils
import pqcoreutils.outputstream as outputstream


def test_outputstream_handler_defaults():
    '''Make sure we correctly handle arguments'''
    stream_handler = outputstream.OutputStreamHandler(
            product='test_produt', unknown_key='ignore_me')
    assert "product" in stream_handler.__dict__
    assert "unknown_key" not in stream_handler.__dict__

    assert isinstance(
            stream_handler.path_builder,
            outputstream.DefaultSingletonPathBuilder)

    assert isinstance(
            stream_handler.write_output,
            outputstream.SingletonWriter)


def test_outputstream_handler_bundled_mode():
    '''Make sure everything is wired up correctly in bundled mode'''
    stream_handler = outputstream.OutputStreamHandler(
            product='test_product', bundled_output=True)
    assert isinstance(
            stream_handler.path_builder,
            outputstream.DefaultBundledPathBuilder)
    assert isinstance(
            stream_handler.write_output,
            outputstream.BundledWriter)


def test_default_singleton_path_builder(tmpdir_factory):
    '''DefaultSingletonPathBuilder works?'''
    root_dir = tmpdir_factory.mktemp('singleton_path_builder_test')
    p_builder = outputstream.DefaultSingletonPathBuilder(
            root_dir.strpath)
    assert p_builder('test') == os.path.join(root_dir.strpath, 'test.xml')


def test_default_bundled_path_builder(tmpdir_factory):
    '''And the DefaultBundledPathBuilder?'''
    root_dir = tmpdir_factory.mktemp('bundled_output_builder_test')
    p_builder = outputstream.DefaultBundledPathBuilder(
            "test_<product>_filename_<seq>",
            root_dir.strpath, 'test_product')
    assert p_builder() == os.path.join(
            root_dir.strpath, 'test_test_product_filename_000.xml')

    assert p_builder.call_count == 1

    assert p_builder() == os.path.join(
            root_dir.strpath, 'test_test_product_filename_001.xml')

    assert p_builder.call_count == 2


def test_singleton_output_writer(tmpdir_factory):
    '''Make sure the singletom writer works'''
    root_dir = tmpdir_factory.mktemp('s_writer_test')
    sample_doc = et.fromstring("""
            <root><element1><element2>value</element2></element1></root>""")
    p_builder = outputstream.DefaultSingletonPathBuilder(root_dir.strpath)
    s_writer = outputstream.SingletonWriter(
            path_builder=p_builder)
    s_writer(sample_doc, 'test_doc')
    assert os.path.isfile(os.path.join(root_dir.strpath, 'test_doc.xml'))


def test_bundled_output_writer(tmpdir_factory):
    '''And now the bundled output writer.'''
    root_dir = tmpdir_factory.mktemp('b_writer_test')
    sample_docs = [
            et.fromstring("""
            <root><element1><element2>value</element2></element1></root>
            """),
            et.fromstring("""
            <root><element1><element2>value</element2></element1></root>
            """),
            et.fromstring("""
            <root><element1><element2>value</element2></element1></root>
            """)
            ]

    p_builder = outputstream.DefaultBundledPathBuilder(
            "test_<product>_<seq>",
            root_dir.strpath, 'test_product')

    p_writer = outputstream.BundledWriter(path_builder=p_builder, records=3)
    for d in sample_docs:
        p_writer(d, 'test_doc')

    assert os.path.isfile(
            os.path.join(
                root_dir.strpath,
                'test_test_product_000.xml'))


def test_outputstream_handler(tmpdir_factory):
    '''Pass in path builder instances'''
    root_dir = tmpdir_factory.mktemp('outoutstream_test')
    p_builder = outputstream.DefaultSingletonPathBuilder(root_dir.strpath)
    stream_handler = outputstream.OutputStreamHandler(path_builder=p_builder)
    assert stream_handler.path_builder is p_builder

    p_builder = outputstream.DefaultBundledPathBuilder(
            "test_template", root_dir.strpath, 'test_product')

    stream_handler = outputstream.OutputStreamHandler(
            path_builder=p_builder, bundled_output=True)
    assert stream_handler.path_builder is p_builder
