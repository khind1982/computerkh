<?xml version="1.0" encoding="UTF-8"?>
  <xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes" />
    <xsl:template match="/mod">
      <rec>
        <itemid>
          <xsl:value-of select="pid" />
        </itemid>
        <subscription>
          <unit>Collection <xsl:value-of select="collection" />
          </unit>
          <country>
            <xsl:value-of select="country" />
          </country>
        </subscription>

        <rec_search>

          <pqid>
            <xsl:value-of select="pid" />
          </pqid>

          <xsl:for-each select="titles/title">
            <title>
              <xsl:value-of select="."></xsl:value-of>
            </title>
          </xsl:for-each>

          <xsl:if test="(authors)">
            <xsl:for-each select="authors/author">
              <author_main>
                <xsl:value-of select="."></xsl:value-of>
              </author_main>
            </xsl:for-each>
          </xsl:if>

          <startdate>
            <xsl:value-of select="date" />0101</startdate>
          <enddate>
            <xsl:value-of select="date" />1231</enddate>
          <displaydate>
            <xsl:value-of select="date" />
          </displaydate>

          <imprint>
            <xsl:value-of select="imprint" />
          </imprint>

          <place_of_publication>
            <xsl:value-of select="city" />
          </place_of_publication>

          <country_of_publication>
            <xsl:value-of select="country" />
          </country_of_publication>

          <publisher_printer>
            <xsl:value-of select="publisher" />
          </publisher_printer>

          <pagination>
            <xsl:value-of select="pagination" />
          </pagination>

          <shelfmark>
            <xsl:value-of select="shelfmark" />
          </shelfmark>

          <source_library>
            <xsl:value-of select="library" />
          </source_library>

          <source_collection>
            <xsl:value-of select="country" />
          </source_collection>

          <subject>
            <xsl:value-of select="subject" />
          </subject>

          <xsl:for-each select="languages/language">
            <language>
              <xsl:value-of select="." />
            </language>
          </xsl:for-each>
        </rec_search>

        <itemimagefiles>
          <xsl:for-each select="itemimagefiles/imageitem">
            <itemimage>
              <itemimagefile1>
                <xsl:value-of select="image" />
              </itemimagefile1>
              <order>
                <xsl:value-of select="order" />
              </order>
              <imagenumber>
                <xsl:value-of select="imagenumber" />
              </imagenumber>

              <xsl:if test="(orderlabel)">
                <orderlabel>
                  <xsl:value-of select="orderlabel" />
                </orderlabel>
              </xsl:if>

              <xsl:if test="(pagecontent)">
                <xsl:for-each select="pagecontent/item">
                  <pagecontent>
                    <xsl:attribute name="number">
                      <xsl:value-of select="number" />
                    </xsl:attribute>
                    <xsl:value-of select="type" />
                  </pagecontent>
                </xsl:for-each>
              </xsl:if>

              <colour>
                <xsl:value-of select="colour" />
              </colour>

              <pagetype>
                <xsl:choose>
                 <xsl:when test="(pagetype!='')">
                   <xsl:value-of select="pagetype" />
                 </xsl:when>
                 <xsl:otherwise>None</xsl:otherwise>
                </xsl:choose>
              </pagetype>



            </itemimage>
          </xsl:for-each>
        </itemimagefiles>



      </rec>
    </xsl:template>
  </xsl:stylesheet>
