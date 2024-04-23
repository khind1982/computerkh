
from lxml import etree
import os, os.path

# get index of articlekey and pageimagefilename for extract script!
# check os.makedirs in media index script - could have sworn it's not producing an error if dir already exists
# nb if article table is incomplete this will not produce files for all data
# remove section after combining with title?
# put medianum on image for consistency

# naming of things like currentimage (from sql) and currentmediaitem (from xml) could be clearer?

# list image merging commands #
# imagekeywords #
# fit the two bits together #
# turn all image level attribs into lists; split on delimiters #
# claire's tidying up steps #
# reading and writing #
# character encoding
# add in line breaks for readability
# claire's test for accuracy using page numbers


class DeepIndexMerger(object):
    
    def __init__(self):
        self.currentarticle = None
        self.setnamespaces()
        self.failedrecords = 0
        
    def setnamespaces(self):
        self.namespaces = {
                "xsi": "http://www.w3.org/2001/XMLSchema-instance",
                "pam": "http://prismstandard.org/namespaces/pam/2.0/",
                "dc": "http://purl.org/dc/elements/1.1/",
                "dcterms": "http://purl.org/dc/terms/",
                "pim": "http://prismstandard.org/namespaces/pim/2.0/",
                "prism": "http://prismstandard.org/namespaces/basic/2.0/",
                "prl": "http://prismstandard.org/namespaces/prl/2.0/",
                "pq": "http://www.proquest.co.uk",
                "cnp": "http://www.condenast.com",
                "pur": "http://prismstandard.org/namespaces/prismusagerights/2.1/"
                # what to do with xmlns="http://www.w3.org/1999/xhtml"?
                }
        #self.CNP = "{http://www.condenast.com}"
        for prefix in self.namespaces.keys():
            namespace_code = prefix.upper()
            setattr(self, namespace_code, "{%s}" % self.namespaces[prefix])
    
    """
    def settasks(self):
        # order of tasks will dictate order in which new fields get appended
        # not sure there's a more elegant/explicit way to do this
        self.tasks = [
                set_abstract,
                set_coverdisplaydate
                ]
    """
    
    def merge(self, article, inputroot, outputroot):
        article.setfilepath(inputroot, iotype="input")
        article.setfilepath(outputroot, iotype="output")
        
        self.currentarticle = article
        try:
            self.tree = etree.parse(article.inputpath)
        except IOError:
            self.failedrecords += 1
            return
        
        #if self.check_id() == False:
        #    return
        
        self.mediaset = self.tree.xpath("//pam:media", namespaces=self.namespaces)
        
        self.merge_article_level_fields()
        self.merge_image_level_fields()
        
        self.final_tidy()
        try:
            os.makedirs(os.path.dirname(article.outputpath))
        except OSError:
            pass
        with open(article.outputpath, "w") as outfile:
            self.tree.write(outfile, encoding="utf-8", xml_declaration=True)
        
    def generic_set_field(self, articleattr, xpath, alwaysreplace=False):
        # will screw up element order if any are sometimes missing
        # could try adding an insert_after parameter...
        # still be dodgy if previous element could be missing!
        text = getattr(self.currentarticle, articleattr)
        if alwaysreplace == False:
            if text == "" or None:
                return
        elemlist = self.tree.xpath(xpath, namespaces=self.namespaces)
        # was going to strip out empty elems, but this is only because of the way
        # transformation process handles specific fields, so belongs better in
        # final_tidy.
        #if text == "":
        #    for elem in elemlist:
        #        elem.getparent().remove(elem)
        if len(elemlist) == 0:
            newelem = etree.Element(self.elementnamefromxpath(xpath))
            newelem.text = text
            newelem.tail = "\n"
            print " ".join(["creating a new", newelem.tag, "in", self.currentarticle.articlenumber])
            insert_after = self.tree.xpath("//prism:copyright", namespaces=self.namespaces)
            insertion_index = insert_after[-1].getparent().index(insert_after[-1]) + 1
            insert_after[-1].getparent().insert(insertion_index, newelem)
        elif len(elemlist) == 1:
            elemlist[0].text = text
        else:
            print " ".join(["too many instances of", xpath, "in", self.currentarticle.articlenumber])

    def generic_set_media_field(self, imageattr, xpath, alwaysreplace=True):
        # as with article level, will screw up element order if any are sometimes missing
        textlist = getattr(self.currentimage, imageattr)
        if alwaysreplace == False:
            if len(textlist) == 0:
                return
        elemlist = self.currentmediaitem.xpath(xpath, namespaces=self.namespaces)
        if len(elemlist) > 1:
            print " ".join(["too many instances of", xpath, "in", self.currentarticle.articlenumber])
            return
        elif len(elemlist) == 0:
            last_media_ref_elem = self.currentmediaitem.xpath("pam:mediaReference", namespaces=self.namespaces)[-1]
            insertion_index = self.currentmediaitem.index(last_media_ref_elem) + 1
        else:
            insertion_index = elemlist[0].getparent().index(elemlist[0])
            elemlist[0].getparent().remove(elemlist[0])
        # now cycle through list of new fields popping them in at the insertion_index            
        indexcounter = 0
        for field in getattr(self.currentimage, imageattr):
            newelem = etree.Element(self.elementnamefromxpath(xpath))
            newelem.text = field
            newelem.tail = "\n"
            self.currentmediaitem.insert(insertion_index + indexcounter, newelem)
            indexcounter += 1
    
    """
    def set_abstract(self):
        abstractelem = self.tree.xpath("//
        
    def set_coverdisplaydate(self):
        if article.coverdisplaydate != None or '':
            cddelement = self.tree.xpath("//prism:coverDisplayDate", namespaces=self.namespaces)
            cddelement.text = article.coverdisplaydate
    """

    def merge_article_level_fields(self):
        # alternatively store these in a dict
        # use a list to determine order of access
        self.generic_set_field("coverdisplaydate", "//prism:coverDisplayDate")
        self.generic_set_field("abstract", "//cnp:abstract")
        self.generic_set_field("articletitle", "//dc:title", alwaysreplace=True)
        self.generic_set_field("articlecontributor", "//dc:contributor", alwaysreplace=True)
        self.generic_set_field("section", "//prism:section", alwaysreplace=True)
        self.generic_set_field("author", "//dc:creator", alwaysreplace=True)
        #self.final_tidy()

    def merge_image_level_fields(self):
        listlocation = 1
        for mediaitem in self.mediaset:    
            if self.currentarticle.images.has_key(listlocation):
                self.currentmediaitem = mediaitem
                self.currentimage = self.currentarticle.images[listlocation]
                self.merge_media_item_fields()
            listlocation += 1
            
    def merge_media_item_fields(self):
        self.generic_set_media_field("imagekey", "cnp:imageKey", alwaysreplace=True)
        self.generic_set_media_field("caption", "pam:caption", alwaysreplace=True)
        self.generic_set_media_field("trend", "cnp:trend")
        self.generic_set_media_field("description", "pam:textDescription")
        self.generic_set_media_field("imagetags", "cnp:tags")
        self.generic_set_media_field("credit", "pam:credit", alwaysreplace=True)
        self.generic_set_media_field("imagecreator", "cnp:imageCreator")
        self.generic_set_media_field("imagepictured", "cnp:pictured")
        self.generic_set_media_field("designerbrand", "cnp:designerBrand")
        self.generic_set_media_field("designerperson", "cnp:designerPerson")
        self.generic_set_media_field("color", "cnp:color")
        self.generic_set_media_field("material", "cnp:material")
        self.set_imagekeywords()
        
    def elementnamefromxpath(self, xpath):
        fullelementname = xpath.split("/")[-1]
        prefix, elementname = fullelementname.split(":")
        url = getattr(self, prefix.upper())
        return "".join([url, elementname])
        
    def set_imagekeywords(self):
        last_media_ref_elem = self.currentmediaitem.xpath("pam:mediaReference", namespaces=self.namespaces)[-1]
        insertion_index = self.currentmediaitem.index(last_media_ref_elem) + 1
        indexcounter = 0
        for garment in self.currentimage.garments:
            categelem = etree.Element("".join([self.CNP, "imageCategory" ]))
            categnameelem = etree.Element("".join([self.CNP, "imageCategoryName"]))
            categnameelem.text = garment.imagecategory
            categelem.append(categnameelem)
            
            keywordelem = etree.Element("".join([self.CNP, "imageKeyword" ]))
            keywordnameelem = etree.Element("".join([self.CNP, "imageKeywordName"]))
            keywordnameelem.text = garment.imagekeyword
            keywordelem.append(keywordnameelem)
            
            for descriptor in garment.imagedescriptor:
                descelem = etree.Element("".join([self.CNP, "imageDescriptor"]))
                descelem.text = descriptor
                keywordelem.append(descelem)
                
            categelem.append(keywordelem)
            self.currentmediaitem.insert(insertion_index + indexcounter, categelem)
            
            indexcounter += 1

    def final_tidy(self):
        # specific tasks to prepare data for handover
        # add sections to titles
        sections = self.tree.xpath("//prism:section", namespaces=self.namespaces)
        articletitles = self.tree.xpath("//dc:title", namespaces=self.namespaces)
        if len(sections) > 0:
            if articletitles[0].text == "":
                articletitles[0].text = sections[0].text
            else:
                articletitles[0].text = ": ".join([sections[0].text, articletitles[0].text])
            sections[0].getparent().remove(sections[0])
        
        # remove any cnp:keyword elements
        keywords = self.tree.xpath("//cnp:keyword", namespaces=self.namespaces)
        for keyword in keywords:
            keyword.getparent().remove(keyword)
            
        # if creator or contributor are empty get rid of them - they choke transformation process
        unwantedelemxpaths = ["//dc:creator", "//dc:contributor"]
        for xpath in unwantedelemxpaths:
            for elem in self.tree.xpath(xpath, namespaces=self.namespaces):
                if elem.text == "":
                    elem.getparent().remove(elem)
                    
        # image indexing needs to be duplicated at article level so filter will work
        imageterms = {}
        imagexpaths = ["//cnp:imageCategoryName", "//cnp:imageKeywordName", "//cnp:imageDescriptor"]
        for xpath in imagexpaths:
            for term in self.tree.xpath(xpath, namespaces=self.namespaces):
                if term.text != "":
                    imageterms[term.text] = ""
        for term in imageterms.keys():
            newelem = etree.Element("".join([self.CNP, "keyword"]))
            newelem.text = term
            newelem.tail = '\n'
            insert_after = self.tree.xpath("//prism:copyright", namespaces=self.namespaces)
            insertion_index = insert_after[-1].getparent().index(insert_after[-1]) + 1
            insert_after[-1].getparent().insert(insertion_index, newelem)
        
        # designerbrands need to be duplicated at article level so filter will work
        brandelems = self.tree.xpath("//cnp:designerBrand", namespaces=self.namespaces)
        branddict = {}
        for brandelem in brandelems:
            if brandelem.text != "":
                branddict[brandelem.text] = ""
        for brand in branddict.keys():
            newelem = etree.Element("".join([self.PRISM, "industry"]))
            newelem.text = brand
            newelem.tail = '\n'
            insert_after = self.tree.xpath("//prism:copyright", namespaces=self.namespaces)
            insertion_index = insert_after[-1].getparent().index(insert_after[-1]) + 1
            insert_after[-1].getparent().insert(insertion_index, newelem)
    
    def check_id(self):
        """Tests to make sure that Conde Nast haven't altered the ID of the current record
        in their SQL database. If they have, this method writes the CN article key and the
        details of which fields don't match to an error list on self.
        
        14/06/12 - may not be necessary; CN seem able to provide proper ids now.
        
        """
        
        return True