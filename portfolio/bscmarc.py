import os
import sys
import argparse
import logging
import datetime

from pymarc import MARCReader
from pymarc import MARCWriter
from pymarc import Field

from pqcoreutils.fileutils import parse_file_to_dict

goid_lookup = parse_file_to_dict(os.path.join(os.path.dirname(__file__), 'lookups/essay_prod_goids.txt'))

logger = logging.getLogger()


def change_leader_encoding(record):
    """Given input MARC record, positions 5 and 9 of leader
     field in the result is changed to 'c' and 'a' respectively."""
    new_leader_text = 'c'.join(record.leader.split(record.leader[5]))
    new_leader_text = ' a'.join(new_leader_text.split('  '))
    new_leader_text = 'i 4500'.join(new_leader_text.split('a 4500'))
    record.remove_fields(record.leader)
    record.leader = new_leader_text
    return record


def change_001_field(record):
    if record.get_fields('001')[0].value() == '16DARI':
        record.remove_fields('001')
        record.add_ordered_field(Field(tag='001', data='28DARI'))
        return record
    return record


def update_date_stamp(record):
    record.remove_fields('005')
    record.add_ordered_field(Field(tag='005', data=f"{datetime.datetime.today().strftime('%Y%m%d%H%M%S.0')}"))
    return record


def change_006_field(record):
    """Given input 006 field, change position 6 to letter 'o'"""
    record.remove_fields('006')
    record.add_ordered_field(
        Field(
            tag='006',
            data=r'm     o  d        '
        )
    )
    return record


def change_008_field(record):
    field_008_text = record.get_fields('008')[0].value()
    field_008_text = field_008_text.split('xxu')[0] + r'miu     o  d        eng d'
    record.remove_fields('008')
    record.add_ordered_field(
        Field(
            tag='008',
            data=field_008_text
        )
    )
    return record


def change_gerritsen_008_field_indicator(record):
    field_008_text = record.get_fields('008')[0].value()
    new_008_field_text = field_008_text.strip(field_008_text[-1]) + 'd'
    record.remove_fields('008')
    record.add_ordered_field(
        Field(
            tag='008',
            data=new_008_field_text
        )
    )
    return record


def change_040_field(record):
    record.remove_fields('040')
    record.add_ordered_field(
        Field(
            tag='040',
            indicators=['\\', '\\'],
            subfields=[
                'a', 'UK-CbPIL',
                'b', 'eng',
                'e', 'rda',
                'e', 'pn',
                'c', 'UK-CbPIL'
            ]
        )
    )
    return record


def separate_041_languages_gerritsen(record):
    try:
        languages = record.get_fields('041')[0].get_subfields('a')[0]
    except IndexError:
        return record
    ind1 = record.get_fields('041')[0].indicator1
    ind2 = record.get_fields('041')[0].indicator2
    langstringlength = len(languages)
    langcodelist = []
    for i in range(0, langstringlength):
        if i % 3 == 0:
            language = languages[i:i+3]
            langcodelist.append(language)
    record.remove_fields('041')
    subfieldslist = []
    for langcode in langcodelist:
        subfieldslist.append('a')
        subfieldslist.append(langcode)
    record.add_ordered_field(
        Field(
            tag='041',
            indicators=[ind1, ind2],
            subfields=subfieldslist
        )
    )
    return record


def add_043_field(record):
    record.add_ordered_field(
        Field(
            tag='043',
            indicators=['\\', '\\'],
            subfields=['a', 'n-us-mi']
        )
    )
    return record


def remove_245_h_subfield(record):
    record.get_fields('245')[0].delete_subfield('h')
    title = record.get_fields('245')[0].get_subfields('a')[0]
    record.get_fields('245')[0].delete_subfield('a')
    record.get_fields(
        '245')[0].add_subfield(
            'a', f'{title}.'
        )
    return record


def change_260_field_to_264_field(record):
    publication_year = record.get_fields('008')[0].value()[7:11]
    record.remove_fields('260')
    record.add_ordered_field(
        Field(
            tag='264',
            indicators=['\\', '\\'],
            subfields=[
                'a', 'Ann Arbor, Mich. :',
                'b', 'ProQuest LLC,',
                'c', f'{publication_year}.'
            ]
        )
    )
    return record


def add_3xx_fields(record):
    record.add_ordered_field(
        Field(
            tag='300',
            indicators=['\\', '\\'],
            subfields=['a', '1 online resource']
            )
    )
    record.add_ordered_field(
        Field(
            tag='336',
            indicators=['\\', '\\'],
            subfields=[
                'a', 'text',
                'b', 'txt',
                '2', 'rdacontent'
                ]
        )
    )
    record.add_ordered_field(
        Field(
            tag='337',
            indicators=['\\', '\\'],
            subfields=[
                'a', 'computer',
                'b', 'c',
                '2', 'rdamedia'
                ]
        )
    )
    record.add_ordered_field(
        Field(
            tag='338',
            indicators=['\\', '\\'],
            subfields=[
                'a', 'online resource',
                'b', 'cr',
                '2', 'rdacarrier'
                ]
        )
    )
    return record


def standardise_533_field(record):
    """
    =533  \\$aElectronic reproduction.$bAnn Arbor, Mich. :$cUMI,$d2000-
    $f(The Gerritsen collection of women's history online)
    $nDigital version of: The Gerritsen collection of women's history
    """
    record.remove_fields('533')
    record.add_ordered_field(
        Field(
            tag='533',
            indicators=['\\', '\\'],
            subfields=[
                'a', f"Electronic reproduction.",
                'b', f"Ann Arbor, Mich. :",
                'c', f'UMI,',
                'd', f'2000-',
                'f', f"(The Gerritsen collection of women's history online)",
                'n', f"Digital version of: The Gerritsen collection of women's history"
                ]
        )
    )
    return record


def change_copyright_statement(record):
    """Given input MARC record, change value of $a
    subfield in 540 field to
    'Copyright (c) 2021 ProQuest LLC.  All rights reserved.'"""
    try:
        record.get_fields('540')[0].delete_subfield('a')
        record.get_fields(
            '540')[0].add_subfield(
                'a', f"Copyright (c) 2021 ProQuest LLC. All rights reserved.")
    except IndexError:
        record.add_ordered_field(
            Field(
                tag='540',
                indicators=['\\', '\\'],
                subfields=['a', f"Copyright (c) 2021 ProQuest LLC. All rights reserved."]
            ))
    return record


def add_655_field(record):
    """Add a new 655 field =655  4$aElectronic books."""
    record.add_ordered_field(
        Field(
            tag='655',
            indicators=['\\', '4'],
            subfields=['a', 'Electronic books.']
        )
    )
    return record


def remove_773_field(record):
    record.remove_fields('773')
    return record


def add_pqp_link(record, goid_lookup):
    """Given input MARC record, change value of $a
    subfield in the 856 field so it includes a link
    to the PQP record for the SSBE essay."""
    goid = goid_lookup[record.get_fields('001')[0].value()]
    sfield = record.get_fields('856')[0].get_subfields('s')[0]
    record.remove_fields('856')
    record.add_ordered_field(
        Field(
            tag='856',
            indicators=['4', '0'],
            subfields=[
                '3', 'Black Studies center',
                'u', f'https://www.proquest.com/bsc/docview/{goid}',
                's', sfield
            ]
        )
    )
    return record


def modify_gerritsen_856_field(record, goid_lookup):
    """Given input MARC record
    Change value of $a subfield so it includes a link
    to thw PQP record"""
    legacy_id = record.get_fields('856')[0].get_subfields('u')[0].split(':')[-1]
    if "Gerritsen-" in legacy_id:
        legacy_id = legacy_id.split("Gerritsen-")[1]
    record.remove_fields('856')
    try:
        record.add_ordered_field(
            Field(
                tag='856',
                indicators=['\\', '\\'],
                subfields=[
                    'u', f'https://www.proquest.com/gerritsen/publication/{goid_lookup[legacy_id]}'
                ]
            )
        )
    except KeyError:
        raise KeyError
    return record


def process_ssbe_record(record, goid_lookup):
    """Given input MARC record, apply all desired
    changes to the record fields."""
    record = change_001_field(record)
    record = change_006_field(record)
    record = change_008_field(record)
    record = update_date_stamp(record)
    record = change_leader_encoding(record)
    record = change_040_field(record)
    record = add_043_field(record)
    record = remove_245_h_subfield(record)
    record = change_260_field_to_264_field(record)
    record = add_3xx_fields(record)
    record = change_copyright_statement(record)
    record = add_655_field(record)
    record = remove_773_field(record)
    record = add_pqp_link(record, goid_lookup)
    return record

def process_gerritsen_record(record, goid_lookup):
    """Given an input Gerritsen MARC record make all
    the required changes and return the modified record"""
    record = change_gerritsen_008_field_indicator(record)
    record = separate_041_languages_gerritsen(record)
    record = standardise_533_field(record)
    try:
        record = modify_gerritsen_856_field(record, goid_lookup)
    except KeyError:
        raise KeyError
    return record


def main(args):
    logging.basicConfig(level=args.loglvl)
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)
    with open(args.infile, 'rb') as inf, open(os.path.join(args.outdir, f'{os.path.basename(args.infile)}'), 'wb') as wr:
        # reader = MARCReader(inf, to_unicode=True, utf8_handling='ignore', force_utf8=True)
        reader = MARCReader(inf)
        writer = MARCWriter(wr)
        for record in reader:
            logger.debug(f"Processing record {record.get_fields('001')[0].value()}")
            # logger.debug(record.get_fields('856')[0].get_subfields())
            if args.product == "gerritsen":
                try:
                    output_record = process_gerritsen_record(record, goid_lookup)
                except KeyError:
                    logger.error(f"Record {record.get_fields('001')[0].value()} does not have a Prod GOID.  It will not be written to output.")
                    continue
            else:
                output_record = process_ssbe_record(record, goid_lookup)
            # logger.debug(output_record)
            try:
                writer.write(output_record)
            except UnicodeEncodeError:
                logger.error(output_record)
                logger.error(f"Incorrect encoding in record {record.get_fields('001')[0].value()}.  It will not appear in the output.")


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('infile', help="The legacy .mrc file")
    parser.add_argument('outdir', help="An output directory for the modified file")
    parser.add_argument('product', help="Product code", choices=['bsc', 'gerritsen'])
    parser.add_argument(
        '-ll', dest='loglvl', help="Set the level for the logger",
        default='CRITICAL', choices=[
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    return parser.parse_args()


if __name__ == "__main__":
    main(parse_args(sys.argv[1:]))
