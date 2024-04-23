import argparse


xsd_path = '/packages/dsol/platform/libdata/mstar/ingestschemas/5/1/'


def parse_args():
    # What do all those options and flags mean?
    argparser = argparse.ArgumentParser()

    argparser.add_argument(
        '-c', dest='count', action='store',
        default=5000, type=int,
        help='The number of records to write per file in bundled output mode')

    argparser.add_argument(
        '-d', dest='dpmi_dir', action='store',
        default='/dc/migrations/eeb/dpmi_masters/',
        help='The directory where DPMI files are located')

    argparser.add_argument(
        '-f', dest='ids_from_file', action='store_true',
        default=False, help='If given, the last argument is taken to be a file'
        'containing paths to books to transform, one ID per line.')

    argparser.add_argument(
        '-i', dest='instance', action='store',
        choices=['dev', 'pre', 'prod'],
        required=True, help='The HMS instance whose JSON files to use')

    argparser.add_argument(
        '-j', dest='hms_json_dir', action='store',
        default='/dc/dsol/migration/eeb/hms',
        help='The directory where the HMS JSON output files are located')

    argparser.add_argument(
        '-m', dest='minor_version', action='store',
        default=60, help='The minor version of the Ingest Schema to be used')

    argparser.add_argument(
        '-n', dest='no_json_ok', action='store_true',
        default=False,
        help="If given, don't fail if an HMS JSON file is not found")

    argparser.add_argument(
        '-o', dest='output_dir', action='store',
        default='/tmp/eeb-ingest', help='Directory to write the output files')

    argparser.add_argument(
        '-q', dest='progress', action='store_false',
        default=True, help='If given, suppress progress indicator')

    argparser.add_argument(
        '-s', dest='schema_path', action='store',
        default=xsd_path,
        help='The path to the directory containting the IngestSchema '
        'file to use to validate output')

    argparser.add_argument(
        '-x', dest='validate_output', action='store_false',
        default=True,
        help='Turn OFF schema validation of the output')

    argparser.add_argument(
        '-B', dest='bundled_output', action='store_false',
        default=True,
        help='Turn OFF bundled output. Each output doc will '
        ' be saved in its own file')

    argparser.add_argument('product', action='store', help='Product code')

    argparser.add_argument(
        'infiles', action='store', nargs='*',
        help='List of files to process')

    return argparser.parse_args()
