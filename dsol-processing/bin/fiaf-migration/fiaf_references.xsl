<?xml version="1.0" encoding="UTF-8"?>
  <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes" />
    <xsl:template match="/record">
      <document>
        <xsl:attribute name="delbatch">
          <xsl:value-of select="delbatch"></xsl:value-of>
        </xsl:attribute>
        <record>

          <booksection>
            <!-- <document>/<record>/<booksection>/docid -->
            <docid>
              <xsl:value-of select="id"></xsl:value-of>
            </docid>

            <!-- <document>/<record>/<booksection>/ country_of_publication -->
            <!-- <publication-countries>/<publication-country> -->
            <!--
            <publication-countries>
              <publication-country>USA</publication-country>
              <publication-country>Canada</publication-country>
              <publication-country>UK</publication-country>
            </publication-countries>
            -->
            <xsl:if test="(publication-countries!='')">
             <xsl:for-each select="publication-countries">
              <xsl:for-each select="publication-country">
                <country_of_publication>
                  <xsl:value-of select="."></xsl:value-of>
                </country_of_publication>
              </xsl:for-each>
              </xsl:for-each>
            </xsl:if>

            <!-- <ISBN>	<document>/<record>/<booksection>/print_issn -->
            <print_issn>
              <xsl:value-of select="ISBN"></xsl:value-of>
            </print_issn>

            <xsl:if test="(sectionheads!='')">
              <sectionheads>
                <!-- <chapter>	<document>/<record>/<booksection>/sectionheads/section1 -->
                <xsl:if test="(chapter!='')">
                  <section1>
                    <xsl:value-of select="chapter"></xsl:value-of>
                  </section1>
                </xsl:if>
                <!-- <part>	<document>/<record>/<booksection>/sectionheads/section2 -->
                <xsl:if test="(part!='')">
                  <section2>
                    <xsl:value-of select="part"></xsl:value-of>
                  </section2>
                </xsl:if>
                <!-- <letter>	<document>/<record>/<booksection>/sectionheads/section3 -->
                <xsl:if test="(letter!='')">
                  <section3>
                    <xsl:value-of select="letter"></xsl:value-of>
                  </section3>
                </xsl:if>
              </sectionheads>
            </xsl:if>

            <!-- <wtitle>	<document>/<record>/<booksection>/work_title -->
            <work_title>
              <xsl:value-of select="wtitle"></xsl:value-of>
            </work_title>

            <!-- <mtitle>	<document>/<record>/<booksection>/title -->
            <title>
              <xsl:value-of select="mtitle"></xsl:value-of>
            </title>

            <doctypes>
              <doctype1>Book</doctype1>
              <doctype1>Chapter</doctype1>
            </doctypes>

            <contributors>
              <xsl:for-each select="wauthor">
                <contributor>
                  <xsl:attribute name="role">PublicationEditor</xsl:attribute>
                  <originalform>
                    <xsl:value-of select="."></xsl:value-of>
                  </originalform>
                  <standardform>
                    <xsl:value-of select="./following-sibling::wauthorinv[1]"></xsl:value-of>
                  </standardform>
                  <role_desc>Ed</role_desc>
                </contributor>
              </xsl:for-each>

              <xsl:for-each select="mauthor">
                <contributor>
                  <xsl:attribute name="role">Author</xsl:attribute>
                  <originalform>
                    <xsl:value-of select="."></xsl:value-of>
                  </originalform>
                  <standardform>
                    <xsl:value-of select="./following-sibling::mauthorinv[1]"></xsl:value-of>
                  </standardform>
                </contributor>
              </xsl:for-each>
            </contributors>

            <!-- <document>/<record>/<booksection>/pubdates/numdate -->
            <!-- <document>/<record>/<booksection>/pubdates/originaldate -->
            <pubdates>
              <originaldate>
                <xsl:value-of select="publication-date"></xsl:value-of>
              </originaldate>
              <numdate>
                <xsl:value-of select="publication-date"></xsl:value-of>0101</numdate>
            </pubdates>

            <!-- <document>/<record>/<booksection>/publiserinfo/<publisher> -->
            <!-- <document>/<record>/<booksection>/publiserinfo/<publisher_address> -->
            <!-- <publisher-address> -->
            <publisherinfo>
              <publisher>
                <xsl:value-of select="publisher"></xsl:value-of>
              </publisher>
              <publisher_address>
                <xsl:value-of select="publisher-address"></xsl:value-of>
              </publisher_address>
            </publisherinfo>

            <vendor>FIAF</vendor>
            <sourceinstitution>FIAF</sourceinstitution>
            <projectcode>fiafref</projectcode>
            <languages>
              <language>English</language>
            </languages>

            <!-- <text>	<document>/bodytext -->
            <!-- <copyright>	<document>/<record>/<booksection>/work_copyright -->
            <xsl:if test="(copyright)">
              <work_copyright>
                <xsl:value-of select="copyright"></xsl:value-of>
              </work_copyright>
            </xsl:if>

          </booksection>
        </record>

        <!-- <document>/bodytext -->
        <bodytext>
          <xsl:value-of select="cdata" disable-output-escaping="yes"></xsl:value-of>
        </bodytext>

      </document>
    </xsl:template>
  </xsl:stylesheet>
