import sys, codecs, re
import pyodbc


class deepindeximporter:

    def __init__(self):
    
        self.databaseConnection = pyodbc.connect('DSN=Vogue;uid=sa;pwd=Gon3.Fishing!')
        self.cu = self.databaseConnection.cursor()
    
    def importfromsql(self, infile):
        self.setqueryadjustments()
        with codecs.open(infile, 'r', 'utf-16') as inf:
            self.count = 0
            currentquery = ''
            inquery = 0
            for line in inf:
                if line[:6] == "INSERT":
                    #print line.encode('ascii', 'xmlcharrefreplace')
                    inquery = 1
                    self.dealwithquery(currentquery)
                    currentquery = line
                elif inquery == 1:
                    currentquery += line
            self.dealwithquery(currentquery, True)

    def setqueryadjustments(self):
        self.adjustments = {
                                "go": [re.compile("^GO[\r\n]+", re.M), ""],
                                "print": [re.compile("^print \'Processed.*?\n", re.M), ""]
                            }

    def dealwithquery(self, query, final=False):
        for adj in self.adjustments.keys():
            query = self.adjustments[adj][0].sub(self.adjustments[adj][1], query)
        #print query.encode('ascii', 'xmlcharrefreplace')
        self.cu.execute(query)
        self.databaseConnection.commit()
        self.count +=1
        if self.count % 1000 == 0 or final == True:
            print "dealt with %s queries" % str(self.count)

def quickrun():
    a = deepindeximporter()
    a.importfromsql("dbo.FASTVIEW_ARTICLES.Table.sql")
    #a.importfromsql("dbo.FASTVIEW_GARMENTS.Table.sql")
    #a.importfromsql("dbo.FASTVIEW_IMAGES.Table.sql")
    #a.importfromsql("dbo.FASTVIEW_ADS.Table.sql")
            
if __name__ == '__main__':

    deepindex("dbo.FASTVIEW_ARTICLES.Table.sql")
            
