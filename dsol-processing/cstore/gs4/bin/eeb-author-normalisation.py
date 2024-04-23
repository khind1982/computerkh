#!/usr/local/bin/python2.7

# Script to read in a list of author names.
# Test each author name against different conditions.
# If any one of the conditions is true, write the line to one file called 'complex-author.txt'.
# If none of the conditions are true, write the line to another file called 'simple-author.txt'.
import os
import sys
import re
import codecs
import shutil

import lxml.etree as et

class AuthorSeparator(object):

    def __init__(self):
        self.complexdict = {}
        self.simplelist = []
        self.names_with_dates = []
        self.files_and_auth_parts = {}

    def add_to_complex(self, infile, name):
        self.complexdict[infile] = name

    def add_to_simple(self, name):
        self.simplelist.append(name)

    def add_to_names_with_dates(self, name):
        self.names_with_dates.append(name)

    def build_files_auth_parts(self, fpath, authparts):
        self.files_and_auth_parts[authparts] = fpath

    def process_simple_list(self):
        return list(set(self.simplelist))

    def process_names_with_dates_list(self):
        return list(set(self.names_with_dates))


def main(args):
    try:
        indir = args[0]
        outpath = args[1]
    except:
        print "Usage: [indir] [path to your output folder]"
        exit(1)

    separator = AuthorSeparator()

    parser = et.XMLParser(remove_blank_text=True)

    if not os.path.exists(outpath):
        os.makedirs(outpath)

    num = 0

    for infile in walk_dirs(indir):
        collection = os.path.dirname(infile).split('/')[-2]
        library = os.path.dirname(infile).split('/')[-1]
        shutil.copyfile(infile, "%s.bak" % infile)
        eebxml = et.parse(infile, parser)
        num += 1
        print "Reading data in file %s...(%s read)." % (infile, num)
        main_authors = eebxml.xpath('.//author_main')
        other_authors = eebxml.xpath('.//author_other')
        main_auth_parts = process_author_name_elements(infile, main_authors, separator)
        other_auth_parts = process_author_name_elements(infile, other_authors, separator)
        if len(main_auth_parts) > 0:
            separator.build_files_auth_parts(infile, main_auth_parts[0])
        if len(other_auth_parts) > 0:
            for other_auth in other_auth_parts:
                separator.build_files_auth_parts(infile, other_auth)
        if len(main_auth_parts) == 0 and len(other_auth_parts) == 0:
            collection = os.path.dirname(infile).split('/')[-2]
            library = os.path.dirname(infile).split('/')[-1]
            outfpath = os.path.join(outpath, collection, library)
            if not os.path.exists(outfpath):
                os.makedirs(outfpath)
            outfilepath = os.path.join(outfpath, os.path.basename(infile))
            write_to_output(outfilepath, eebxml)


    print "Writing new field information to output files..."
    with codecs.open('%s/complex-author-list.txt' % (outpath), 'w', encoding='utf8') as complexoutput:
        for infile, auth in separator.complexdict.items():
            complexoutput.write('%s\t%s\n' % (auth, infile))
    with codecs.open('%s/simple-author.txt' % (outpath), 'w', encoding='utf8') as simpleoutput:
        simplist = separator.process_simple_list()
        for simpauth in simplist:
            simpleoutput.write('%s\n' % simpauth)
    with codecs.open('%s/date-author.txt' % (outpath), 'w', encoding='utf8') as dateoutput:
        datelist = separator.process_names_with_dates_list()
        for dateauth in datelist:
            dateoutput.write('%s\n' % dateauth)

    #     datelist = separator.process_names_with_dates_list()
    #     for dateauth in datelist:
    #         dateoutput.write('%s\n' % dateauth)

    # To create the custom implementation in individual files
    # Iterate over files_and_auth_parts {path to file: [(file tuple), (file tuple)]}
    # For each filepath and list, pass the filepath and list to a new function
    # The function will put the new elements in the data
    # Sub-functions will iterate over each list and return the custom Xpath

    for authbundle, fpath in separator.files_and_auth_parts.items():
        xmldata = add_custom_author_field(fpath, authbundle, parser)
        collection = os.path.dirname(fpath).split('/')[-2]
        library = os.path.dirname(fpath).split('/')[-1]
        outfpath = os.path.join(outpath, collection, library)
        if not os.path.exists(outfpath):
            os.makedirs(outfpath)
        outfilepath = os.path.join(outfpath, os.path.basename(fpath))
        write_to_output(outfilepath, xmldata)
    print "Finished.  Written new field information in files."


def process_author_name_elements(infile, authors, separator):
    auth_parts = []
    for main_auth_etree in authors:
        author_name = main_auth_etree.xpath('./author_corrected')[0].text
        if process_name_string(infile, author_name, separator):
            birth_date, death_date = process_name_string(infile, author_name, separator)
            auth_parts.append((main_auth_etree, birth_date, death_date))
    # for other_auth_etree in authors:
    #     author_name = other_auth_etree.xpath('//author_corrected')[0].text
    #     if process_name_string(author_name, separator):
    #         birth_date, death_date = process_name_string(author_name, separator)
    #         auth_parts.append((other_auth_etree, birth_date, death_date))
    return auth_parts


def walk_dirs(indir):
    for root, dirs, files in os.walk(indir):
        for f in files:
            if f.endswith('.xml'):
                yield os.path.join(root, f)


def process_name_string(infile, author_name, separator):
    if len(author_name.split(', ')) == 3:
        if parse_complex_name(author_name, separator):
            separator.add_to_names_with_dates(author_name)
            return parse_complex_name(author_name, separator)
        else:
            separator.add_to_complex(infile, author_name)
    elif len(author_name.split(', ')) > 3:
        separator.add_to_complex(infile, author_name)
    elif len(author_name.split(', ')) == 2:
        return check_two_part_names(infile, author_name, separator)
    else:
        separator.add_to_simple(author_name)


def check_two_part_names(infile, author_name, separator):
    if check_name_length(author_name):
        separator.add_to_simple(author_name)
    else:
        if parse_complex_name(author_name, separator):
            separator.add_to_names_with_dates(author_name)
            return parse_complex_name
        else:
            separator.add_to_complex(infile, author_name)


def parse_complex_name(author_name, separator):
    # numlist = ['0', '1', '2', '3', '4',
    # '5', '6', '7', '8', '9']
    if check_name_length(author_name):
        end_chunk = author_name.split(', ')[-1]
        if len(end_chunk.split('-')) > 1:
            if parse_death_date(end_chunk):
                death_date = end_chunk.split('-')[-1]
            else:
                death_date = ''
            if parse_birth_date(end_chunk):
                birth_date = end_chunk.split('-')[0]
            else:
                birth_date = ''
        elif len(end_chunk.split('-')) == 1:
            death_date, birth_date = parse_single_dates(end_chunk)
        return birth_date, death_date
    else:
        return False


def parse_single_dates(end_chunk):
    if re.search(r".*[0-9]{1,}", end_chunk):
        birth_date = end_chunk
        death_date = ''
    else:
        birth_date = ''
        death_date = ''
    return death_date, birth_date


def check_name_length(author_name):
    last_name_chunk = author_name.split(', ')[0]
    first_name_chunk = author_name.split(', ')[1]
    if len(last_name_chunk.split(' ')) > 1 and len(first_name_chunk.split(' ')) > 1:
        return False
    elif len(last_name_chunk.split(' ')) > 3:
        return False
    elif len(first_name_chunk.split(' ')) > 2:
        return False
    elif re.search(r".*[0-9]{2,}", first_name_chunk):
        return False
    # elif "Pope" or "Saint" in first_name_chunk:
    #     return False
    else:
        return True


def parse_death_date(end_chunk):
    if re.search(r".*[0-9]{2,}", end_chunk.split('-')[-1]):
        return True


def parse_birth_date(end_chunk):
    if re.search(r".*[0-9]{2,}", end_chunk.split('-')[0]):
        return True


def date_test(author_name, separator):
    pass


def add_custom_author_field(filepath, auth, xmlparser):
    xmldata = et.parse(filepath, xmlparser)
    updated_author_element = create_custom_author(auth)
    return updated_author_element.getroottree()

def create_custom_author(authparts):
    authetree, birth_date, death_date = authparts
    authname = et.tostring(authetree.xpath('./author_corrected')[0]).split('<author_corrected>')[1].split('</author_corrected')[0]
    lastnames = authname.split(', ')[0]
    firstnames = authname.split(', ')[1]

    # This code has been added to strip
    # Existing normalisation elements
    # From the data before adding updates
    if authetree.xpath('./DoNotNormalize'):
        for elem in authetree.xpath('./DoNotNormalize'):
            et.strip_elements(authetree, 'DoNotNormalize')
    if authetree.xpath('./last_name'):
        for elem in authetree.xpath('./last_name'):
            et.strip_elements(authetree, 'last_name')
    if authetree.xpath('./first_name'):
        for elem in authetree.xpath('./first_name'):
            et.strip_elements(authetree, 'first_name')
    if authetree.xpath('./birth_date'):
        for elem in authetree.xpath('./birth_date'):
            et.strip_elements(authetree, 'birth_date')
    if authetree.xpath('./death_date'):
        for elem in authetree.xpath('./death_date'):
            et.strip_elements(authetree, 'death_date')


    normalize = et.SubElement(authetree, 'DoNotNormalize')
    normalize.text = "Y"
    if lastnames:
        lastname_element = et.SubElement(authetree, 'last_name')
        lastname_element.text = lastnames
    if firstnames:
        firstname_element = et.SubElement(authetree, 'first_name')
        firstname_element.text = firstnames
    if birth_date:
        birthdate_element = et.SubElement(authetree, 'birth_date')
        birthdate_element.text = birth_date
    if death_date:
        deathdate_element = et.SubElement(authetree, 'death_date')
        deathdate_element.text = death_date
    return authetree


def write_to_output(outfpath, xmldata):
    with open(outfpath, 'w') as writefile:
        writefile.write(et.tostring(xmldata, pretty_print=True, xml_declaration=True, encoding="UTF-8"))

if __name__ == '__main__':
    main(sys.argv[1:])
