<?xml version="1.0" encoding="UTF-8"?>
  <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes" />
    <xsl:template match="/ROW">
      <document>
        <xsl:attribute name="delbatch">
          <xsl:value-of select="delbatch"></xsl:value-of>
        </xsl:attribute>
        <record>
          <film>
            <docid>
              <xsl:value-of select="id"></xsl:value-of>
            </docid>
            <accnum>
              <xsl:value-of select="AN"></xsl:value-of>
            </accnum>
            <xsl:if test="(FC!='')">
              <country_of_production>
                <xsl:value-of select="FC"></xsl:value-of>
              </country_of_production>
            </xsl:if>
            <title>
              <xsl:value-of select="FT1"></xsl:value-of>
            </title>
            <xsl:if test="(FTs!='')">
              <xsl:for-each select="FTs">
                <alternate_title>
                  <xsl:value-of select="."></xsl:value-of>
                </alternate_title>
              </xsl:for-each>
            </xsl:if>
            <doctypes>
              <doctype1>Film</doctype1>
            </doctypes>
            <xsl:if test="(contributors)">
              <contributors>
                <xsl:if test="(CA1)">
                  <contributor>
                    <xsl:attribute name="order">
                      <xsl:value-of select="generate-id(contributor)" />
                    </xsl:attribute>
                    <xsl:attribute name="role">Cast</xsl:attribute>
                    <originalform>
                      <xsl:value-of select="CA1"></xsl:value-of>
                    </originalform>
                  </contributor>
                </xsl:if>
                <xsl:if test="(CAs)">
                  <xsl:for-each select="CAs">
                    <contributor>
                      <xsl:attribute name="order">
                        <xsl:value-of select="generate-id(contributor)" />
                      </xsl:attribute>
                      <xsl:attribute name="role">Cast</xsl:attribute>
                      <originalform>
                        <xsl:value-of select="."></xsl:value-of>
                      </originalform>
                    </contributor>
                  </xsl:for-each>
                </xsl:if>
                <xsl:if test="(PC1)">
                  <contributor>
                    <xsl:attribute name="order">
                      <xsl:value-of select="generate-id(contributor)" />
                    </xsl:attribute>
                    <xsl:attribute name="role">ProductionCompany</xsl:attribute>
                    <organisation_name>
                      <xsl:value-of select="PC1"></xsl:value-of>
                    </organisation_name>
                  </contributor>
                </xsl:if>
                <xsl:if test="(PCs)">
                  <xsl:for-each select="PCs">
                    <contributor>
                      <xsl:attribute name="order">
                        <xsl:value-of select="generate-id(contributor)" />
                      </xsl:attribute>
                      <xsl:attribute name="role">ProductionCompany</xsl:attribute>
                      <organisation_name>
                        <xsl:value-of select="."></xsl:value-of>
                      </organisation_name>
                    </contributor>
                  </xsl:for-each>
                </xsl:if>
                <xsl:if test="(FP1)">
                  <contributor>
                    <xsl:attribute name="order">
                      <xsl:value-of select="generate-id(contributor)" />
                    </xsl:attribute>
                    <xsl:attribute name="role">Producer</xsl:attribute>
                    <originalform>
                      <xsl:value-of select="FP1"></xsl:value-of>
                    </originalform>
                  </contributor>
                </xsl:if>
                <xsl:if test="(FPs)">
                  <xsl:for-each select="FPs">
                    <contributor>
                      <xsl:attribute name="order">
                        <xsl:value-of select="generate-id(contributor)" />
                      </xsl:attribute>
                      <xsl:attribute name="role">Producer</xsl:attribute>
                      <originalform>
                        <xsl:value-of select="."></xsl:value-of>
                      </originalform>
                    </contributor>
                  </xsl:for-each>
                </xsl:if>
                <xsl:if test="(FD1)">
                  <contributor>
                    <xsl:attribute name="order">
                      <xsl:value-of select="generate-id(contributor)" />
                    </xsl:attribute>
                    <xsl:attribute name="role">Director</xsl:attribute>
                    <originalform>
                      <xsl:value-of select="FD1"></xsl:value-of>
                    </originalform>
                  </contributor>
                </xsl:if>
                <xsl:if test="(FDs)">
                  <xsl:for-each select="FDs">
                    <contributor>
                      <xsl:attribute name="order">
                        <xsl:value-of select="generate-id(contributor)" />
                      </xsl:attribute>
                      <xsl:attribute name="role">Director</xsl:attribute>
                      <originalform>
                        <xsl:value-of select="."></xsl:value-of>
                      </originalform>
                    </contributor>
                  </xsl:for-each>
                </xsl:if>
                <xsl:if test="(FW1)">
                  <contributor>
                    <xsl:attribute name="order">
                      <xsl:value-of select="generate-id(contributor)" />
                    </xsl:attribute>
                    <xsl:attribute name="role">Crew</xsl:attribute>
                    <originalform>
                      <xsl:value-of select="FW1"></xsl:value-of>
                    </originalform>
                      <contributor_notes>
                        <production_role>Writer</production_role>
                      </contributor_notes>
                  </contributor>
                </xsl:if>
                <xsl:if test="(FWs)">
                  <xsl:for-each select="FWs">
                    <contributor>
                      <xsl:attribute name="order">
                        <xsl:value-of select="generate-id(contributor)" />
                      </xsl:attribute>
                      <xsl:attribute name="role">Crew</xsl:attribute>
                      <originalform>
                        <xsl:value-of select="."></xsl:value-of>
                      </originalform>
                      <contributor_notes>
                        <production_role>Writer</production_role>
                      </contributor_notes>
                    </contributor>
                  </xsl:for-each>
                </xsl:if>
                <xsl:if test="(PH1)">
                  <contributor>
                    <xsl:attribute name="order">
                      <xsl:value-of select="generate-id(contributor)" />
                    </xsl:attribute>
                    <xsl:attribute name="role">Crew</xsl:attribute>
                    <originalform>
                      <xsl:value-of select="PH1"></xsl:value-of>
                    </originalform>
                      <contributor_notes>
                        <production_role>Photography</production_role>
                      </contributor_notes>
                  </contributor>
                </xsl:if>
                <xsl:if test="(PHs)">
                  <xsl:for-each select="PHs">
                    <contributor>
                      <xsl:attribute name="order">
                        <xsl:value-of select="generate-id(contributor)" />
                      </xsl:attribute>
                      <xsl:attribute name="role">Crew</xsl:attribute>
                      <originalform>
                        <xsl:value-of select="."></xsl:value-of>
                      </originalform>
                      <contributor_notes>
                        <production_role>Photography</production_role>
                      </contributor_notes>
                    </contributor>
                  </xsl:for-each>
                </xsl:if>
                <xsl:if test="(CR1)">
                  <contributor>
                    <xsl:attribute name="order">
                      <xsl:value-of select="generate-id(contributor)" />
                    </xsl:attribute>
                    <xsl:attribute name="role">Crew</xsl:attribute>
                    <originalform>
                      <xsl:value-of select="CR1"></xsl:value-of>
                    </originalform>
                      <contributor_notes>
                        <production_role>Credit</production_role>
                      </contributor_notes>
                  </contributor>
                </xsl:if>
                <xsl:if test="(CRs)">
                  <xsl:for-each select="CRs">
                    <contributor>
                      <xsl:attribute name="order">
                        <xsl:value-of select="generate-id(contributor)" />
                      </xsl:attribute>
                      <xsl:attribute name="role">Crew</xsl:attribute>
                      <originalform>
                        <xsl:value-of select="."></xsl:value-of>
                      </originalform>
                      <contributor_notes>
                        <production_role>Credit</production_role>
                      </contributor_notes>
                    </contributor>
                  </xsl:for-each>
                </xsl:if>
              </contributors>
            </xsl:if>

            <subjects>
              <subject>
                <xsl:attribute name="type">production</xsl:attribute>
                <xsl:value-of select="FT1"></xsl:value-of>
              </subject>
              <xsl:if test="(FTs!='')">
                <xsl:for-each select="FTs">
                  <subject>
                    <xsl:attribute name="type">production</xsl:attribute>
                    <xsl:value-of select="."></xsl:value-of>
                  </subject>
                </xsl:for-each>
              </xsl:if>
            </subjects>

            <xsl:if test="(productions)">
              <productions>
                <production_details>
                  <xsl:if test="(FI!='')">
                    <description>
                      <xsl:value-of select="FI"></xsl:value-of>
                    </description>
                  </xsl:if>
                  <xsl:if test="(SE!='')">
                    <production_series>
                      <xsl:value-of select="SE"></xsl:value-of>
                    </production_series>
                  </xsl:if>
                </production_details>
              </productions>
            </xsl:if>

            <pubdates>
              <originaldate>
                <xsl:if test="(year=0001)">
                  <xsl:attribute name="undated">true</xsl:attribute>
                </xsl:if>
                <xsl:value-of select="year"></xsl:value-of>
              </originaldate>
              <numdate>
                <xsl:if test="(year=0001)">
                  <xsl:attribute name="undated">true</xsl:attribute>
                </xsl:if>
                <xsl:value-of select="year"></xsl:value-of>0101</numdate>
            </pubdates>

            <vendor>FIAF</vendor>
            <sourceinstitution>FIAF</sourceinstitution>
            <projectcode>fiaftre</projectcode>
            <languages>
              <language>English</language>
            </languages>
            <xsl:if test="(notes)">
              <notes>
                <xsl:if test="(AR!='')">
                  <note>
                    <xsl:attribute name="type">Document</xsl:attribute>
                    <xsl:attribute name="subtype">Archive</xsl:attribute>
                    <xsl:value-of select="AR"></xsl:value-of>
                  </note>
                </xsl:if>
                <xsl:if test="(AH!='')">
                  <note>
                    <xsl:attribute name="type">Document</xsl:attribute>
                    <xsl:attribute name="subtype">Access holdings</xsl:attribute>
                    <xsl:value-of select="AH"></xsl:value-of>
                  </note>
                </xsl:if>
                <xsl:if test="(NH!='')">
                  <note>
                    <xsl:attribute name="type">Document</xsl:attribute>
                    <xsl:attribute name="subtype">Non-access holdings</xsl:attribute>
                    <xsl:value-of select="NH"></xsl:value-of>
                  </note>
                </xsl:if>
                <xsl:if test="(NT!='')">
                  <note>
                    <xsl:attribute name="type">Document</xsl:attribute>
                    <xsl:value-of select="NT"></xsl:value-of>
                  </note>
                </xsl:if>

              </notes>
            </xsl:if>
          </film>
        </record>
      </document>
    </xsl:template>
  </xsl:stylesheet>
