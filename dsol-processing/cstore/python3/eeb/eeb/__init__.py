'''Basic EEB transform functions that don't belong in a more
specific scope.'''

import json
import os
import sys

import lxml.etree as et

import eeb.cli as cli
import eeb.outputstream as stream
import eeb.validator as validator


# Register a default parser
et.set_default_parser(parser=et.XMLParser(remove_blank_text=True))


# Custom path builder for EEB in Singleton output mode (when -B is given).
# We want the output to be split by portions of the file name, to avoid
# ending up with huge numbers of files in a flat directory structure.
class EEBSingletonPathBuilder:
    '''Used to create the file path for use in 1-to-1 mode. Each product will
    want its own SingletonPathBuilder.'''
    def __init__(self, root_dir):
        self.root_dir = root_dir

    def __call__(self, object_id):
        # At the moment, this is absolutely NOT a default path builder - it
        # is very much geared towards EEB. However, it should be easy enough
        # to refactor once we get more data sets to handle.
        return os.path.join(self.root_dir, *object_id.split('-')[0:3],
                            '%s.xml' % object_id)


# Normalise the values in args.infiles. If an entry is a file, leave it
# as it is.  If it's a directory, expand its entry to include all XML files
# at that location.  If ids_from_file is True, treat the first value in
# infiles as a file containing paths to the target objects. In this case,
# if infiles is longer than one item, also print a warning that extra
# positional parameters are ignored.  We use `yield' to create an iterator
# generator, which allows us to start processing content much earlier than
# if we collected a full list.


def input_file_list(infiles, ids_from_file):
    if ids_from_file:
        yield from targets_from_file(infiles)
    else:
        yield from targets_from_fs_walk(infiles)


def targets_from_fs_walk(infiles):
    for i in infiles:
        if os.path.isfile(i):
            yield i
        elif os.path.isdir(i):
            for root, dirs, files in os.walk(i):
                dirs.sort()
                for f in sorted(files):
                    if f.endswith('.xml'):
                        yield os.path.join(root, f)


def targets_from_file(infiles):
    if len(infiles) > 1:
        print("Ignoring extra filenames on commandline", file=sys.stderr)
    with open(infiles[0]) as inf:
        for line in inf.readlines():
            if not line.startswith('#'):
                yield line.strip()


def find_hms_keys(book_id, hms_json, dpmi_xml):
    '''Extract from hms_json and dpmi_xml the values we need to send in
    to the template to populate the appropriate //Component/Representation
    elements. If either value is NoneType, return the empty hms_keys element.
    '''
    found = {'pft': False, 'dpmi': False, 'thumb': False}
    global hms_keys
    hms_keys = et.Element('hms-keys')
    if not all([hms_json, dpmi_xml]):
        return hms_keys
    thumb_img_path = get_thumb_from_dpmi(book_id, dpmi_xml)

    for d in hms_json:
        for i in d['objects']:
            if i['type'] == 'PFT':
                pdf_key = et.SubElement(hms_keys, 'pdf-key')
                pdf_key.text = i['retrieveKey']
                pdf_size = et.SubElement(hms_keys, 'pdf-size')
                pdf_size.text = i['size']
                found['pft'] = True
            if i['type'] == 'DPMI':
                dpmi_key = et.SubElement(hms_keys, 'dpmi-key')
                dpmi_key.text = i['retrieveKey']
                found['dpmi'] = True
            if i['type'] == 'THUM' and i['objectId'] == thumb_img_path:
                thumb_key = et.SubElement(hms_keys, 'thumb-key')
                thumb_key.text = i['retrieveKey']
                found['thumb'] = True

    return hms_keys


def get_thumb_from_dpmi(book_id, dpmi_xml):
    '''Look in the DPMI file for the Title page of the current book.'''
    try:
        # Look for the //rep with a ./tag containing "Title page"
        thumb_img = dpmi_xml.xpath(
            '//tag[contains(., "Title page")]/../rep/path[contains(., "THUM")]')[0].text  # noqa
    except IndexError:
        # Which failing, go for the first that matches the book ID and
        # contains THUM since this is the first internal page of the
        # current book, i.e. the first non-cover image.

        # Grab all the THUM images from the DPMI file and use the first
        thumb_img = sorted([i.text for i in dpmi_xml.xpath(
            f'//rep/path[contains(., "{book_id}") and contains(., "THUM")]')])[0]  # noqa

    return thumb_img.replace('+THUM', '')


def find_dpmi_file(book_id, dpmi_root_dir):
    '''Look for the DPMI file, and if found, parse it and return it.'''
    dpmi_path = os.path.join(dpmi_root_dir, '%s_dpmi.xml' % book_id)
    if os.path.isfile(dpmi_path):
        return et.parse(dpmi_path)


def find_hms_data_file(book_id, hms_json_root_dir):
    '''Look for the HMS JSON file, and if found, load and return it.'''
    hms_data_path = os.path.join(hms_json_root_dir, '%s.json' % book_id)
    if os.path.isfile(hms_data_path):
        with open(hms_data_path) as j:
            return json.load(j)


def run_transform(args):
    '''Run the transform against the files/directories passed on the command
    line, yielding each result tree to the caller.'''

    xsl_path = os.path.join(
        os.path.dirname(__file__), '../libdata/eeb', 'eeb-transform.xsl')
    xslt_root = et.parse(xsl_path)
    transform = et.XSLT(xslt_root)

    for input_file in input_file_list(args.infiles, args.ids_from_file):
        book_id = os.path.basename(input_file).replace('.xml', '')

        # Grab the DPMI data and HMS JSON, if they exist.
        dpmi_xml = find_dpmi_file(book_id, args.dpmi_dir)
        hms_json = find_hms_data_file(
            book_id, os.path.join(args.hms_json_dir, args.instance))
        if not hms_json and not args.no_json_ok:
            print("No HMS data found for %s. It will not be in the output" %
                  book_id, file=sys.stderr)
            continue
        # Find the HMS key data for the current book. This will either be
        # an lxml container containing information about the discovered keys,
        # or an empty lxml element.
        global hms_keys
        hms_keys = find_hms_keys(book_id, hms_json, dpmi_xml)

        # Parse the input file into an lxml Element Tree
        doc = et.parse(input_file)

        # Since the product code is a string, it needs to be quoted properly,
        # or it won't be seen by the template. There are (at least) two ways to
        # do this:
        # "'%s'" % args.product
        # et.XSLT.strparam(args.product)
        # I prefer the latter.
        product = et.XSLT.strparam(args.product)
        try:
            yield ((input_file, book_id), transform(
                doc, ProdCode=product, MinVer=str(args.minor_version)))
        except et.XSLTApplyError as err:
            handle_error(transform, err)


def handle_error(transform, exception):
    # TODO make this handle dev and production usage. For dev, print the error
    # on the terminal and end. In production, log an error and add an item to
    # an application message handler, as in the GS4 transform monster.
    print("XSLT Error log follows", file=sys.stderr)
    print(exception, file=sys.stderr)
    print(transform.error_log, file=sys.stderr)
    sys.exit(1)


def main(*argv):
    '''Process the received list of args, build the product-specific
    config template, load and prepare the transform, then process the
    list of input files.'''
    args = cli.parse_args()

    product = args.product

    # call define_hmsKeys so that pqfn:hmsKeys() is available from the
    # stylesheet.
    define_hmsKeys(args)

    if not args.bundled_output:
        path_builder = EEBSingletonPathBuilder(args.output_dir)
    else:
        path_builder = None

    # Get an instance of OutputStreamHandler so we have some way of
    # writing our cunningly crafted Ingest Schema format docs.
    outputhandler = stream.OutputStreamHandler(
        root_dir=args.output_dir,
        path_builder=path_builder,
        bundled_output=args.bundled_output, product=product,
        records=args.count)

    xmlvalidator = validator.IngestSchemaValidator(
        args.schema_path, args.minor_version)
    # Each document transformed will be yielded from the run_transform
    # function, so we can then validate it against the schema, and decide
    # where to send it.
    validation_failures = []
    seen = 0
    transformed = 0
    for (book_file, book_id), result_tree in run_transform(args):
        # Validate the document against the schema. It's probably enough to
        # use the most recent version, and not worry about picking a specific
        # version.
        seen += 1
        if args.validate_output:
            try:
                xmlvalidator.validate(result_tree, (book_file, book_id))
                transformed += 1
            except et.DocumentInvalid as exc:
                validation_failures.append((book_id, book_file, exc))
                continue
        else:
            transformed += 1

        # If we get here, we know the transformed doc is good, and should
        # be saved.
        outputhandler.write_output(result_tree, book_id)
        if args.progress:
            sys.stderr.buffer.write(
                b"\033[1000D\033[KSeen: \033[92m%s\033[0m  transformed: \033[91m%s\033[0m  (\033[96m%s\033[0m)" % (bytes(str(seen), 'utf-8'), bytes(str(transformed), 'utf-8'), bytes(book_id, 'utf-8')))  # noqa

    if args.progress:
        print('\n', file=sys.stderr)

    if validation_failures:
        print("The following validation errors were encountered.", file=sys.stderr)  # noqa
        print("Affected titles are NOT included in the output", file=sys.stderr)  # noqa
        print("-----------------", file=sys.stderr)
        for book_id, src_file, error in validation_failures:
            print(book_id, file=sys.stderr)
            print(src_file, file=sys.stderr)
            print(error, file=sys.stderr)
            print("-----------------", file=sys.stderr)
        print("Total %s failed transformations" % len(validation_failures),
              file=sys.stderr)


#  Custom XPath functions
# Create a namespace for custom functions
ns = et.FunctionNamespace('http://local/functions')
ns.prefix = 'pqfn'


@ns
def fixDate(context, dateString):
    if dateString[0].text.endswith('00'):
        return dateString[0].text[0:4] + '01'
    return dateString[0].text


# These are the values that need to appear in ObjectBundleData
# elements to aid PQIS with the GeoIP version of the product.
geoip_codes = {
        'kbd': 'EEBKBDK',
        'wel': 'EEBWellcomeTrust',
        'bnc': 'EEBBNCF',
        'kbn': 'EEBKBNL',
        }


@ns
def geoipCode(context, library):
    return geoip_codes.get(library[0])


# define the hmsKeys XPath function as a closure. We need
# access to the args collection (specifically, the target instance,
# in order to build the paths for the HMS JSON files), which we can't
# get from libxml as a parameter to the function pqfn:hmsKeys when it
# is called from the template.
def define_hmsKeys(args):
    def hmsKeys(context, book_id):
        # We receive book_id as a list.
        book_id = book_id[0]
        dpmi_xml = find_dpmi_file(book_id, args.dpmi_dir)
        hms_json = find_hms_data_file(
            book_id, os.path.join(args.hms_json_dir, args.instance))
        if not hms_json and not args.no_json_ok:
            print("No HMS data found for %s. It will not be in the output" %
                  book_id, file=sys.stderr)

        return find_hms_keys(book_id, hms_json, dpmi_xml)
    this_module = sys.modules[__name__]
    setattr(this_module, "hmsKeys", ns(hmsKeys))


@ns
def primaryContributors(context, nodelist):
    primary_contrib = primary_contrib_entry(nodelist)

    results = et.Element('results')
    results.append(primary_contrib)

    return results


@ns
def secondaryContributors(context, nodelist):
    secondary_contrib = secondary_contrib_entry(nodelist)

    results = et.Element('results')
    for result in secondary_contrib:
        results.append(
            build_result_element(result, './aut_other_cerl_variant'))
    return results


def primary_contrib_entry(nodelist):
    """Given :nodelist: extract elements relating to the primary
    contributor and associated CERL variant values. Deduplicate
    CERL values and construct a resultset to return to the template"""
    primary_main = [elem for elem in nodelist if elem.tag == 'author_main'][0]
    try:
        primary_variants = [elem for elem in nodelist
                            if elem.tag == 'aut_cerl'][0]
    except IndexError:
        primary_variants = None
    return build_result_element(
        (primary_main, primary_variants), './aut_cerl_variant')


def build_result_element(elements, var_xpath):
    """Receives element tree tuple and xpath of CERL variants.
    Returns an element tree whose root element is <result>"""
    main_elem, variant_elem = elements
    result = et.Element('result')
    main = et.SubElement(result, 'main')
    main.text = main_elem.xpath('./author_corrected')[0].text

    if main_elem.xpath('author_viaf'):
        viaf = et.SubElement(result, 'viaf')
        viaf.text = main_elem.xpath('author_viaf')[0].text

    if main_elem.xpath('lionid'):
        lion = et.SubElement(result, 'lionid')
        lion.text = main_elem.xpath('lionid')[0].text

    variants = et.SubElement(result, 'variants')
    if variant_elem is not None:
        variants_deduped = sorted(
            set([node.text.strip() for node
                in variant_elem.xpath(var_xpath)
                if node.text is not None]))
        for cerl_ref in variants_deduped:
            variant = et.SubElement(variants, 'variant')
            variant.text = cerl_ref
    else:
        variants_deduped = []
    return result


def secondary_contrib_entry(nodelist):
    """Given nodelist, split the nodelist into two lists which match
    the tag in the parent element.  Pass these into match_groups and return
    the results."""
    secondary_main = [elem for elem in nodelist if elem.tag == 'author_other']
    secondary_variants = [
        elem for elem in nodelist if elem.tag == 'aut_other_cerl']

    return match_groups(secondary_main, secondary_variants)


def match_groups(main_elems, variant_elems):
    """Given two lists of elements, iterate over the list of authors
    and find the corresponding CERL variants for that author.
    Return them as a tuple. If any of the authors
    have no CERL variants, return the tuple with a nonetype."""

    checklist = {}
    return_dict = {}

    for main_elem in main_elems:
        auth = main_elem.xpath("./author_corrected")[0].text
        checklist[auth] = main_elem
        for variant_elem in variant_elems:
            if check_main_for_cerls(variant_elem, auth):
                return_dict[auth] = (main_elem, variant_elem)
            else:
                continue

    for auth, main_elem in checklist.items():
        if auth in return_dict.keys():
            continue
        else:
            return_dict[auth] = (main_elem, None)

    return return_dict.values()


def check_main_for_cerls(variant_elem, auth):
    """Given the variant element and the text of a
    particular author, check whether
    the author matches any author in the list
    of CERL variants and return 'True' if
    one is found"""
    auth_set = set([auth])
    variants = set([node.text.strip() for node in variant_elem.getchildren()])
    if auth_set & variants:
        return True


# END Custom XPath functions
