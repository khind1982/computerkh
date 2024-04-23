import optparse
import subprocess
import os

# identify -format "%x x %y" 00001t.tif

# subprocess.call(['chmod', '+x', image_processing_shell_filename])

parser = optparse.OptionParser()
parser.add_option('-t', '--type', dest="type", help='Type of query. s for single directory, m for multi directories')
parser.add_option('-i', '--indr', dest="indr", help='Input directory')
(options, args) = parser.parse_args()

if options.type is None or options.indr is None:
    parser.print_help()
    exit(1)

read_type = options.type
in_directory = options.indr

if read_type is not 'm' and read_type is not 's':
    parser.print_help()
    exit(1)


def reader(directory):
    if read_type is 's':
        for f in os.listdir(directory):
            if f.endswith('.tif'):
                yield os.path.join(in_directory, f)
    elif read_type is 'm':
        for root, dirs, files in os.walk(input_directory):
            for f in files:
                if f.endswith('.tif'):
                    yield os.path.join(root, f)

input_directory = options.indr
results = open("blah.txt", "w")
for f in reader(in_directory):
    print f
    command = '/usr/local/versions/ImageMagick-6.7.2/bin/identify -format "%%x x %%y" %s' % f
    subprocess.call(command, shell=True)
