import sys
import os
import pytest

import lxml.etree as et

from collections import namedtuple

sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

from latin_products.preprocessing import tracs_records

# @pytest.fixture
# def input_dir(tmpdir_factory):
#     """A base input directory for sample input files."""
#     return tmpdir_factory.mktemp("samples")


@pytest.fixture
def output_dir(tmpdir_factory):
    """A base input directory for test output files."""
    return tmpdir_factory.mktemp("output")


@pytest.fixture
def sample_cvt_indir(tmpdir_factory):
    indir = tmpdir_factory.mktemp("samples")
    fname = f"{indir}/asa01.cvt"
    with open(fname, 'w') as inf:
        inf.write(
            """
                <vlgroup>
                    <div0>
                        <comhd0>
                            <idref>Z000068317</idref>
                            <voltitle>Jan. I</voltitle>
                            <attbytes>12901Kb</attbytes>
                        </comhd0>
                        <div1>
                            <header>
                                <comhd1>
                                    <idref>Z100068318</idref>Bibliographic Details
                                    <attbytes>1Kb</attbytes>
                                </comhd1>
                                <file>
                                    <citn>
                                        <pubtitle>Jan. I</pubtitle>
                                        <city>Cambridge</city>
                                        <pubdate>1999</pubdate>
                                        <publ>Chadwyck-Healey</publ>
                                        <series>Acta Sanctorum Full-Text Database</series>
                                        <copyrite>Copyright &#169; 1999-2002 ProQuest Information and Learning Company. Do not export or print from this database without checking the Copyright Conditions to see what is permitted.</copyrite>
                                    </citn>
                                </file>
                                <source>
                                    <citn>
                                        <editor>
                                            <name>Ioannes Bollandus</name>
                                            <nameinv>Bollandus, Ioannes</nameinv>
                                        </editor>
                                        <editor>
                                            <name>Godefridus Henschenius</name>
                                            <nameinv>Henschenius, Godefridus</nameinv>
                                        </editor>
                                        <pubtitle>Acta Sanctorum Quotquot toto orbe coluntur, vel a Catholicis Scriptoribus celebrantur, Qu&#230; ex Latinis & Gr&#230;cis, aliarumque gentium antiquis monumentis collegit, digessit, Notis illustrauit Ioannes Bollandus Societatis Iesu Theologus, Seruata primigenia Scriptorum phrasi. Operam et Studium Contulit Godefridus Henschenius Eiusdem Societ. Theologus. Prodit nunc duobus Tomis Ianuarius, In quo MCLXX. nominatorum Sanctorum, & aliorum innumerabilium memoria, vel res gest&#230; illustrantur. Ceteri menses ex ordine subsequentur</pubtitle>
                                        <city>Antwerp</city>
                                        <publ>Ioannes Meursius</publ>
                                        <pubdate>1643</pubdate>
                                        <desc>lxii, [22], 1122, [90] p.</desc>
                                    </citn>
                                </source>
                                <acc.no>ASA01</acc.no>
                            </header>
                        </div1>
                    </div0>
                </vlgroup>
            """
        )
    return indir


pld_input_data = et.fromstring("""
    <div0>
        <comhd0>
            <idref>Z000067587</idref>
            <voltitle>Vol. 25</voltitle>
            <attbytes>5705Kb</attbytes>
        </comhd0>
        <div1>
            <comhd1>
                <idref>Z100067588</idref>Bibliographic details
                <attbytes>1Kb</attbytes>
            </comhd1>
            <file>
                <pubcitn>
                    <city>Alexandria, VA</city>
                    <date>1996</date>
                    <publ>Chadwyck-Healey Inc.</publ>
                    <series>Patrologia Latina Database</series>
                    <pubnote>
                    Copyright &#169; 1996 Chadwyck-Healey Inc. Do not export or print from this database without checking the Copyright Conditions to see what is permitted.
                    </pubnote>
                </pubcitn>
            </file>
            <biblio>
                <pubcitn>
                    <title>Patrologiae Cursus Completus, sive bibliotheca universalis ... omnium S.S. Patrum, Doctorum Scriptorumque ecclesiasticorum qui ab aevo apostolico ad Innocentii III tempora floruerunt ... SERIES PRIMA,</title>
                    <desc>PATROLOGIAE TOMUS XXV.</desc>
                    <authors>S. HIERONYMI</authors>
                    <auth.no>TOMI QUINTUS ET SEXTUS.</auth.no>
                    <imprint>PARISIIS, VENIT APUD EDITOREM,<hi>IN VIA DICTA</hi>D'AMBOISE, PRE&#768;S LA BARRIE&#768;RE D'ENFER, OU PETIT-MONTROUGE.</imprint>
                    <date>1845.</date>
                </pubcitn>
            </biblio>
        </div1>
    </div0>
""", et.HTMLParser(remove_blank_text=True))

acta_input_data = et.fromstring("""
    <vlgroup>
        <div0>
            <comhd0>
                <idref>Z000068317</idref>
                <voltitle>Jan. I</voltitle>
                <attbytes>12901Kb</attbytes>
            </comhd0>
            <div1>
                <header>
                    <comhd1>
                        <idref>Z100068318</idref>Bibliographic Details
                        <attbytes>1Kb</attbytes>
                    </comhd1>
                    <file>
                        <citn>
                            <pubtitle>Jan. I</pubtitle>
                            <city>Cambridge</city>
                            <pubdate>1999</pubdate>
                            <publ>Chadwyck-Healey</publ>
                            <series>Acta Sanctorum Full-Text Database</series>
                            <copyrite>Copyright &#169; 1999-2002 ProQuest Information and Learning Company. Do not export or print from this database without checking the Copyright Conditions to see what is permitted.</copyrite>
                        </citn>
                    </file>
                    <source>
                        <citn>
                            <editor>
                                <name>Ioannes Bollandus</name>
                                <nameinv>Bollandus, Ioannes</nameinv>
                            </editor>
                            <editor>
                                <name>Godefridus Henschenius</name>
                                <nameinv>Henschenius, Godefridus</nameinv>
                            </editor>
                            <pubtitle>Acta Sanctorum Quotquot toto orbe coluntur, vel a Catholicis Scriptoribus celebrantur, Qu&#230; ex Latinis & Gr&#230;cis, aliarumque gentium antiquis monumentis collegit, digessit, Notis illustrauit Ioannes Bollandus Societatis Iesu Theologus, Seruata primigenia Scriptorum phrasi. Operam et Studium Contulit Godefridus Henschenius Eiusdem Societ. Theologus. Prodit nunc duobus Tomis Ianuarius, In quo MCLXX. nominatorum Sanctorum, & aliorum innumerabilium memoria, vel res gest&#230; illustrantur. Ceteri menses ex ordine subsequentur</pubtitle>
                            <city>Antwerp</city>
                            <publ>Ioannes Meursius</publ>
                            <pubdate>1643</pubdate>
                            <desc>lxii, [22], 1122, [90] p.</desc>
                        </citn>
                    </source>
                    <acc.no>ASA01</acc.no>
                </header>
            </div1>
        </div0>
    </vlgroup>
    """, et.HTMLParser(remove_blank_text=True))


def test_build_acta_tracs_object():
    actual = tracs_records.build_tracs_object(acta_input_data, 'acta')
    assert actual.cbl_id == ""
    assert actual.pubid == "acta-Z000068317"
    assert actual.author == ""
    assert actual.pubtitle.startswith("Acta Sanctorum Quotquot toto orbe coluntur")
    assert actual.pubsubtitle == ""
    assert actual.editors == "Ioannes Bollandus|Godefridus Henschenius"
    assert actual.isbn == ""
    assert actual.publpubdate == ""
    assert actual.placepub == "Antwerp"
    assert actual.countrypub == "Belgium"
    assert actual.imprint == "Ioannes Meursius, for the Society of Bollandists"
    assert actual.publbranding == ""
    assert actual.collection == "Acta Sanctorum"
    assert actual.prd_id == ""
    assert actual.pubdate == ""
    assert actual.pagination == "lxii, [22], 1122, [90] p."
    assert actual.rightsformats == "citation|Text|InlineImages|pinkyInlineImage|thumb"
    assert actual.language == "Latin|Greek|Hebrew"
    assert actual.restrictions == ""
    assert actual.primarycontent == ""
    assert actual.contentsource == "CH Misc"
    assert actual.contentmodel == "CM_LION_PRIMARY_WORK"
    assert actual.sourcetype == "Books"
    assert actual.browsetype == "NPC_BookMongraph"
    assert actual.openlayer == ""


def test_build_pld_tracs_object():
    actual = tracs_records.build_tracs_object(pld_input_data, "pld")
    assert actual.cbl_id == ""
    assert actual.pubid == "pld-Z000067587"
    assert actual.author == "S. HIERONYMI"
    assert actual.pubtitle.startswith("Patrologiae Cursus Completus")
    assert actual.pubsubtitle == ""
    assert actual.editors == ""
    assert actual.isbn == ""
    assert actual.publpubdate == ""
    assert actual.placepub == ""
    assert actual.countrypub == "France"
    assert actual.imprint.startswith("PARISIIS, VENIT APUD EDITOREM")
    assert actual.publbranding == ""
    assert actual.collection == "Patrologia Latina Database"
    assert actual.prd_id == ""
    assert actual.pubdate == ""
    assert actual.pagination == ""
    assert actual.rightsformats == "citation|Text|InlineImages|pinkyInlineImage|thumb"
    assert actual.language == "Latin|Greek|Hebrew"
    assert actual.restrictions == ""
    assert actual.primarycontent == ""
    assert actual.contentsource == "CH Misc"
    assert actual.contentmodel == "CM_LION_PRIMARY_WORK"
    assert actual.sourcetype == "Books"
    assert actual.browsetype == "NPC_BookMongraph"
    assert actual.openlayer == ""


def test_create_output_headers():
    output_headers = tracs_records.create_output_headers()
    assert output_headers == """CBL_ID\tLegacy PubID\tAuthor\tPublication Title\tPublication Sub Title\tEditor\tISBN\tPublished Pubdate. Notes\tPlace of Publication\tCountry of Publication\tImprint\tPublisher Branding\tCollection\tPRD_ID\tPubdate\tPagination\tRights/Formats\tLanguage\tRestrictions\tPrimary Content Owner\tContent Source\tContent Model Type\tSource Type\tBrowseType\tOpen Layer Status\n"""


def test_main(sample_cvt_indir, output_dir):
    args = namedtuple('args', 'input_dir output_dir product')
    sample_args = args(
        input_dir=str(sample_cvt_indir),
        output_dir=str(output_dir),
        product="acta"
    )
    tracs_records.main(sample_args)
    assert "tracs_output.txt" in os.listdir(output_dir)


def test_output_file_has_headers(sample_cvt_indir, output_dir):
    args = namedtuple('args', 'input_dir output_dir product')
    sample_args = args(
        input_dir=str(sample_cvt_indir),
        output_dir=str(output_dir),
        product="acta"
    )
    tracs_records.main(sample_args)
    assert os.path.isfile(os.path.join(output_dir, "tracs_output.txt"))
    with open(os.path.join(output_dir, "tracs_output.txt"), 'r') as testreadout:
        assert testreadout.readlines()[0].startswith("CBL_ID")


def test_create_tracs_entry_from_tracs_object():
    input_object = tracs_records.build_tracs_object(acta_input_data, "acta")
    actual = tracs_records.create_tracs_entry_from_tracs_object(input_object)
    assert "\tActa Sanctorum\t" in actual
