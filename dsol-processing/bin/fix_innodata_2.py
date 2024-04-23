import os, re
import pickle
import site
site.addsitedir('/packages/dsol/lib/python2.7/site-packages')
site.addsitedir('/packages/dsol/lib/python')
from bs4 import BeautifulSoup
import lxml.etree as etree
import StringIO
import pprint
import shutil

# current master pickle cache
db = '/dc/dsol/steadystate/innodata_bkp/cache_20150123/iimp'

# location of crawled innodata source htm files
raw = '/products/impa/build/iimp/crawl/'

# output location for fixed cache
new = '/dc/dsol/steadystate/innodata_fixed/cache/iimp'


i = 0
try:
    for root, dirs, files in os.walk(db):
        for f in files:
            if f == 'fulltext.pickle':
                # create output directories
                root_splt = root.split('/')
                sub_path_1 = os.path.join(new, root_splt[7])
                if not os.path.isdir(sub_path_1):
                    os.mkdir(sub_path_1)
                sub_path_2 = os.path.join(sub_path_1, root_splt[8])
                if not os.path.isdir(sub_path_2):
                    os.mkdir(sub_path_2)
                sub_path_3 = os.path.join(sub_path_2, root_splt[9])
                if not os.path.isdir(sub_path_3):
                    os.mkdir(sub_path_3)
 
                outfilename = os.path.join(sub_path_3, f)
                pickle_filename = os.path.join(root, f)
                html_file_name = '%s%s/%s/%s/%s.htm' % (raw, root_splt[-3], root_splt[-2], root_splt[-1], root_splt[-1])

                # process the html
                try:
                    html_file = open(html_file_name, 'r').read()
                    html_file = re.sub('<[Mm][Ee][Tt][Aa].*?>', '', html_file)
                    html_file = re.sub('<[Bb][Aa][Ss][Ee][Ff][Oo][Nn][Tt].*?>', '', html_file)
                    html_file = re.sub('</[Bb][Aa][Ss][Ee][Ff][Oo][Nn][Tt]>', '', html_file)
                    html_file = re.sub('<[Bb][Ll][Oo][Cc][Kk][Qq][Uu][Oo][Tt][Ee].*?>', '', html_file)
                    html_file = re.sub('</[Bb][Ll][Oo][Cc][Kk][Qq][Uu][Oo][Tt][Ee]>', '', html_file)
                    html_file = re.sub('<[Bb][Rr] [Cc].*?>', '', html_file)
                    html_file = re.sub('<[Ff][Oo][Nn][Tt] .*?>', '', html_file)
                    html_file = re.sub('</[Ff][Oo][Nn][Tt]>', '', html_file)
                    html_file = re.sub('<[Aa] .*?>', '', html_file)
                    html_file = re.sub('</[Aa]>', '', html_file)
                    html_file = re.sub('<IMG SRC="/images/ch/iimpft/images/top.gif" .*?>', '', html_file)
                    html_file = html_file.replace('<H3>END</H3>', '')
                    html_file = html_file.replace('</CENTER>', '')
                    html_file = html_file.replace('<CENTER>', '')
                    html_file = re.sub('<[Hh][Tt][Mm][Ll]>', '', html_file)
                    html_file = re.sub('</[Hh][Tt][Mm][Ll]>', '', html_file)
                    html_file = re.sub('<[Hh][Ee][Aa][Dd]>', '', html_file)
                    html_file = re.sub('</[Hh][Ee][Aa][Dd]>', '', html_file)
                    html_file = re.sub('</[Bb][Oo][Dd][Yy]>', '', html_file)
                    html_file = re.sub('&COPY;', '&#169;', html_file)
                    html_file = re.sub('&copy;', '&#169;', html_file)
                    # Removing links - is this required? Not knowing what characters
                    # can follow may wreak some havoc...
                    html_file = re.sub('\(?www.*?[ \)]', '', html_file)
                    charset = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144, 145, 146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 160]
                    for char in charset:
                        try:
                            html_file = html_file.replace(unichr(char), '')
                        except UnicodeDecodeError:
                            html_file = html_file.replace(chr(char), '')

                    new_soup = BeautifulSoup(html_file)
                    # check the html is valid.
                    bsoup = new_soup.prettify()
                    utf_soup = bsoup.encode('utf-8')
                    xml = StringIO.StringIO(bsoup)
                    

                    try:
                        record = etree.parse(xml)
                        # unpickle here
                        pickle_contents = open(pickle_filename, 'r')
                        data = pickle.load(pickle_contents)
                        old_soup = BeautifulSoup(data['fullText']['value'])
                        old_objects = old_soup.find_all('object')
                        new_images = new_soup.find_all('img')
                        
                        outfile = open(outfilename, 'w')
                        if len(new_images) > 0:
                            #Nasty hack here in order to get python to match crawl img tags against
                            #utf_soup when they contain single quotes
                            utf_soup_hacked = utf_soup.replace("'", "<SINGLEQUOTE12345>")
                            for j, img in enumerate(new_images):
                                try:
                                    img_string_hacked = str(new_images[j]).replace("'", "<SINGLEQUOTE12345>")
                                    utf_soup_hacked = utf_soup_hacked.replace(img_string_hacked, str(old_objects[j]))
                                except IndexError:
                                    print 'images do not match in source and pickle %s' % html_file_name
                                utf_soup = utf_soup_hacked.replace("<SINGLEQUOTE12345>", "'")
                                utf_soup = utf_soup.replace('\'\'', '"')
                                utf_soup = utf_soup.replace('\'', '\'')
                                utf_soup = utf_soup.replace('\n', '')
                            data['fullText']['value'] = utf_soup
                            pickle.dump(data, outfile)
                            i = i + 1
                        else:
                            # no images - swap the bad html for the good and save the file
                            data['fullText']['value'] = bsoup
                            pickle.dump(data, outfile)
                            i = i + 1

                    except etree.XMLSyntaxError:
                        # cannot parse the source material, use the old pickle
                        print 'could not parse %s' % html_file_name
                        shutil.copy(pickle_filename, outfilename)
                        i = i + 1
                except IOError:
                    print '%s does not exist' % html_file_name
                    shutil.copy(pickle_filename, outfilename)
    print i


except KeyboardInterrupt:
    print ''
    exit(1)
