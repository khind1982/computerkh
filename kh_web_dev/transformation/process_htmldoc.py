import os

import lxml.etree as et

def main():
    with open('mydocument.html', 'r') as inf:
        html_data = et.parse(inf, et.XMLParser(remove_blank_text=True, resolve_entities=True))
        xslt = et.parse("fulltext_changer.xsl")
        transform = et.XSLT(xslt)
        new_html_data = transform(html_data)
        with open('mydocument_output.html', 'w') as writef:
            writef.write(et.tostring(new_html_data, pretty_print=True).decode())

if __name__ == "__main__":
    main()