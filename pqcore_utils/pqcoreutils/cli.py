import argparse
import os
import sys

import pqcoreutils.fileutils


def bundler_parse_args(args):
    parser = argparse.ArgumentParser()
    parser.add_argument("-p", dest="product", required=True)
    parser.add_argument("-g", dest="pattern", default="*.xml")
    parser.add_argument(
        "-r",
        dest="records",
        default=5000,
        type=int,
        help="number of records per bundle",
    )
    parser.add_argument("indir", default=None)
    parser.add_argument("outdir", default=None)
    return parser.parse_args(args)


def bundler_main():
    args = bundler_parse_args(sys.argv[1:])
    for argument in [args.indir]:
        if not os.path.isdir(argument):
            raise ValueError(f"Not a directory: {argument}")
    if not os.path.exists(args.outdir):
        os.makedirs(args.outdir)
    pqcoreutils.fileutils.concatenate_singleton_files(
        args.indir, args.outdir, args.product, args.pattern, args.records
    )


if __name__ == "__main__":  # pragma: no cover
    bundler_main()
