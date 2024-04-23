import sys
import os
import argparse
import logging
import requests

from io import BytesIO

import lxml.etree as et

from pqcoreutils.fileutils import read_lookup_file

logger = logging.getLogger()

instance = {
    'dev': 'http://nightly2services.aa1.pqe/relatedids/goid/',
    'pre': 'http://preprodservices.aa1.pqe/relatedids/goid/',
    'prod': 'http://mfg.prodservices.dc4.pqe/relatedids/goid/'
}

errors = []


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '-f', dest='input_recs', required=True,
        help="The input file containing doc IDs")
    parser.add_argument(
        '-o', dest='output_file', required=True,
        help="The output file with linked IDs"
        )
    parser.add_argument(
        '-i', dest='instance', required=True,
        help="The instance for the required GOID",
        choices=['dev', 'pre', 'prod']
        )
    parser.add_argument(
        '--loglvl', dest='loglvl', help="Set the level for the logger",
        default='CRITICAL', choices=[
            'DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'])
    return parser.parse_args(args)


def fetch_goid(docid, inst):
    goid = requests.get(
        f'{instance[inst]}eebo/{docid}').text
    try:
        goid_xml = et.parse(BytesIO(goid.encode('utf-8')))
        return goid_xml.xpath('//RelatedId')[0].text
    except IndexError:
        errors.append(f"No GOID found for {docid}")


def main(args):
    logging.basicConfig(level=args.loglvl)
    with open(args.output_file, 'w') as lupfile:
        with open(
            os.path.join(os.path.dirname(
                args.output_file), 'errors.log'), 'w') as errfile:
            seen = 0
            for docid in read_lookup_file(args.input_recs):
                seen += 1
                goid = fetch_goid(docid, args.instance)
                if goid is not None:
                    lupfile.write(f'{docid}|{goid}\n')
                logger.debug(f"Processed {seen} docids...")
            for error in errors:
                errfile.write(f'{error}\n')
    logger.debug("Finished.")
# Make sure this can be used across products.
# Need to make sure product ID is recognised by the service.
# Output needs to be a lookup table.
# Sometimes products have multiple related IDs - be aware.


if __name__ == '__main__':
    main(parse_args(sys.argv[1:]))
