# -*- mode: python -*-

import sys

# Build a dictionary of records from a spreadsheet
def ssrecords(sheet):
    recdict = {}
    print 'Building record dictionary from spreadsheet...\n'

    for col in range(sheet.ncols):
        for row in range(1, sheet.nrows):
            pqid = sheet.cell_value(row, 0).encode('latin-1')
            recdict[pqid] = {}

    print 'Total records seen: %s\nNow adding row values:\n' % len(recdict.keys())
    values = 0

    for key in recdict.keys():
        for col in range(1, sheet.ncols):
            for row in range(sheet.nrows):
                if sheet.cell_value(row, 0).encode('latin-1') == key:
                    tag = sheet.cell_value(0, col).encode('latin-1')
                    if tag in recdict[key].keys():
                        if sheet.cell_value(row, col) != u'':
                            recdict[key][tag].append(sheet.cell_value(row, col))
                    else:
                        recdict[key][tag] = []
                        if sheet.cell_value(row, col) != u'':
                            recdict[key][tag].append(sheet.cell_value(row, col)) 
        values += 1
        sys.stdout.write('Row values added: %s\r' % values)
        sys.stdout.flush()
    return recdict


