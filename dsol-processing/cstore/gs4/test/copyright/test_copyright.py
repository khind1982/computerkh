# -*- mode: python -*-

'''
Tests for the script that handles adding and modifying copyright data for the
transformation app.
'''

import os

import pytest
from copyrightmgr import CopyrightManager, CLI


@pytest.fixture
def aaa_lookup():
    '''Make sure we use a stable baseline lookup file for our tests.'''
    aaa_file = os.path.join(
        os.path.dirname(__file__), '../../libdata/epc_copyrights/aaa.lut')
    with open(aaa_file, 'w') as f:
        f.write("# This file is managed by the copyright script.\n")
        f.write("# Beware of manually editing it!\n\n")
        f.write("AAA1234|Copyright text here\n")
        f.write("AAA1235|Different copyright text\n")


@pytest.fixture(params=['aaa', 'bpd'])
def product_fixture(request):
    '''A very simple way to test against multiple product codes.'''
    return request.param


def test_copyright_manager_initialisation(product_fixture):
    cr_mgr = CopyrightManager(product_fixture)
    assert getattr(cr_mgr, 'product') == product_fixture
    assert hasattr(cr_mgr, 'data_file')
    assert os.path.isdir(os.path.dirname(getattr(cr_mgr, 'data_file')))
    assert hasattr(cr_mgr, 'lookup_data')


def test_read_existing_data(product_fixture, aaa_lookup):
    cr_mgr = CopyrightManager(product_fixture)
    assert isinstance(cr_mgr.lookup_data, dict)
    if product_fixture == 'aaa':
        assert 'AAA1234' in cr_mgr.lookup_data.keys()
        assert cr_mgr.lookup_data['AAA1235'] == "Different copyright text"


def test_invalid_product():
    with pytest.raises(RuntimeError) as exc:
        CopyrightManager('nosuchproduct')
    assert 'nosuchproduct - unknown product code' in str(exc.value)


def test_product_with_no_cr_lookup():
    with pytest.raises(RuntimeError) as exc:
        CopyrightManager('vogue')
    assert 'vogue - product does not use' in str(exc.value)


def test_add_new_value(aaa_lookup):
    cr_mgr = CopyrightManager('aaa')
    cr_mgr.add(key="AAA9876", value="Some copyright text")
    assert 'AAA9876' in cr_mgr.lookup_data
    cr_mgr2 = CopyrightManager('aaa')
    assert 'AAA9876' in cr_mgr2.lookup_data.keys()


def test_call_add_on_existing_value(aaa_lookup):
    cr_mgr = CopyrightManager('aaa')
    with pytest.raises(RuntimeError):
        cr_mgr.add(key='AAA1234', value='New text')

        
def test_delete_value(aaa_lookup):
    cr_mgr = CopyrightManager('aaa')
    cr_mgr.remove('AAA1235')
    assert 'AAA1235' not in cr_mgr.lookup_data.keys()
    cr_mgr2 = CopyrightManager('aaa')
    assert 'AAA1235' not in cr_mgr2.lookup_data.keys()


def test_lookup_key(aaa_lookup):
    cr_mgr = CopyrightManager('aaa')
    key_data = cr_mgr.find('AAA1235')
    assert key_data == 'AAA1235:\tDifferent copyright text'


def test_lookup_missing_key(aaa_lookup):
    cr_mgr = CopyrightManager('aaa')
    key_data = cr_mgr.find('nonesuch')
    assert key_data == "'nonesuch' - not found"


def test_command_line_add(mocker):
    mocker.patch.object(CopyrightManager, 'add')
    CLI('aaa', ['BCD4567', 'some stuff'])
    CopyrightManager.add.assert_called_once_with(
        key='BCD4567', value='some stuff')


def test_command_line_find(mocker):
    mocker.patch.object(CopyrightManager, 'find')
    CLI('aaa', ['AAA1234'])
    CopyrightManager.find.assert_called_once_with(key='AAA1234')


def test_command_line_find_missing_key(mocker):
    mocker.patch.object(CopyrightManager, 'find')
    CLI('aaa', ['nonesuch'])
    CopyrightManager.find.assert_called_once_with(key="nonesuch")


def test_command_line_delete_key(mocker):
    mocker.patch.object(CopyrightManager, 'remove')
    CLI('aaa', ['del', 'AAA1235'])
    CopyrightManager.remove.assert_called_once_with(key='AAA1235')


def test_command_line_force_update(mocker):
    mocker.patch.object(CopyrightManager, 'modify')
    CLI('aaa', ['-f', 'AAA1234', 'New text'])
    CopyrightManager.modify.assert_called_once_with(
        key='AAA1234', value='New text')


def test_command_line_no_jid(capsys):
    CLI('aaa', [])
    out, err = capsys.readouterr()
    assert "Usage:" in err


def test_print_help(capsys):
    CLI()
    out, err = capsys.readouterr()
    assert "Usage:" in err
