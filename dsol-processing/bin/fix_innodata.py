# coding=utf-8
import os
import re
import site
site.addsitedir('/packages/dsol/lib/python2.6/site-packages')
from bs4 import BeautifulSoup
import lxml.etree as etree
import StringIO
import shutil
import codecs
from htmlentitydefs import codepoint2name

directory = '/dc/dsol/steadystate/out/iimpft'


def html_entities(text):
    if isinstance(text, (UnicodeEncodeError, UnicodeTranslateError)):
        s = []
        for c in text.object[text.start:text.end]:
            if ord(c) in codepoint2name:
                s.append(u'&%s;' % codepoint2name[ord(c)])
            else:
                s.append(u'&#%s;' % ord(c))
        return ''.join(s), text.end
    else:
        raise TypeError("Can't handle %s" % text.__name__)

codecs.register_error('html_entities', html_entities)

chars = {'&Agrave;': 'À', '&Aacute;': 'Á', '&Acirc;': 'Â', '&Atilde;': 'Ã', '&Auml;': 'Ä', '&Aring;': 'Å', '&AElig;': 'Æ', '&iexcl;': 'l',
         '&Ccedil;': 'Ç', '&Egrave;': 'È', '&Eacute;': 'É', '&Ecirc;': 'Ê', '&Euml;': 'Ë', '&Igrave;': 'Ì', '&Iacute;': 'Í', '&Icirc;': 'Î',
         '&Iuml;': 'Ï', '&ETH;': 'Ð', '&Ntilde;': 'Ñ', '&Ograve;': 'Ò', '&Oacute;': 'Ó', '&Ocirc;': 'Ô', '&Otilde;': 'Õ', '&Ouml;': 'Ö', '&times;': '×',
         '&Oslash;': 'Ø', '&Ugrave;': 'Ù', '&Uacute;': 'Ú', '&Ucirc;': 'Û', '&Uuml;': 'Ü', '&Yacute;': 'Ý', '&THORN;': 'Þ', '&szlig;': 'ß',
         '&agrave;': 'à', '&aacute;': 'á', '&acute;': 'á', '&acirc;': 'â', '&atilde;': 'ã', '&auml;': 'ä', '&aring;': 'å', '&aelig;': 'æ',
         '&ccedil;': 'ç', '&cedil;': 'ç', '&egrave;': 'è', '&eacute;': 'é', '&ecirc;': 'ê', '&euml;': 'ë', '&igrave;': 'ì', '&iacute;': 'í',
         '&icirc;': 'î', '&iuml;': 'ï', '&eth;': 'ð', '&ntilde;': 'ñ', '&ograve;': 'ò', '&oacute;': 'ó', '&ocirc;': 'ô', '&otilde;': 'õ', '&ouml;': 'ö',
         '&divide;': '÷', '&oslash;': 'ø', '&ugrave;': 'ù', '&uacute;': 'ú', '&ucirc;': 'û', '&uuml;': 'ü', '&yacute;': 'ý', '&thorn;': 'þ',
         '&yuml;': 'ÿ', '&Iota;': 'I', '&laquo;': '«', '&raquo;': '»'}
chars1 = {'&iexcl;': '¡', '&cent;': '¢', '&pound;': '£', '&curren;': '¤', '&yen;': '¥', '&brvbar;': '¦', '&sect;': '§', '&uml;': '¨', '&copy;': '©',
          '&ordf;': 'ª', '&laquo;': '«', '&not;': '¬', '&shy;': '­', '&reg;': '®', '&macr;': '¯', '&deg;': '°', '&plusmn;': '±', '&sup2;': '²', '&sup3;': '³',
          '&acute;': '´', '&micro;': 'µ', '&para;': '¶', '&middot;': '·', '&cedil;': '¸', '&sup1;': '¹', '&ordm;': 'º', '&raquo;': '»', '&frac14;': '¼',
          '&frac12;': '½', '&frac34;': '¾', '&iquest;': '¿', '&Agrave;': 'À', '&Aacute;': 'Á', '&Acirc;': 'Â', '&Atilde;': 'Ã', '&Auml;': 'Ä', '&Aring;': 'Å',
          '&AElig;': 'Æ', '&Ccedil;': 'Ç', '&Egrave;': 'È', '&Eacute;': 'É', '&Ecirc;': 'Ê', '&Euml;': 'Ë', '&Igrave;': 'Ì', '&Iacute;': 'Í', '&Icirc;': 'Î',
          '&Iuml;': 'Ï', '&ETH;': 'Ð', '&Ntilde;': 'Ñ', '&Ograve;': 'Ò', '&Oacute;': 'Ó', '&Ocirc;': 'Ô', '&Otilde;': 'Õ', '&Ouml;': 'Ö', '&times;': '×',
          '&Oslash;': 'Ø', '&Ugrave;': 'Ù', '&Uacute;': 'Ú', '&Ucirc;': 'Û', '&Uuml;': 'Ü', '&Yacute;': 'Ý', '&THORN;': 'Þ', '&szlig;': 'ß', '&agrave;': 'à',
          '&aacute;': 'á', '&acirc;': 'â', '&atilde;': 'ã', '&auml;': 'ä', '&aring;': 'å', '&aelig;': 'æ', '&ccedil;': 'ç', '&egrave;': 'è', '&eacute;': 'é',
          '&ecirc;': 'ê', '&euml;': 'ë', '&igrave;': 'ì', '&iacute;': 'í', '&icirc;': 'î', '&iuml;': 'ï', '&eth;': 'ð', '&ntilde;': 'ñ', '&ograve;': 'ò',
          '&oacute;': 'ó', '&ocirc;': 'ô', '&otilde;': 'õ', '&ouml;': 'ö', '&divide;': '÷', '&oslash;': 'ø', '&ugrave;': 'ù', '&uacute;': 'ú', '&ucirc;': 'û',
          '&uuml;': 'ü', '&yacute;': 'ý', '&thorn;': 'þ', '&yuml;': 'ÿ', '&fnof;': 'ƒ', '&Alpha;': 'Α', '&Beta;': 'Β', '&Gamma;': 'Γ', '&Delta;': 'Δ',
          '&Epsilon;': 'Ε', '&Zeta;': 'Ζ', '&Eta;': 'Η', '&Theta;': 'Θ', '&Iota;': 'Ι', '&Kappa;': 'Κ', '&Lambda;': 'Λ', '&Mu;': 'Μ', '&Nu;': 'Ν', '&Xi;': 'Ξ',
          '&Omicron;': 'Ο', '&Pi;': 'Π', '&Rho;': 'Ρ', '&Sigma;': 'Σ', '&Tau;': 'Τ', '&Upsilon;': 'Υ', '&Phi;': 'Φ', '&Chi;': 'Χ', '&Psi;': 'Ψ', '&Omega;': 'Ω',
          '&alpha;': 'α', '&beta;': 'β', '&gamma;': 'γ', '&delta;': 'δ', '&epsilon;': 'ε', '&zeta;': 'ζ', '&eta;': 'η', '&theta;': 'θ', '&iota;': 'ι',
          '&kappa;': 'κ', '&lambda;': 'λ', '&mu;': 'μ', '&nu;': 'ν', '&xi;': 'ξ', '&omicron;': 'ο', '&pi;': 'π', '&rho;': 'ρ', '&sigmaf;': 'ς', '&sigma;': 'σ',
          '&tau;': 'τ', '&upsilon;': 'υ', '&phi;': 'φ', '&chi;': 'χ', '&psi;': 'ψ', '&omega;': 'ω', '&thetasym;': 'ϑ', '&upsih;': 'ϒ', '&piv;': 'ϖ', '&bull;': '•',
          '&hellip;': '…', '&prime;': '′', '&Prime;': '″', '&oline;': '‾', '&frasl;': '⁄', '&weierp;': '℘', '&image;': 'ℑ', '&real;': 'ℜ', '&trade;': '™',
          '&alefsym;': 'ℵ', '&larr;': '←', '&uarr;': '↑', '&rarr;': '→', '&darr;': '↓', '&harr;': '↔', '&crarr;': '↵', '&lArr;': '⇐', '&uArr;': '⇑', '&rArr;': '⇒',
          '&dArr;': '⇓', '&hArr;': '⇔', '&forall;': '∀', '&part;': '∂', '&exist;': '∃', '&empty;': '∅', '&nabla;': '∇', '&isin;': '∈', '&notin;': '∉',
          '&ni;': '∋', '&prod;': '∏', '&sum;': '∑', '&minus;': '−', '&lowast;': '∗', '&radic;': '√', '&prop;': '∝', '&infin;': '∞', '&ang;': '∠', '&and;': '∧',
          '&or;': '∨', '&cap;': '∩', '&cup;': '∪', '&int;': '∫', '&there4;': '∴', '&sim;': '∼', '&cong;': '≅', '&asymp;': '≈', '&ne;': '≠', '&equiv;': '≡',
          '&le;': '≤', '&ge;': '≥', '&sub;': '⊂', '&sup;': '⊃', '&nsub;': '⊄', '&sube;': '⊆', '&supe;': '⊇', '&oplus;': '⊕', '&otimes;': '⊗', '&perp;': '⊥',
          '&sdot;': '⋅', '&lceil;': '⌈', '&rceil;': '⌉', '&lfloor;': '⌊', '&rfloor;': '⌋', '&lang;': '⟨', '&rang;': '⟩', '&loz;': '◊', '&spades;': '♠',
          '&clubs;': '♣', '&hearts;': '♥', '&diams;': '♦', '&lt;': '<', '&gt;': '>', '&OElig;': 'Œ', '&oelig;': 'œ', '&Scaron;': 'Š', '&scaron;': 'š',
          '&Yuml;': 'Ÿ', '&circ;': 'ˆ', '&tilde;': '˜', '&ensp;': ' ', '&emsp;': ' ', '&thinsp;': ' ', '&zwnj;': '‌', '&zwj;': '‍', '&lrm;': '‎', '&rlm;': '‏',
          '&ndash;': '–', '&mdash;': '—', '&lsquo;': '‘', '&rsquo;': '’', '&sbquo;': '‚', '&ldquo;': '“', '&rdquo;': '”', '&bdquo;': '„', '&dagger;': '†',
          '&Dagger;': '‡', '&permil;': '‰', '&lsaquo;': '‹', '&rsaquo;': '›', '&euro;': '€'}


def encode_for_html(unicode_data, encoding='ascii'):
    return unicode_data.encode(encoding, 'html_entities')


def yield_xml(in_file):
    records = in_file.split('<?xml version=\'1.0\' encoding=\'UTF-8\'?>')
    records = records[1:]
    for record in records:
        # record = '<!DOCTYPE html>%s' % record
        record = '<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "/home/rschumac/work/iimpiipaprisma/innodata_fix/xhtml11.dtd">%s' % record

        yield record


try:
    for f in os.listdir(directory):
        if '20150324' in f:
            filename = os.path.join(directory, f)
            print filename
            xml_file = open(filename, 'r').read()
            out_file_name = filename.replace('20150324', '20150325')
            out_file = open(out_file_name, 'w')
            for record in yield_xml(xml_file):
                # record = record.encode('utf-8')
                xml = StringIO.StringIO(record)
                parser = etree.XMLParser(load_dtd=True)
                parsed_xml = etree.parse(xml, parser)

                u_date = parsed_xml.xpath('//LastLegacyUpdateTime')[0]
                u_date.text = '20150325030000'
                try:
                    parsed_value = parsed_xml.xpath('//Text')[0].text
                    parsed_value = encode_for_html(parsed_value)
                    parsed_value = re.sub('æ', '', parsed_value)
                    if 'ÃÅ' in parsed_value:
                        print parsed_value
                    parsed_value = re.sub('Å', '', parsed_value)
                    parsed_value = re.sub('¼', '', parsed_value)
                    parsed_value = re.sub('´', '', parsed_value)
                    parsed_value = re.sub('<title>&nbsp;</title>', '<title></title>', parsed_value)
                    parsed_value = re.sub('http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', '', parsed_value)
                    parsed_value = re.sub('<>', '', parsed_value)
                    parsed_value = re.sub('&#[0-9]+;', '', parsed_value)
                    for k in chars:
                        if k in parsed_value:
                            parsed_value = re.sub(k, chars[k], parsed_value)
                    for k in chars1:
                        if k in parsed_value:
                            parsed_value = re.sub(k, chars1[k], parsed_value)
                    parsed_value = re.sub('&(?!([a-zA-Z0-9]+|#[0-9]+|#x[0-9a-fA-F]+);)', '&amp;', parsed_value)
                    parsed_value = re.sub('&;', '', parsed_value)
                    parsed_value = re.sub('& ', '', parsed_value)
                    parsed_value = re.sub(' & ', '', parsed_value)
                    replace_path = parsed_xml.xpath('//Text')[0]
                    replace_path.text = etree.CDATA(unicode(parsed_value, "UTF-8"))
                    xml = etree.tostring(parsed_xml, pretty_print=True, xml_declaration=True, encoding='UTF-8')
                    out_file.write(xml)
                except IndexError:
                    xml = etree.tostring(parsed_xml, pretty_print=True, xml_declaration=True, encoding='UTF-8')
                    out_file.write(xml)
            # exit(1)

except KeyboardInterrupt:
    print ''
    exit(1)
