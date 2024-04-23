import os
import sys
import re
import optparse
import shutil
import subprocess
import lxml.etree as etree
from PIL import Image
sys.path.insert(0, "/packages/dsol/lib/python")

parser = optparse.OptionParser()
parser.add_option('-i', '--indr', dest="indr", help='Input directory')
(options, args) = parser.parse_args()

if options.indr is None:
    parser.print_help()
    exit(1)

input_directory = options.indr

# input_directory = '/dc/theses/01-IN'
viewer_directory = '/opt/DSol/apache2/htdocs/theses/viewer/viewer'

out = open('/opt/DSol/apache2/htdocs/theses/viewer/viewer/files.txt', 'w')
k = 0
view_files = {}
try:
    for root, dirs, files in os.walk(input_directory):
        for f in files:
            if not root.endswith('convert'):
                if f.endswith('.xml'):
                    view_files[os.path.join(root, f).rsplit('/', 1)[1].split('.')[0]] = os.path.join(root, f)
                    paths = root.split('01-IN')[1].split('/')
                    prev_path = ''
                    for sub in paths:
                        if sub is not '':
                            prev_path = '%s/%s' % (prev_path, sub)
                            make_directory = '%s/%s' % (viewer_directory, prev_path)
                            make_directory = make_directory.replace('//', '/')
                            if not os.path.exists(make_directory):
                                os.mkdir(make_directory)
                                os.chmod(make_directory, 0775)

                    directory = '/dc/theses/01-IN%s' % prev_path

                    i = 0
                    while i < 10:
                        i = i + 1
                        tiff = '%s/%05d.tif' % (directory, i)
                        jpeg = '%s/%05d.jpg' % (make_directory, i)
                        # print jpeg
                        if not os.path.isfile(tiff):
                            tiff = '%s/%05dt.tif' % (directory, i)
                        # print tiff
                        command = '/usr/local/versions/ImageMagick-6.4.5/bin/convert %s %s' % (tiff, jpeg)
                        subprocess.call(command, shell=True)
                        os.chmod(jpeg, 0775)
                        if i is 1:
                            print tiff
    for key in sorted(view_files):
        line = "%s|%s\n" % (view_files[key], key)
        out.write(line)
        out.close()

except KeyboardInterrupt:
    for key in sorted(view_files):
        line = "%s|%s\n" % (view_files[key], key)
        out.write(line)
        out.close()
    exit(1)


.carousel-control.left {
  background-image: -webkit-linear-gradient(left, rgba(0, 0, 0, 0.005) 0%, rgba(0, 0, 0, 0.0001) 100%);
  background-image: -o-linear-gradient(left, rgba(0, 0, 0, 0.005) 0%, rgba(0, 0, 0, 0.0001) 100%);
  background-image: linear-gradient(to right, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.0001) 100%);

.carousel-control.right {
  background-image: -webkit-linear-gradient(right, rgba(0, 0, 0, 0.005) 0%, rgba(0, 0, 0, 0.0001) 100%);
  background-image: -o-linear-gradient(right, rgba(0, 0, 0, 0.005) 0%, rgba(0, 0, 0, 0.0001) 100%);
  background-image: linear-gradient(to left, rgba(0, 0, 0, 0) 0%, rgba(0, 0, 0, 0.0001) 100%);
