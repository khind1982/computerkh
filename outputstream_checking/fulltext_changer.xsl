<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:fo="http://www.w3.org/1999/XSL/Format"
	xmlns:d="http://www.w3.org/1999/XSL/Format"
	xmlns:pqfn="http://local/functions" exclude-result-prefixes="fo pqfn">
	<xsl:param name="ProdCode"/>

	<xsl:output method="xml" indent="yes" encoding="UTF-8"/>

    <xsl:template match="h1">
        <h3 style="text-align: center;"><xsl:apply-templates/></h3>
    </xsl:template>

	<xsl:variable name="uppercase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZ'"/>
	<xsl:variable name="lowercase" select="'abcdefghijklmnopqrstuvwxyz'"/>
	<xsl:template match="*">
		<xsl:element name="{translate(local-name(), $uppercase, $lowercase)}" namespace="{namespace-uri()}">
			<xsl:apply-templates select="@*|node()"/>
		</xsl:element>
	</xsl:template>

	<xsl:template match="@*">
		<xsl:attribute name="{translate(local-name(), $uppercase, $lowercase)}" namespace="{namespace-uri()}">
			<xsl:value-of select="."/>
		</xsl:attribute>
	</xsl:template>
	<xsl:template match="comment() | text() | processing-instruction()">
		<xsl:copy/>
	</xsl:template>

</xsl:stylesheet>
