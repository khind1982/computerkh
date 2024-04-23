# -*- coding: latin-1 -*-
import xlrd
import types

def smart_unicode(s, encoding='utf-8', errors='strict'):
    if type(s) in (unicode, int, long, float, types.NoneType):
        return unicode(s)
    elif type(s) is str or hasattr(s, '__unicode__'):
        return unicode(s, encoding, errors)
    else:
        return unicode(str(s), encoding, errors)

def smart_str(s, encoding='utf-8', errors='strict', from_encoding='utf-8'):
    if type(s) in (int, long, float, types.NoneType):
        return str(s)
    elif type(s) is str:
        if encoding != from_encoding:
            return s.decode(from_encoding, errors).encode(encoding, errors)
        else:
            return s
    elif type(s) is unicode:
        return s.encode(encoding, errors)
    elif hasattr(s, '__str__'):
        return smart_str(str(s), encoding, errors, from_encoding)
    elif hasattr(s, '__unicode__'):
        return smart_str(unicode(s), encoding, errors, from_encoding)
    else:
        return smart_str(str(s), encoding, errors, from_encoding)

spread_sheet = xlrd.open_workbook('Agency.xls')
sheet1 = spread_sheet.sheet_by_name('Agency')

def lookup(filename, delimiter, comment='#'):
    luTable = {}
    with open(filename, 'r') as lutfile:
        for line in lutfile:
            if line.startswith(comment):
                continue
            else:
                split_line = line.split(delimiter, 1)
                luTable[split_line[0]] = split_line[1].rstrip()
    return luTable

codes = lookup("CODES.txt", "|")
nums = 1

with open('output.txt', 'w') as result:
    for rownum in range(sheet1.nrows):

        RecordId = sheet1.cell(rowx=rownum, colx=0).value
        Status = sheet1.cell(rowx=rownum, colx=1).value
        OrgName = sheet1.cell(rowx=rownum, colx=2).value
        Address1 = sheet1.cell(rowx=rownum, colx=3).value
        Address2 = sheet1.cell(rowx=rownum, colx=4).value
        Address3 = sheet1.cell(rowx=rownum, colx=5).value
        Address4 = sheet1.cell(rowx=rownum, colx=6).value
        ConfidentialAddress = sheet1.cell(rowx=rownum, colx=7).value
        PostCode = sheet1.cell(rowx=rownum, colx=8).value
        PublicPhone = sheet1.cell(rowx=rownum, colx=9).value
        AdminPhone = sheet1.cell(rowx=rownum, colx=10).value
        Minicom = sheet1.cell(rowx=rownum, colx=11).value
        Email = sheet1.cell(rowx=rownum, colx=12).value
        Website = sheet1.cell(rowx=rownum, colx=13).value
        Monday = sheet1.cell(rowx=rownum, colx=14).value
        Tuesday = sheet1.cell(rowx=rownum, colx=15).value
        Wednesday = sheet1.cell(rowx=rownum, colx=16).value
        Thursday = sheet1.cell(rowx=rownum, colx=17).value
        Friday = sheet1.cell(rowx=rownum, colx=18).value
        Weekends = sheet1.cell(rowx=rownum, colx=19).value
        OfficeHours = sheet1.cell(rowx=rownum, colx=20).value
        TargetGroup = sheet1.cell(rowx=rownum, colx=21).value
        AreaServed = sheet1.cell(rowx=rownum, colx=22).value
        ServiceOffered = sheet1.cell(rowx=rownum, colx=23).value
        HowtoContact = sheet1.cell(rowx=rownum, colx=24).value
        Languages = sheet1.cell(rowx=rownum, colx=25).value
        TypeofOrganisation = sheet1.cell(rowx=rownum, colx=26).value
        Fax = sheet1.cell(rowx=rownum, colx=27).value
        WheelchairAccess = sheet1.cell(rowx=rownum, colx=28).value
        AdaptedToilets = sheet1.cell(rowx=rownum, colx=29).value
        AccessText = sheet1.cell(rowx=rownum, colx=30).value
        PublicTransport = sheet1.cell(rowx=rownum, colx=31).value
        YearEstablished = sheet1.cell(rowx=rownum, colx=32).value
        Staffing = sheet1.cell(rowx=rownum, colx=33).value
        CharityNo = sheet1.cell(rowx=rownum, colx=34).value
        LocalAuthority = sheet1.cell(rowx=rownum, colx=35).value
        LastUpdated = sheet1.cell(rowx=rownum, colx=36).value

        result.write('<rec>\n')
        result.write('<attribs>\n')
        try:
            (OrgName, Address4)
            result.write('<somhd>%s - %s</somhd>\n' % (smart_str(OrgName), smart_str(Address4)))
            result.write('<rechd>%s - %s</rechd>\n' % (smart_str(OrgName), smart_str(Address4)))
        except IndexError:
            result.write('<somhd>%s</somhd>\n' % smart_str(OrgName))
            result.write('<rechd>%s</rechd>\n' % smart_str(OrgName))
        result.write('<oldid>%s</oldid>\n' % int(RecordId))
        result.write('<id>084/%05d</id>\n' % nums)
        nums += 1
        result.write('<level>1</level>\n')
        result.write('</attribs>\n')
        result.write('<metadata>\n')
        result.write('<hdate></hdate>\n')
        result.write('<pubdate></pubdate>\n')
        result.write('</metadata>\n')
        result.write('<map>%s</map>\n' % PostCode)
        result.write('<body>\n')
        result.write('<table>\n')
        result.write('<tr><td valign=top><b>Address:</b></td><td valign=top>%s<br>' % smart_str(OrgName))
        if Address1:  result.write(smart_str('%s<br>' % Address1))
        if Address2:  result.write(smart_str('%s<br>' % Address2))
        if Address3:  result.write(smart_str('%s<br>' % Address3))
        if Address4:  result.write(smart_str('%s<br>' % Address4))
        result.write('<pst>%s</pst></td></tr>\n' % PostCode)
        result.write('<tr><td valign=top><b>Telephone (Public):</b></td><td valign=top>%s</td></tr>\n' % PublicPhone)
        result.write('<tr><td valign=top><b>Fax:</b></td><td valign=top>%s</td></tr>\n' % AdminPhone)
        result.write('<tr><td valign=top><b>Email:</b></td><td valign=top><a target="_blank" href="mailto:%s">%s</a></td></tr>\n' % (Email, Email))
        try:
            Website
            result.write('<tr><td valign=top><b>Website:</b></td><td valign=top><a target="extlink" href="%s">%s</a></td></tr>\n' % (Website, Website))
        except IndexError:
            result.write('<tr><td valign=top><b>Website:</b></td><td valign=top>N/A</td></tr>\n')
        try:
            HowtoContact
            result.write('<tr><td valign=top><b>How To Contact?:</b></td><td valign=top>%s</td></tr>\n' % smart_str(HowtoContact))
        except IndexError:
            result.write('<tr><td valign=top><b>How To Contact?:</b></td><td valign=top>N/A</td></tr>\n')
        result.write('<tr><td valign=top>&nbsp;</td><td valign=top>&nbsp;</td></tr>\n')
        result.write('<tr><td colspan=2><b><u>Organisation Details</u></b></td></tr>\n')
        if TypeofOrganisation:
            
            result.write('<tr><td valign=top><b>Organisation Type:</b></td><td valign=top>%s</td></tr>\n' % codes[TypeofOrganisation])
        else:
            result.write('<tr><td valign=top><b>Organisation Type:</b></td><td valign=top></td></tr>\n')
        try:
            CharityNo
            result.write('<tr><td valign=top><b>Charity Number:</b></td><td valign=top>%s</td></tr>\n' % CharityNo)
        except IndexError:
            result.write('<tr><td valign=top><b>Charity Number:</b></td><td valign=top>N/A</td></tr>\n')
        try:
            YearEstablished
            result.write('<tr><td valign=top><b>Year Established:</b></td><td valign=top>%s</td></tr>\n' % YearEstablished)
        except IndexError:
            result.write('<tr><td valign=top><b>Year Established:</b></td><td valign=top>N/A</td></tr>\n')
        try:
            AreaServed
            result.write('<tr><td valign=top><b>Area Served:</b></td><td valign=top>%s</td></tr>\n' % smart_str(AreaServed))
        except IndexError:
            result.write('<tr><td valign=top><b>Area Served:</b></td><td valign=top>N/A</td></tr>\n')
        try:
            TargetGroup
            repl_line = '<tr><td valign=top><b>Target Group:</b></td><td valign=top>%s</td></tr>\n' % smart_str(TargetGroup)
            repl_line = smart_str(repl_line)
            result.write(repl_line)
        except IndexError:
            result.write('<tr><td valign=top><b>Target Group:</b></td><td valign=top>N/A</td></tr>\n')
        try:
            ServiceOffered
            line_rep = '<tr><td valign=top><b>Service Offered:</b></td><td valign=top>%s</td></tr>\n' % smart_str(ServiceOffered)
            line_rep = smart_str(line_rep)
            result.write(line_rep)
        except IndexError:
            result.write('<tr><td valign=top><b>Service Offered:</b></td><td valign=top>N/A</td></tr>\n')
        try:
            PostCode
            result.write('<tr><td valign=top><b>Staff:</b></td><td valign=top>%s</td></tr>\n' % PostCode)
        except IndexError:
            result.write('<tr><td valign=top><b>Staff:</b></td><td valign=top>v</td></tr>\n')

        result.write('<tr><td valign=top>&nbsp;</td><td valign=top>&nbsp;</td></tr>\n')
        result.write('<tr><td colspan=2><b><u>Opening Details</u></b></td></tr>\n')
        result.write('<tr><td valign=top><b>Opening Hours:</b></td><td valign=top>')
        if Monday != '':
            result.write('Monday: %s<br>' % smart_str(Monday))
        else:
            result.write('Monday: N/A<br>')
        if Tuesday != '':
            result.write('Tuesday: %s<br>' % smart_str(Tuesday))
        else:
            result.write('Tuesday: N/A<br>')
        if Wednesday != '':
            result.write('Webnesday: %s<br>' % smart_str(Wednesday))
        else:
            result.write('Webnesday: N/A<br>')
        if Thursday != '':
            result.write('Thursday: %s<br>' % smart_str(Thursday))
        else:
            result.write('Thursday: N/A<br>')
        if Friday != '':
            result.write('Friday: %s<br>' % smart_str(Friday))
        else:
            result.write('Friday: N/A<br>')
        if Weekends != '':
            result.write('Weekends: %s<br>' % smart_str(Weekends))
        else:
            result.write('Weekends: N/A<br>')

        result.write('</td></tr>\n')
        result.write('<tr><td valign=top>&nbsp;</td><td valign=top>&nbsp;</td></tr>\n')
        result.write('<tr><td colspan=2><b><u>Access Details</u></b></td></tr>\n')
        try:
            AccessText
            result.write('<tr><td valign=top><b>Access Notes:</b></td><td valign=top>%s</td></tr>\n' % smart_str(AccessText))
        except IndexError:
            result.write('<tr><td valign=top><b>Access Notes:</b></td><td valign=top>No information available</td></tr>\n')
        try:
            PublicTransport
            result.write('<tr><td valign=top><b>Public Transport:</b></td><td valign=top>%s</td></tr>\n' % smart_str(PublicTransport))
        except IndexError:
            result.write('<tr><td valign=top><b>Public Transport:</b></td><td valign=top>No information available</td></tr>\n')
        if WheelchairAccess:
            wheel = smart_str(WheelchairAccess).strip()
            result.write('<tr><td valign=top><b>Wheelchair Access:</b></td><td valign=top>%s</td></tr>\n' % codes[wheel])
 
        if AdaptedToilets:
            AdaptedT = codes[AdaptedToilets]
            result.write('<tr><td valign=top><b>Disabled Toilets:</b></td><td valign=top>%s</td></tr>' % AdaptedT)

        result.write('</table>\n')
        result.write('</body>\n')
        result.write('</rec>\n')
