import multiprocessing as mp
import os

import lxml.etree as et

'''Generate DPMI files, using a multiprocessing pool to speed up
the execution.'''

# Register a default parser
et.set_default_parser(parser=et.XMLParser(remove_blank_text=True))

# Define the XSL transform at the module level so it is available to
# all child processes without needing to be passed around as a parameter.
xslt_root = et.parse('libdata/eeb/eeb-dpmi.xsl')
xsl = et.XSLT(xslt_root)

# Ensure we don't start too many processes. The multiprocessing module
# is pretty smart, actually, so this is really so we can keep track of
# number of consumers of the queued files.
NUM_JOBS = mp.cpu_count()


def main(root, destdir):
    '''Create a queue to hold the filenames to be transformed, start a process
    to walk the file system and push items onto the queue, and start a batch
    of worker processes to do the transformation and write the results.'''
    jobs = mp.Queue()
    mp.Process(target=walk, args=(root, jobs)).start()
    [mp.Process(target=transform, args=(destdir, jobs)).start()
        for i in range(NUM_JOBS)]

    jobs.close()


def transform(destdir, jobs):
    '''Take a filename from the jobs queue, transform it, and write the result.
    If the value from the queue is None, call break to exit the loop and shut
    down the process.'''
    while True:
        infile = jobs.get()
        if infile is None:
            break
        outfile = destfile(destdir, infile)
        dpmi = xsl(et.parse(infile))
        with open(outfile, 'w+b') as outf:
            outf.write(et.tostring(dpmi, pretty_print=True, encoding='utf-8'))


def walk(root, jobs):
    '''Walk the file system from the provided root, and add every file whose
    name ends in ".xml" to the jobs queue. When the walk is finished, add
    None to the queue NUM_JOBS times to signal to every worker process that
    there are no more jobs to process.'''
    for root, dirs, files in os.walk(root):
        for _file in files:
            if _file.endswith('.xml'):
                jobs.put(os.path.join(root, _file))
    else:
        for n in range(NUM_JOBS):
            jobs.put(None)


def destfile(directory, filename):
    '''Build an output file path from the given parameters.'''
    return os.path.join(
        directory, os.path.basename(
            filename.replace('.xml', '_dpmi.xml')))
