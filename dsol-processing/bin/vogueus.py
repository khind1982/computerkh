"""Removes whitespace from new delivery vogue US files"""
import argparse
import os
import sys

import lxml.etree as et

import pqcoreutils.fileutils as fileutils


def parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument('indir',
        default=None)
    parser.add_argument('outdir',
        default=None)
    return parser.parse_args(args)


def main(args):
    parser = et.XMLParser(remove_blank_text=True)
    if os.path.abspath(args.indir) == os.path.abspath(args.outdir):
        print("Output directory cannot be the same as input directory")
    else:
        for f in fileutils.build_input_file_list(args.indir,
            pattern='*_final.xml'):
            with open(f'{args.outdir}/{os.path.basename(f)}', 'w') as out:
                root = et.parse(f, parser)
                out.write(et.tostring(root, pretty_print=True).decode('utf-8'))


if __name__ == '__main__':
    main(parse_args(sys.argv[1:]))