<?xml version="1.0" encoding="UTF-8"?>
  <xsl:stylesheet version="1.0" xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output method="xml" indent="yes" />
    <xsl:template match="/document">
      <document>
        <xsl:attribute name="delbatch"><xsl:value-of select="@delbatch"></xsl:value-of></xsl:attribute>
        <xsl:for-each select="record">
          <record>
            <xsl:for-each select="film">
              <film>
                <docid>
                  <xsl:value-of select="docid"></xsl:value-of>
                </docid>
                <accnum>
                  <xsl:value-of select="accnum"></xsl:value-of>
                </accnum>
                <xsl:if test="(country_of_production!='')">
                  <country_of_production>
                    <xsl:value-of select="country_of_production"></xsl:value-of>
                  </country_of_production>
                </xsl:if>
                <title>
                  <xsl:value-of select="title"></xsl:value-of>
                </title>
                <xsl:if test="(alternate_title!='')">
                  <alternate_title>
                    <xsl:value-of select="alternate_title"></xsl:value-of>
                  </alternate_title>
                </xsl:if>
                <doctypes>
                  <doctype1>Film</doctype1>
                </doctypes>

                <xsl:if test="(contributors!='')">
                  <xsl:for-each select="contributors">
                      <contributors>
                        <xsl:for-each select="contributor">
                          <contributor>
                            <!--
                            <xsl:attribute name="order">
                              <xsl:value-of select="position()" />
                            </xsl:attribute>
                            -->
                            <xsl:attribute name="role">
                              <xsl:value-of select="@role" />
                            </xsl:attribute>
                            <xsl:if test="(organisation_name)">
                              <originalform>
                                <xsl:value-of select="organisation_name" />
                              </originalform>
                              <organisation_name>
                                <xsl:value-of select="organisation_name" />
                              </organisation_name>
                            </xsl:if>
                            <xsl:if test="(originalform)">
                              <originalform>
                                <xsl:value-of select="originalform" />
                              </originalform>
                            </xsl:if>
                            <xsl:if test="(contribdesc)">
                              <contribdesc>
                                <xsl:value-of select="contribdesc" />
                              </contribdesc>
                            </xsl:if>
                          </contributor>
                        </xsl:for-each>
                      </contributors>
                  </xsl:for-each>
                </xsl:if>

                <xsl:for-each select="subjects">
                  <subjects>
                    <xsl:for-each select="subject">
                      <subject>
                        <xsl:attribute name="type">
                          <xsl:value-of select="@type" />
                        </xsl:attribute>
                        <xsl:value-of select="text()"></xsl:value-of>
                      </subject>
                    </xsl:for-each>
                  </subjects>
                </xsl:for-each>
                <xsl:for-each select="productions">
                  <productions>
                    <xsl:for-each select="production_details">
                      <production_details>
                        <description>
                          <xsl:value-of select="description"></xsl:value-of>
                        </description>
                      </production_details>
                    </xsl:for-each>
                  </productions>
                </xsl:for-each>
                <xsl:choose>
                  <xsl:when test="pubdates!=''">
                    <xsl:for-each select="pubdates">
                      <pubdates>
                        <originaldate>
                          <xsl:value-of select="originaldate"></xsl:value-of>
                        </originaldate>
                        <numdate>
                          <xsl:value-of select="numdate"></xsl:value-of>
                        </numdate>
                      </pubdates>
                    </xsl:for-each>
                  </xsl:when>
                  <xsl:otherwise>
                    <pubdates>
                      <originaldate>00000101</originaldate>
                      <numdate>00010101</numdate>
                    </pubdates>
                  </xsl:otherwise>
                </xsl:choose>
                <vendor>FIAF</vendor>
                <sourceinstitution>FIAF</sourceinstitution>
                <languages>
                  <language>English</language>
                </languages>
                <xsl:for-each select="notes">
                  <notes>
                    <xsl:for-each select="note">
                      <note>
                        <xsl:attribute name="type">
                          <xsl:value-of select="@type" />
                        </xsl:attribute>
                        <xsl:if test="(@contentlabel!='')">
                          <xsl:attribute name="contentlabel">
                            <xsl:value-of select="@contentlabel"></xsl:value-of>
                          </xsl:attribute>
                        </xsl:if>
                        <xsl:value-of select="."></xsl:value-of>
                      </note>
                    </xsl:for-each>
                  </notes>
                </xsl:for-each>
              </film>
            </xsl:for-each>
          </record>
        </xsl:for-each>
      </document>
    </xsl:template>
  </xsl:stylesheet>
