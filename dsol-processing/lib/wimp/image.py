import os

class Image(object):
    def __init__(self, name, xml, namespaces):
        self.name = name
        # The XML fragment from the manifest file.
        self.xml = xml
        self.namespaces = namespaces
        self.suffix = os.path.splitext(self.name)[-1][1:]

    def name_as(self, sufx):
        return self.name.replace(self.suffix, sufx)

    @property
    def image_scanner(self):
        while True:
            try:
                return self._image_scanner #pylint: disable = E1101
            except AttributeError:
                setattr(
                    self, "_image_scanner",
                    self.xml.xpath(
                        './/mix:scannerManufacturer',
                        namespaces=self.namespaces
                    )[0].text)

    @property
    def compression_ratio(self):
        if self.image_scanner in ['Zeutschel']:
            return '16'
        else:
            return '8'
