<xsl:stylesheet version="1.0"  xmlns:xsl="http://www.w3.org/1999/XSL/Transform">
    <xsl:output omit-xml-declaration="yes" indent="yes"/>
    <xsl:strip-space elements="*"/>

    <xsl:variable name="vApos">'</xsl:variable>

    <xsl:template match="*[@* or not(*)] ">
      <xsl:if test="not(*)">
         <xsl:apply-templates select="ancestor-or-self::*" mode="path"/>
         <xsl:value-of select="concat('=',$vApos,.,$vApos)"/>
         <xsl:text>&#xA;</xsl:text>
        </xsl:if>
        <xsl:apply-templates select="@*|*"/>
    </xsl:template>

<!--     <xsl:template match="*" mode="path">
        <xsl:value-of select="concat('/',name())"/>
        <xsl:variable name="vnumPrecSiblings" select=
         "count(preceding-sibling::*[name()=name(current())])"/>
        <xsl:if test="$vnumPrecSiblings">
            <xsl:value-of select="concat('[', $vnumPrecSiblings +1, ']')"/>
        </xsl:if>
    </xsl:template>
 -->

    <xsl:template match="*" mode="path">
        <xsl:value-of select="concat('/',name())"/>
        <xsl:variable name="vnumPrecSiblings" select=
         "count(preceding-sibling::*[name()=name(current())])"/>
         <xsl:variable name="vnumFollowSiblings" select=
         "count(following-sibling::*[name()=name(current())])"/>
         <xsl:choose>
          <xsl:when test="$vnumPrecSiblings">
            <xsl:value-of select="concat('[', $vnumPrecSiblings, ']')"/>
        </xsl:when>
        <xsl:when test="not($vnumPrecSiblings) and $vnumFollowSiblings">
            <xsl:value-of select="concat('[', '0', ']')"/>
        </xsl:when>
      </xsl:choose>
    </xsl:template>

    <xsl:template match="@*">
        <xsl:apply-templates select="../ancestor-or-self::*" mode="path"/>
        <xsl:value-of select="concat('[@',name(), '=',$vApos,.,$vApos,']')"/>
        <xsl:text>&#xA;</xsl:text>
    </xsl:template>
</xsl:stylesheet>
