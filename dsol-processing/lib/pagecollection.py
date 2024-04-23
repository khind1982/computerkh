import os
import datetime
import lxml.etree as ET
from commonUtils.textUtils import xmlescape
from streams.etreestream import EtreeStream  # pylint:disable=F0401


class PagefileReader(object):
    def __init__(self, pagefileroot, path=None):
        self.pagefileroot = pagefileroot
        if path is None:
            self.path = '*.xml'
        else:
            self.path = path
        self.streamOpts = 'dataRoot=%s' % self.pagefileroot

    def __iter__(self):
        for _pagefile in EtreeStream(
                {'stream': self.path,
                    'streamOpts': self.streamOpts}).streamdata():
            yield _pagefile


class FileWriter(object):
    def __init__(self, pagemap, path):
        self.pagemap = pagemap
        self.path = path

    def write(self):
        self._check_path()
        with open(self.path, 'w') as outf:
            outf.write(ET.tostring(self.pagemap.xml, pretty_print=True))

    def _check_path(self):
        # If the output file path passed in to __init__() doesn't
        # exist, create it.
        if not os.path.isdir(os.path.dirname(self.path)):
            os.makedirs(os.path.dirname(self.path))


class PCGenerator(object):
    def __init__(self, output_destination):
        self.output_destination = output_destination

    @property
    def output_path(self):
        # pylint:disable=E1101
        journalid = self.pfxml.find('journalid').text
        date = self.pfxml.find('date').text
        if self.xml.tag == 'PageMap':
            filename = self.pfxml.xpath('/page')[0].attrib['id']
            which = 'pagemap'
        elif self.xml.tag == 'mindex':
            filename = self.pfxml.find('pcid').text
            which = 'pcmi'
        return os.path.join(
                self.output_destination, journalid, date,
                'xml/%s/%s.xml' % (which, filename))


class PagemapGenerator(PCGenerator):
    # pylint: disable = E1101
    def __init__(self, pfxml, output_destination):
        super(self.__class__, self).__init__(output_destination)
        # The xml from the pagefile.
        self.pfxml = pfxml
        # The xml we are building for the pagemap file.
        self.xml = ET.Element('PageMap')

    def __getattr__(self, attr):
        if attr in ['product', 'journalid', 'date', 'pcid', 'pagesequence']:
            return self.pfxml.find(attr).text
        elif attr == 'zones':
            return self.pfxml.xpath('.//zone')
        else:
            print self.pfxml.find('pcid').text
            print ET.tostring(self.pfxml)
            raise AttributeError("instance has no attribute %s" % attr)

    def __str__(self):
        return ET.tostring(self.xml, pretty_print=True)

    @property
    def rescale_700(self):
        return float(self.pfxml.xpath('/page')[0].attrib['rescale700'])

    def append(self, what):
        self.xml.append(what)

    def build(self):
        ET.SubElement(self.xml, 'PcId').text = self.pcid
        ET.SubElement(self.xml, 'PageNum').text = self.pagesequence
        for zone in self.zones:
            self.append(self.build_zone(zone))

    def build_and_finalise(self):
        self.build()
        FileWriter(self, self.output_path).write()

    def build_zone(self, zone):
        coords = zone.xpath('zonecoords')[0].attrib
        _zone = ET.Element('Zone')
        ET.SubElement(_zone, 'DocId').text = zone.attrib['articleid']
        ET.SubElement(_zone, 'Title').text = xmlescape(
                zone.find('article_title').text)
        ET.SubElement(_zone, 'Blocked').text = 'false'
        for point in ['top', 'left', 'bottom', 'right']:
            _zone.append(self.coord_point(point, coords))
        return _zone

    def coord_point(self, point, coords):
        rescale = lambda n: str(int(int(n)/self.rescale_700))
        pointE = ET.Element(point.capitalize())
        try:
            pointE.text = rescale(coords[point])
        except ValueError:
            print ET.tostring(self.pfxml, pretty_print=True)
            raise

        return pointE


class PcmiGenerator(PCGenerator):
    # pylint:disable=W0201,E1101
    def __init__(self, output_destination):
        super(self.__class__, self).__init__(output_destination)
        self.pages = []

    def append_page(self, pfxml):
        self.pfxml = pfxml
        comp = ET.Element('comp', {'type': 'IP'})
        ET.SubElement(comp, 'name').text = pfxml.find('pagenumber').text
        ET.SubElement(comp, 'order').text = pfxml.find('pagesequence').text
        rep_thum = ET.SubElement(comp, 'rep', {'type': 'THUM'})
        ET.SubElement(rep_thum, 'path').text = self.thum_path
        rep_imp = ET.SubElement(comp, 'rep', {'type': 'IMP'})
        ET.SubElement(rep_imp, 'path').text = self.imp_path
        self.pages.append(comp)

    @property
    def thum_path(self):
        return self.media_path('img.jpg')

    @property
    def imp_path(self):
        return self.media_path('pagemap.xml')

    def media_path(self, which):
        product = self.pfxml.find('product').text
        if product.startswith('bp'):
            product = 'bpc'
        if product == 'eim':
            # EIMA3. product code should be eima
            product = 'eima'
        if product == 'art':
            # art is really AAA, Collection 2
            product = 'aaa'

        return '/media/ch/{product}/pc/{pcid}/page/{pagesequence}/{which}'.format(
            product=product,
            pcid=self.pfxml.find('pcid').text,
            pagesequence=self.pfxml.find('pagesequence').text,
            which=which,
            )

    def build_file(self):
        self.xml = ET.Element('mindex')
        for page in self.pages:
            self.xml.append(page)
        FileWriter(self, self.output_path).write()


class SQLScriptGenerator(object):
    def __init__(self):
        pass


class PageCollectionThreadingSQLGenerator(SQLScriptGenerator):
    def __init__(self, pfxml):
        startup_time = lambda: datetime.datetime.now().strftime(
                "%d%m%Y-%H:%M")
        super(self.__class__, self).__init__()
        self.pfxml = pfxml
        self.aid = self.pfxml.xpath('//zone')[0].attrib['articleid']
        self.page_image = self.pfxml.getroot().attrib['id']
        self.journalid = self.pfxml.find('journalid').text
        self.product = self.pfxml.find('product').text
        self.pcid = self.pfxml.find('pcid').text
        self.pagesequence = self.pfxml.find('pagesequence').text
        self.table_copy = "%s_backup_%s" % (self.product, startup_time())
        self.script = "SELECT * INTO %s FROM %s;" % (
                self.table_copy, self.product)

    @property
    def pcidpath(self):
        while True:
            try:
                return self._pcidpath
            except AttributeError:
                j = self.pcid.split('_')[0]
                y = self.pcid.split('_')[1][0:4]
                m = self.pcid.split('_')[1][4:6]
                self._pcidpath = os.path.join('/', j, y, m)

    @property
    def pcmi_path(self):
        return os.path.join(self.pcidpath, "xml/pcmi/%s.xml" % self.pcid)

    @property
    def pagemap_path(self):
        return os.path.join(
                self.pcidpath, "xml/pagemap/%s.xml" % self.page_image)

    @property
    def scaledimg_path(self):
        return (os.path.join(
            '/', self.journalid, self.pcid, "scaled/%s.jpg" % self.page_image))

    def pagemap(self):
        return (self.pcid, self.pagesequence, self.pagemap_path, "PAGEMAP")

    def pcmi(self):
        return (self.pcid, self.pcmi_path, "PCMI")

    def scaledimg(self):
        return (self.pcid, self.pagesequence,
                self.scaledimg_path, "SCALED_IMG")

    def generate_sql(self):
        pass
