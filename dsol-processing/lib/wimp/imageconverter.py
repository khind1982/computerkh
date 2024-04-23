import os

import subprocess as _subp

#from extensions.osextensions import makedirsp

LOG_ROOT = "/var/tmp/wellcome/conversion_logs"

class ImageConverter(object):
    # pylint: disable = E1101
    opj_decompress = '/usr/local/bin/opj_decompress'
    opj_compress = '/usr/local/bin/opj_compress'

    def __init__(self, image):
        self.image = image
        self.image_basename = os.path.basename(self.image.name)
        self.image_book_id = '-'.join(self.image_basename.split('-')[0:4])
        self.log_path = os.path.join(LOG_ROOT, self.image_book_id)
        self.make_log_dir()

    def make_log_dir(self):
        os.makedirsp(self.log_path)

    def convert_image(self, raw_images, png_dir, jp2_dir):
        self.convert_jp2_to_png(raw_images, png_dir)
        self.convert_png_to_jp2(png_dir, jp2_dir)

    def convert_jp2_to_png(self, input_dir, output_dir):
        os.makedirsp(output_dir)
        input_file = os.path.join(input_dir, self.image.name)
        out_name = self.image.name_as('png')
        out_file = os.path.join(output_dir, out_name)
        out_logfile = self._log_file_path("jp2_to_png-stdout")
        err_logfile = self._log_file_path("jp2_to_png-stderr")
        if os.path.exists(out_file):
            return
        with open(out_logfile, 'w') as outf, open(err_logfile, 'w') as errf:
            _subp.check_call(
                [
                    self.opj_decompress,
                    '-i', input_file,
                    '-o', out_file
                ],
                stdout=outf, stderr=errf
            )

    def convert_png_to_jp2(self, input_dir, output_dir):
        os.makedirsp(output_dir)
        input_file = os.path.join(input_dir, self.image.name_as('png'))
        out_name = self.image.name
        out_file = os.path.join(output_dir, out_name)
        out_logfile = self._log_file_path("png_to_jp2-stdout")
        err_logfile = self._log_file_path("png_to_jp2-stderr")
        if os.path.exists(out_file):
            return
        with open(out_logfile, 'w') as outf, open(err_logfile, 'w') as errf:
            _subp.check_call(
                [
                    self.opj_compress,
                    '-i', input_file,
                    '-o', out_file,
                    '-t', '1024,1024',
                    '-p', 'RLCP',
                    '-r', self.image.compression_ratio
                ],
                stdout=outf, stderr=errf
            )

    def _log_file_path(self, direction):
        return os.path.join(
            self.log_path,
            "%s-%s.log" % (
                os.path.splitext(self.image_basename)[0],
                direction
            )
        )
    