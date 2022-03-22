import sys
import os
import datetime
import logging

import pytest

import lxml.etree as et

from collections import namedtuple
from shutil import copy

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import latin_products.transform.ingest.citations as citations
import latin_products.transform.ingest.fulltext as fulltext

from pqcoreutils.fileutils import build_input_file_list

actatestdata = os.path.join(os.path.dirname(__file__), 'testdata/Z400067037.xml')
actatestdataft = os.path.join(os.path.dirname(__file__), 'testdata/Z400068144.xml')
actatestdatalangs = os.path.join(os.path.dirname(__file__), 'testdata/Z400062232.xml')
pldtestdata = os.path.join(os.path.dirname(__file__), 'testdata/Z300148711.xml')
pldtestdataimages = os.path.join(
    os.path.dirname(__file__), 'testdata/Z500036966.xml')
pldtestdatalangs = os.path.join(
    os.path.dirname(__file__), 'testdata/Z400070388.xml')

html_parser = et.HTMLParser(remove_blank_text=True)

xslt = et.parse(os.path.join(os.path.dirname(__file__), '../latin_products/transform/xsl/gsl-transform.xsl'))
xslt_transform = et.XSLT(xslt)


def setup_logger(loglvl):
    logger = logging.getLogger('citations')
    logging.basicConfig(level=loglvl)
    return logger

logger = setup_logger('DEBUG')


@pytest.fixture
def output_dir(tmpdir_factory):
    """A base input directory for test output files."""
    return tmpdir_factory.mktemp("output")


@pytest.fixture
def acta_indir(tmpdir_factory):
    actaindir = tmpdir_factory.mktemp("acta")
    copy(actatestdata, actaindir)
    return actaindir


@pytest.fixture
def pld_indir(tmpdir_factory):
    pldindir = tmpdir_factory.mktemp("pld")
    copy(pldtestdata, pldindir)
    return pldindir


@pytest.fixture
def sample_acta_args(acta_indir, output_dir):
    args = namedtuple('args', 'indir outdir product minor_version loglvl instance targets toc_location')
    sample_args = args(
        indir=str(acta_indir),
        outdir=str(output_dir),
        product='acta',
        minor_version='64',
        loglvl='DEBUG',
        instance='dev',
        targets=False,
        toc_location='/dc/migrations/latin/acta/transform/input/01_toc'
    )
    return sample_args


@pytest.fixture
def sample_pld_args(pld_indir, output_dir):
    args = namedtuple('args', 'indir outdir product minor_version loglvl instance targets toc_location')
    sample_args = args(
        indir=str(pld_indir),
        outdir=str(output_dir),
        product='pld',
        minor_version='64',
        loglvl='DEBUG',
        instance='dev',
        targets=False,
        toc_location='/dc/migrations/latin/pld/processing/toc_output/'
    )
    return sample_args

def test_fixtures(sample_pld_args, sample_acta_args):
    for f in build_input_file_list(sample_pld_args.indir):
        assert os.path.basename(f) == "Z300148711.xml"
    for f in build_input_file_list(sample_acta_args.indir):
        assert os.path.basename(f) == "Z400067037.xml"


def test_render_ingest_record_acta(sample_acta_args):
    logger = setup_logger(sample_acta_args.loglvl)
    acta_input = et.parse(actatestdata, html_parser)
    actual = citations.render_ingest_record(
        acta_input, xslt_transform, sample_acta_args, logger)
    assert actual.xpath('.//LegacyID')[0].text == 'acta-Z400067037'
    assert actual.xpath('.//PublicationInfo/LegacyPubID')[0].text == 'acta-Z000065230'
    assert actual.xpath('.//ObjectInfo/ObjectType')[0].text == 'Book Chapter'
    assert actual.xpath('.//ObjectInfo/ObjectType/@ObjectTypeOrigin')[0] == 'acta'
    assert "Vita Auctore Laurentio Surio Carthusiano" in actual.xpath('.//Title')[0].text
    assert actual.xpath('.//ObjectInfo/ObjectNumericDate')[0].text == '16430101'
    assert actual.xpath('.//ObjectInfo/ObjectRawAlphaDate')[0].text == '1643'
    assert actual.xpath('.//PrintLocation/StartPage')[0].text == '681'
    assert actual.xpath('.//PrintLocation/Pagination')[0].text == '654-689'
    assert actual.xpath('.//ObjectInfo/Language/RawLang')[0].text == 'Latin'
    assert actual.xpath('.//ObjectInfo/Language/@IsPrimary')[0] == 'true'
    assert actual.xpath(".//ObjectID[@IDType='CHLegacyID']")[0].text == 'acta-Z400067037'
    assert actual.xpath(".//ObjectID[@IDType='CHOriginalLegacyID']")[0].text == 'Z400067037'
    assert actual.xpath(".//Terms/Term[@TermType='Personal']/TermValue")[0].text == 'Henricus Suso, ordinis Praedicat. Ulmae in Germania'
    assert actual.xpath(".//Terms/FlexTerm[@FlexTermName='SaintGender']/FlexTermValue")[0].text == 'Male'
    assert actual.xpath(".//Terms/FlexTerm[@FlexTermName='FeastMonth']/FlexTermValue")[0].text == 'Januarius'
    assert actual.xpath(".//Terms/FlexTerm[@FlexTermName='FeastDay']/FlexTermValue")[0].text == '25'
    assert actual.xpath(".//Terms/FlexTerm[@FlexTermName='ReligiousWorkType']/FlexTermValue")[0].text == 'Latin hagiographical texts post-1500'
    assert actual.xpath(".//Contributors/Contributor/OriginalForm")[0].text == 'Society of Bollandists'


@pytest.mark.xfail(Reason="Do not test until BHL Number functionality added to product.")
def test_render_ingest_record_acta_bhl_number_handling(sample_acta_args):
    logger = setup_logger(sample_acta_args.loglvl)
    acta_input = et.parse(actatestdata, html_parser)
    actual = citations.render_ingest_record(
        acta_input, xslt_transform, sample_acta_args, logger)
    assert actual.xpath(".//ObjectIDs/ObjectID[@IDType='BHLNumber']")[0].text == '1586'


def test_render_ingest_record_pld(sample_pld_args):
    logger = setup_logger(sample_pld_args.loglvl)
    pld_input = et.parse(pldtestdata, html_parser)
    actual = citations.render_ingest_record(
        pld_input, xslt_transform, sample_pld_args, logger)
    assert actual.xpath('.//LegacyID')[0].text == 'pld-Z300148711'
    assert actual.xpath('.//PublicationInfo/LegacyPubID')[0].text == 'pld-Z000148702'
    assert actual.xpath('.//ObjectInfo/ObjectType')[0].text == 'Book Chapter'
    assert actual.xpath('.//ObjectInfo/ObjectType/@ObjectTypeOrigin')[0] == 'pld'
    assert "HISTORIARUM LIBRI TRES" in actual.xpath('.//Title')[0].text
    assert actual.xpath('.//ObjectInfo/ObjectNumericDate')[0].text == '18530101'
    assert actual.xpath('.//ObjectInfo/ObjectRawAlphaDate')[0].text == '1853'
    assert actual.xpath('.//PrintLocation/StartPage')[0].text == '107'
    assert actual.xpath('.//PrintLocation/Pagination')[0].text == '0019-0079'
    assert actual.xpath('.//ObjectInfo/Language/RawLang')[0].text == 'Latin'
    assert actual.xpath('.//ObjectInfo/Language/@IsPrimary')[0] == 'true'
    assert actual.xpath(".//ObjectIDs/ObjectID[@IDType='CHLegacyID']")[0].text == 'pld-Z300148711'
    assert actual.xpath(".//ObjectIDs/ObjectID[@IDType='CHOriginalLegacyID']")[0].text == 'Z300148711'
    assert actual.xpath(".//Contributors/Contributor/OriginalForm")[0].text == 'Cibardi, Ademarus'
    assert actual.xpath(".//Contributors/Contributor/ContribDesc")[0].text == 'Medieval author'


def test_render_ingest_record_acta_does_not_produce_copyright(sample_acta_args):
    logger = setup_logger(sample_acta_args.loglvl)
    acta_input = et.parse(actatestdata, html_parser)
    actual = citations.render_ingest_record(
        acta_input, xslt_transform, sample_acta_args, logger)
    with pytest.raises(AssertionError):
        assert actual.xpath('//ObjectInfo/Copyright/CopyrightData')


def test_render_ingest_record_pld_does_not_produce_copyright(sample_pld_args):
    logger = setup_logger(sample_pld_args.loglvl)
    pld_input = et.parse(pldtestdata, html_parser)
    actual = citations.render_ingest_record(
        pld_input, xslt_transform, sample_pld_args, logger)
    with pytest.raises(AssertionError):
        assert actual.xpath('//ObjectInfo/Copyright/CopyrightData')


def test_render_ingest_record_does_not_have_notes(sample_pld_args):
    logger = setup_logger(sample_pld_args.loglvl)
    pld_input = et.parse(pldtestdata, html_parser)
    actual = citations.render_ingest_record(
        pld_input, xslt_transform, sample_pld_args, logger)

    with pytest.raises(AssertionError):
        assert actual.xpath('//Notes/Note[@NoteType="Publication"]')


def test_render_ingest_record_acta_does_not_produce_title_flexterm(sample_acta_args):
    logger = setup_logger(sample_acta_args.loglvl)
    acta_input = et.parse(actatestdata, html_parser)
    actual = citations.render_ingest_record(
        acta_input, xslt_transform, sample_acta_args, logger)
    with pytest.raises(AssertionError):
        assert actual.xpath('//Terms/FlexTerm[@FlexTermName="SubjWork"]/FlexTermValue')
        assert actual.xpath('//Terms/FlexTerm[@FlexTermName="SubjAuth"]/FlexTermValue')


def test_render_ingest_record_appends_toc_to_ingest_record(sample_pld_args):
    logger = setup_logger(sample_pld_args.loglvl)
    pld_input = et.parse(pldtestdata, html_parser)
    actual = citations.render_ingest_record(
        pld_input, xslt_transform, sample_pld_args, logger)
    assert actual.xpath('//TOC2')
    assert actual.xpath('//MaxLevels')[0].text == '8'


def test_render_ingest_record_handles_missing_saintname(sample_acta_args):
    """Given a single work record with empty saintname field, ensure an
    empty personal term is not created."""
    acta_input = et.parse(os.path.join(os.path.dirname(__file__), 'testdata/Z200000007.xml'), html_parser)
    result = citations.render_ingest_record(
        acta_input, xslt_transform, sample_acta_args, logger)
    term = result.xpath('.//Terms/Term[@TermType="Personal"]')
    assert not term


class TestTitleScenarios:
    """Given a single work record with mainhead and comhd2, ensure only mainhead is selected."""
    acta_input = et.parse(os.path.join(os.path.dirname(__file__), 'testdata/Z200000007.xml'), html_parser)

    def test_comhd_and_mainhead_present(self, sample_acta_args):
        result = citations.render_ingest_record(
            self.acta_input, xslt_transform, sample_acta_args, logger)
        field = result.xpath('.//Title')[0]
        assert field.text == 'Martyrologium Romanum'

    def test_onlycomhd(self, sample_acta_args):
        self.acta_input.xpath('.//comhd2')[0].text = 'Added comhd2 text'
        mainhead = self.acta_input.xpath('.//mainhead')[0]
        mainhead.getparent().remove(mainhead)
        result = citations.render_ingest_record(
            self.acta_input, xslt_transform, sample_acta_args, logger)
        field = result.xpath('.//Title')[0]
        assert field.text == 'Added comhd2 text'


@pytest.mark.xfail(reason='not yet implemented')
def test_process_fulltext_in_isolation_acta(sample_acta_args):
    logger = setup_logger(sample_acta_args.loglvl)
    acta_input = et.parse(actatestdataft, html_parser)
    actual = fulltext.process_fulltext(
        acta_input,
        sample_acta_args.product,
        sample_acta_args.loglvl,
        sample_acta_args.indir,
        sample_acta_args.instance)
    assert actual.xpath('//div[@data-pqp-search-type="apparat"]')


@pytest.mark.xfail(reason='not yet implemented')
def test_process_fulltext_in_isolation_pld(sample_pld_args):
    logger = setup_logger(sample_pld_args.loglvl)
    pld_input = et.parse(pldtestdata, html_parser)
    actual = fulltext.process_fulltext(
        pld_input,
        sample_pld_args.product,
        sample_pld_args.loglvl,
        sample_pld_args.indir,
        sample_pld_args.instance)
    assert actual.xpath('.//end_note')
    assert actual.xpath('.//end_note/@pqid')[0] == 'end_PN110748'
    assert actual.xpath('.//end_note/@link')[0] == 'PN110748'
    assert "Gestorum" in actual.xpath('.//note/@title')[0]


def test_process_fulltext_inline_image_divs(sample_pld_args):
    logger = setup_logger(sample_pld_args.loglvl)
    pld_input = et.parse(pldtestdataimages, html_parser)
    actual = fulltext.process_fulltext(
        pld_input,
        sample_pld_args.product,
        sample_pld_args.loglvl,
        sample_pld_args.indir,
        sample_pld_args.instance)
    assert actual.xpath(".//div/object/@class")[0] == 'mstar_link_to_media'
    assert actual.xpath(".//div/object[@class='mstar_link_to_media']/param/@name")[0] == 'mstar_lm_alignment'
    assert actual.xpath(".//div/object[@class='mstar_link_to_media']/param/@name")[1] == 'mstar_lm_display_control'
    assert actual.xpath(".//div/object[@class='mstar_link_to_media']/param/@name")[2] == 'mstar_lm_media_type'
    assert actual.xpath(".//div/object[@class='mstar_link_to_media']/param/@value")[3] == '1'


def test_render_ingest_record_has_fulltext_components(sample_pld_args):
    logger = setup_logger(sample_pld_args.loglvl)
    pld_input = et.parse(pldtestdataimages, html_parser)
    actual = citations.render_ingest_record(
        pld_input, xslt_transform, sample_pld_args, logger)
    assert actual.xpath('.//Component/@ComponentType')[1] == 'FullText'
    assert actual.xpath(".//Component/Representation[@RepresentationType='FullText']")
    assert actual.xpath(".//Component/Representation[@RepresentationType='FullText']/MimeType")[0].text == "text/xml"
    assert actual.xpath(".//Component/Representation[@RepresentationType='FullText']/Resides")[0].text == "FAST"


def test_render_ingest_record_has_inline_image_components(sample_pld_args):
    logger = setup_logger(sample_pld_args.loglvl)
    pld_input = et.parse(pldtestdataimages, html_parser)
    actual = citations.render_ingest_record(
        pld_input, xslt_transform, sample_pld_args, logger)
    assert actual.xpath('.//Component/@ComponentType')[2] == 'InlineImage'
    assert actual.xpath(".//InlineImageCount")[0].text == '8'
    assert actual.xpath(".//OrderCategory")[0].text == 'Illustration'
    assert actual.xpath(".//Representation[@RepresentationType='Full']/MimeType")[0].text == 'image/jpeg'
    assert actual.xpath(".//Representation[@RepresentationType='Full']/Resides")[0].text == 'HMS'
    assert actual.xpath(".//Representation[@RepresentationType='Full']/MediaKey")[0].text == '/media/hms/OBJ/6A8N'


def test_main_integration_function_acta(sample_acta_args):
    # logger = setup_logger(sample_acta_args.loglvl)
    citations.main(sample_acta_args)
    assert os.listdir(sample_acta_args.outdir)[0] == f'CH_SS_acta_{str(datetime.date.today()).replace("-", "")}_Z400067037.xml'


def test_main_integration_function_pld(sample_pld_args):
    # logger = setup_logger(sample_acta_args.loglvl)
    citations.main(sample_pld_args)
    assert os.listdir(sample_pld_args.outdir)[0] == f'CH_SS_pld_{str(datetime.date.today()).replace("-", "")}_Z300148711.xml'
