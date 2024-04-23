<?xml version="1.0" encoding="utf8"?>
<xsl:stylesheet
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:xs="http://www.w3.org/2001/XMLSchema"
	xmlns:eeb="http://local.data"
	xmlns:ext="http://exslt.org/common"
	xmlns:date="http://exslt.org/dates-and-times"
	xmlns:regexp="http://exslt.org/regular-expressions"
	extension-element-prefixes="date ext xs regexp"
	version="1.0">


	<!-- Standard copyright text used in Ingest Schema data -->
	<xsl:variable name="copyrightText"
		select="'Database copyright ProQuest LLC; ProQuest does not claim copyright in the individual underlying works.'" />


	<!-- Lookup table to find the library short code from its full name, as -->
	<!-- provided in the source material. -->
	<xsl:key name="lib-lookup" match="eeb:library" use="eeb:name" />
	<xsl:variable name="library-code" select="document('')/*/eeb:libraries"/>

	<xsl:template match="eeb:libraries" as="xs:libraries">
		<xsl:param name="curr-lib"/>
		<xsl:value-of select="key('lib-lookup', $curr-lib)/eeb:code"/>
	</xsl:template>

	<eeb:libraries>
		<eeb:library>
			<eeb:name>Biblioteca Nazionale Centrale di Firenze</eeb:name>
			<eeb:code>bnc</eeb:code>
			<eeb:geoip>EEBBNCF</eeb:geoip>
		</eeb:library>
		<eeb:library>
			<eeb:name>Bibliothèque nationale de France, Paris</eeb:name>
			<eeb:code>bnf</eeb:code>
		</eeb:library>
		<eeb:library>
			<eeb:name>Det Kongelige Bibliotek / The Royal Library (Copenhagen)</eeb:name>
			<eeb:code>kbd</eeb:code>
			<eeb:geoip>EEBKBDK</eeb:geoip>
		</eeb:library>
		<eeb:library>
			<eeb:name>Koninklijke Bibliotheek, Nationale bibliotheek van Nederland</eeb:name>
			<eeb:code>kbn</eeb:code>
			<eeb:geoip>EEBKBNL</eeb:geoip>
		</eeb:library>
		<eeb:library>
			<eeb:name>The Wellcome Library, London</eeb:name>
			<eeb:code>wel</eeb:code>
			<eeb:geoip>EEBWellcomeTrust</eeb:geoip>
		</eeb:library>
	</eeb:libraries>


	<!--
	Date handling for EEB. Where we have start and end date values in the source,
	use them. Otherwise, try to extract a year from the displaydate element and
	use it as the basis for generating the normalised, machine-readable dates that
	PQIS needs to allow date sorting and searching.
	-->

	<xsl:template name="fix-start-date">
		<xsl:param name="display-date" />
		<xsl:variable name="year">
			<xsl:call-template name="extract-year-from-displaydate">
				<xsl:with-param name="display-date" select="$display-date" />
			</xsl:call-template>
		</xsl:variable>
		<xsl:value-of select="$year" /><xsl:text>0101</xsl:text>
	</xsl:template>

	<xsl:template name="fix-end-date">
		<xsl:param name="display-date" />
		<xsl:variable name="end-date">
			<xsl:call-template name="fix-start-date">
				<xsl:with-param name="display-date" select="$display-date" />
			</xsl:call-template>
		</xsl:variable>
		<xsl:value-of select="regexp:replace($end-date, '0101$', 'g', '1231')" />
	</xsl:template>

	<xsl:template name="extract-year-from-displaydate">
		<xsl:param name="display-date" />
		<xsl:for-each select="regexp:match($display-date, '\d{4}')">
			<xsl:value-of select="." />
		</xsl:for-each>
	</xsl:template>

</xsl:stylesheet>
