#!/usr/local/bin/python2.7

import codecs
import re, os, sys

authlog = codecs.open('author_errors.log', 'w', 'latin-1')
authlog.close()

class standardiser:
    
    def read_lookup(self, lookupfile):
    
        self.authors = {}
        authlog = codecs.open('author_errors.log', 'w', 'latin-1')
        autlist = codecs.open(lookupfile, 'rU', 'utf8')
        for line in autlist:
            #autline=line.decode('latin-1')
            autversions = line.strip().split('|')
            if len(autversions) != 4:
                authlog.write("".join(["Bad lookup entry: ", line, "\n"]))
                continue
            original_author, corrected_author, uninverted_author, lionid = autversions
            self.authors[original_author] = {
                                        "corrected": corrected_author,
                                        "uninverted": uninverted_author,
                                        "lionid": lionid
                                        }
        autlist.close()

    def standardise_author(self, filename):

        print filename
        authlog = codecs.open('author_errors.log', 'a', 'latin-1')

        authorre = re.compile("<author_name>(.*?)</author_name>")
        authorcorrectedre = re.compile("<author_corrected>.*?</author_corrected>")
        authoruninvertedre = re.compile("<author_uninverted>.*?</author_uninverted>")
        lionidre = re.compile("<lionid>.*?</lionid>")
    
        eeb_file = codecs.open(filename, "r", "utf8")
        temp_file = codecs.open(filename + ".temp", "w", "utf8")
    
        for line in eeb_file:
            if authorre.search(line) != None:
                original_author = authorre.search(line).group(1)
            #if original_author[-1] == ".":
            #    original_author = original_author[:-1]
            #print original_author
            #print authors
                if not original_author in self.authors:
                    authlog.write("".join(["No author found in lookup for: ", original_author, ", ", filename, "\n"]))
                else:
                    line = authorre.sub("".join(["<author_name>", original_author, "</author_name>"]), line)
                    line = authorcorrectedre.sub("".join(["<author_corrected>", self.authors[original_author]["corrected"], "</author_corrected>"]), line, 1)
                    line = authoruninvertedre.sub("".join(["<author_uninverted>", self.authors[original_author]["uninverted"], "</author_uninverted>"]), line)
                    if self.authors[original_author]["lionid"] != "":
                        line = lionidre.sub("", line)
                        line = line.replace("</author_uninverted>", "".join(["</author_uninverted><lionid>", self.authors[original_author]["lionid"], "</lionid>"]))
         
            temp_file.write(line)
        eeb_file.close()
        temp_file.close()
        authlog.close()
    
        os.rename(filename, filename + ".bak")
        os.rename(filename + ".temp", filename)
     
if __name__ == '__main__':

    
    author_standardiser = standardiser()
    author_standardiser.read_lookup('/dc/eurobo/content/authors/author_lookup.lut')
    for filename in sys.argv[1:]:
        if filename[-4:] == '.xml':
            author_standardiser.standardise_author(filename)