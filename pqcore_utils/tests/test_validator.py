"""Tests for the XML Schema validator convenience class."""
import os
import textwrap

import lxml.etree as et
import pytest

import pqcoreutils.validator as validator


schema_data = textwrap.dedent(
    """\
        <?xml version="1.0"?>
        <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
            elementFormDefault="qualified">
          <xs:element name="root">
            <xs:complexType>
              <xs:sequence>
                <xs:element name="title" type="xs:string"/>
                <xs:element name="notes" type="xs:string" minOccurs="0" />
              </xs:sequence>
            </xs:complexType>
          </xs:element>
        </xs:schema>
    """
)


@pytest.fixture(scope="session")
def sample_schema_file(tmpdir_factory):
    schema = tmpdir_factory.mktemp("schema").join("sample.xsd")
    schema.write(schema_data)
    return schema


@pytest.fixture(scope="session")
def sample_ingest_schema(tmpdir_factory):
    schema = tmpdir_factory.mktemp("ingest_schema").join("Ingest_v5.1.64.xsd")
    schema.write(schema_data)
    return schema


@pytest.fixture(scope="session")
def sample_doc(tmpdir_factory):
    doc = tmpdir_factory.mktemp("sample").join("doc.xml")
    doc.write(
        textwrap.dedent(
            """\
        <?xml version="1.0"?>
        <root>
          <title>My Title</title>
        </root>
        """
        )
    )
    return doc


@pytest.fixture(scope="session")
def bad_doc(tmpdir_factory):
    doc = tmpdir_factory.mktemp("sample").join("bad_doc.xml")
    doc.write(
        textwrap.dedent(
            """\
        <?xml version="1.0"?>
        <root>
          <title>abc</title>
          <author>Someone</author>
        </root>
        """
        )
    )
    return doc


@pytest.fixture(scope="session")
def doc_with_junk_xml_in_cdata(tmpdir_factory):
    """A document with invalid XML wrapped inside CDATA tags."""
    doc = tmpdir_factory.mktemp("sample").join("bad_cdata.xml")
    doc.write(
        textwrap.dedent(
            """\
        <?xml version="1.0"?>
        <root>
          <title>bad doc, bad!</title>
          <notes><![CDATA[<not an="element"]]></notes>
        </root>
        """
        )
    )
    return doc


def test_validator_loads_schema(sample_schema_file):
    sv = validator.XMLSchemaValidator(sample_schema_file.strpath)
    assert sv.schema
    assert sv.logfile == os.path.abspath(
        os.path.join(os.path.expanduser("~"), "validation.log")
    )

    sv = validator.XMLSchemaValidator(
        sample_schema_file.strpath, logfile="./my.logfile"
    )
    assert sv.logfile == "./my.logfile"


def test_validator_reports_its_schema_file(sample_schema_file):
    sv = validator.XMLSchemaValidator(sample_schema_file.strpath)
    assert sv.schema_file == sample_schema_file.strpath


def test_validator_with_good_file(sample_schema_file, sample_doc):
    """Make sure a good doc goes through validation without errors"""
    sv = validator.XMLSchemaValidator(sample_schema_file.strpath)
    xml = et.parse(sample_doc.strpath)
    assert sv.validate(xml, "test_doc") is None
    assert bool(sv.errors) is False


def test_validator_with_huge_file(sample_schema_file, huge_tree_xml):
    """Make sure a huge doc goes through validation without errors"""
    sv = validator.IngestSchemaValidator("/dc/migrations/schema/", "77-dev")
    xml = et.parse(
        huge_tree_xml, parser=et.XMLParser(strip_cdata=False, huge_tree=True)
    )
    assert sv.validate(xml, "huge_tree_doc", huge_tree=True) is None
    assert bool(sv.errors) is False


def test_validator_with_bad_file(mocker, sample_schema_file, bad_doc):
    """When given a bad document, we expect the message to be logged,
    and for the lxml exception to be reraised."""
    sv = validator.XMLSchemaValidator(sample_schema_file.strpath)
    mocker.patch.object(sv, "log_error")
    xml = et.parse(bad_doc.strpath)
    with pytest.raises(et.DocumentInvalid):
        sv.validate(xml, "abc")
        assert sv.log_error.called
    assert len(sv.errors) == 1
    assert "abc" in sv.errors.keys()
    assert (
        "Element 'author': This element is not expected."
        in sv.errors.get("abc")[0].__str__()
    )


def test_validator_with_junk_xml_in_cdata(
    mocker, sample_schema_file, doc_with_junk_xml_in_cdata
):
    sv = validator.XMLSchemaValidator(sample_schema_file.strpath)
    mocker.patch.object(sv, "log_error")
    xml = et.parse(doc_with_junk_xml_in_cdata.strpath)
    assert sv.validate(xml, "test") is None
    assert bool(sv.errors) is False


def test_validator_log_error_method(capfd, sample_schema_file, bad_doc):
    """When we get an error, is it properly logged?"""
    sv = validator.XMLSchemaValidator(sample_schema_file.strpath, logfile="/dev/stdout")
    xml = et.parse(bad_doc.strpath)
    with pytest.raises(et.DocumentInvalid):
        sv.validate(xml, "abc")
    output = capfd.readouterr()
    assert ":: Element 'author': This element is not expected." in output.out


# @pytest.mark.skip
def test_ingest_schema_validator(sample_ingest_schema):
    """As a convenience, we provide a class that is geared to loading
    Ingest Schema files."""
    schema_path = os.path.dirname(sample_ingest_schema.strpath)
    sv = validator.IngestSchemaValidator(schema_path, "64")
    assert sv.schema


def test_display_error_messages(capfd, sample_schema_file, bad_doc):
    """Display validation error messages in a nice, easy to read format"""
    sv = validator.XMLSchemaValidator(sample_schema_file.strpath, logfile="/dev/null")
    xml = et.parse(bad_doc.strpath)
    for num in range(10):
        with pytest.raises(et.DocumentInvalid):
            sv.validate(xml, f"bad_doc_{num}")

    assert len(sv.errors) == 10
    sv.error_report()
    output = capfd.readouterr()

    for num in range(10):
        assert f"bad_doc_{num}" in output.err
    assert "author" in output.err


def test_null_validator(capfd, sample_schema_file, sample_doc, bad_doc):
    null_validator = validator.XMLSchemaValidator(str(sample_schema_file), null=True)
    assert isinstance(null_validator, validator.NullValidator)
    assert null_validator.validate("bad xml", "no such ID") is None
    assert null_validator.error_report() is None


def test_validator_with_null_equals_false(sample_schema_file):
    sv = validator.XMLSchemaValidator(str(sample_schema_file), null=False)
    assert isinstance(sv, validator.XMLSchemaValidator)
