#!/usr/local/bin/python2.5

''' Strip out all the FiXML gunge from the IIMP/IIPA source data '''

''' Works on a file at a time, so needs to be called in a loop from the CLI '''

import sys, os, re
for lib_path in ['/home/dbye/svn/dsol/trunk/Darkstar', 
                 '/home/dbye/lib', '/home/dbye/lib/python']:
    sys.path.append(lib_path)

import codecs

from EntityShield import *

if len(sys.argv) != 3:
    sys.stderr.write("Usage: " + os.path.basename(__file__) + " <datatype> <filename>\n")
    exit(1)
else:
    dataType = sys.argv[1]
    infile = sys.argv[2]

outputPath = os.path.join(os.path.expanduser('~'), 'xml_cleaned', dataType)
''' Make ~/xml_cleaned if it doesn't already exist. '''
if not os.path.isdir(outputPath):
    os.makedirs(outputPath)

data = [line.rstrip() for line in open(infile)]
sys.stderr.write(os.path.basename(infile) + ": Removing FiXML markup and inline full text...")
clean_data = os.path.basename(infile)
clean_data = re.match(r'(.*)\..*', clean_data).group(1) + '_cleaned.xml'
clean_data = os.path.join(outputPath, clean_data)

cleaned = []
decoder = codecs.getdecoder('latin1')
data = [decoder(line)[0] for line in data]
data = [line.encode('utf8', 'xmlcharrefreplace') for line in data]
for line in data:
    line = re.sub(u'\xb3\xc2', '', line, re.U)
    line = re.sub(r'\x04', '', line)
    cleaned.append(line)

data = cleaned

keep = []
inside = "NO"
done_so_far = [0]
for line in data:
    done_so_far[0] += 1

    ''' Strip out FiXML markup '''
    devalued = protect(re.sub(r'</?value>', '', line))
    line = re.sub(r'(<!\[CDATA\[|\]\]>)', '', devalued)
    remove = re.compile(chr(0x19) + '\)')
    line = re.sub(remove, '-', line)
    ''' This filthy hack is required to get round the existence of randomly placed
    '<' characters in the source data. I am preserving them as Unicode entrefs. '''
    bits = re.split(r'<', line)
    if len(bits) == 2:
        line = '<' + bits[1]
    elif len(bits) == 3:
        line = '<' + bits[1] + '<' + bits[-1]
    elif len(bits) >= 4:
        del(bits[0])
        bits[0] = '<' + bits[0]
        bits[-1] = '<' + bits[-1]
        line = ('&lt;').join(bits)
    if inside == 'NO':
        if re.search(r'name="body"', line):
            inside = 'YES'
        keep.append(line.rstrip())
    if inside == 'YES':
        if re.search(r'</element>', line):
           inside = 'NO'
    if done_so_far[0] % 1000 == 0:
        sys.stderr.write('.')
del(data)

sys.stderr.write('Done.\nFixing up XML...\n')
outfile = open(clean_data, 'w')
done_so_far = [0]
for line in keep:
    done_so_far[0] += 1

    if re.search(r'<element name="body">', line):
        line = '<element name="body"></element>'
    outfile.write(line + '\n')
    if done_so_far[0] % 1000 == 0:
        sys.stderr.write('.')
    
outfile.close()
sys.stderr.write('Done.\n')
