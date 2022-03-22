import sys
import os

import pytest

import lxml.etree as et

import latin_products.preprocessing.add_search_divs as add_search_divs

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

actatestdata = os.path.join(os.path.dirname(__file__), 'testdata/Z400061657.xml')
actatestdatadiv = os.path.join(
    os.path.dirname(__file__), 'testdata/Z400061657_with_note_and_apar.xml')
pldtestdata = os.path.join(os.path.dirname(__file__), 'testdata/Z400149032.xml')

html_parser = et.HTMLParser(remove_blank_text=True)


def test_convert_summary_to_apparatus_acta():
    input = et.parse(actatestdata, html_parser)
    output = add_search_divs.convert_summary_to_apparatus(input)
    assert output.xpath('.//div[@data-pqp-search-type="apparat"]')
    assert len(output.xpath('.//div[@data-pqp-search-type="apparat"]')) == 5


def test_convert_notes_to_note_searchtype_acta():
    input = et.parse(actatestdata, html_parser)
    output = add_search_divs.convert_notes_to_note_searchtype(input)
    # print(et.tostring(output))
    assert output.xpath('.//div[@data-pqp-search-type="note"]')
    assert len(output.xpath('.//div[@data-pqp-search-type="note"]')) == 1


def test_add_note_and_summary_search_elements_acta():
    input = et.parse(actatestdata, html_parser)
    output = add_search_divs.add_note_and_summary_search_elements(input)
    print(et.tostring(output).decode())
    assert len(output.xpath('.//div[@data-pqp-search-type="apparat"]')) == 5
    assert len(output.xpath('.//div[@data-pqp-search-type="note"]')) == 1


def test_add_non_appar_search_divs_acta():
    input = et.parse(actatestdatadiv, html_parser)
    output = add_search_divs.add_note_and_summary_search_elements(input)
    output = add_search_divs.add_non_appar_search_divs(output)
    assert len(output.xpath('.//div[@data-pqp-search-type="non-apparat"]')) == 6
