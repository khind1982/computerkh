<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet
	version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:xs="http://www.w3.org/2001/XMLSchema"
	xmlns:date="http://exslt.org/dates-and-times"
	xmlns:l="http://local.data">

  <!-- given a standard ISO date stamp, remove any non-numeric characters
			 to yield a 14-digit number -->
	<xsl:template name="l:timeStamp"> <!-- as="xs:timeStamp"> -->
		<xsl:param name="dateString" />
		<xsl:variable name="tempTimeStamp">
			<xsl:call-template name="l:replace-string">
				<xsl:with-param name="text">
					<xsl:call-template name="l:replace-string">
						<xsl:with-param name="text">
							<xsl:call-template name="l:replace-string">
								<xsl:with-param name="text" select="$dateString" />
								<xsl:with-param name="replace" select="'-'" />
								<xsl:with-param name="with" select="''" />
							</xsl:call-template>
						</xsl:with-param>
						<xsl:with-param name="replace" select="':'" />
						<xsl:with-param name="with" select="''" />
					</xsl:call-template>
				</xsl:with-param>
				<xsl:with-param name="replace" select="'T'" />
				<xsl:with-param name="with" select="''" />
			</xsl:call-template>
		</xsl:variable>
		<xsl:choose>
			<xsl:when test="contains($tempTimeStamp, '+')">
				<xsl:value-of select="substring-before($tempTimeStamp, '+')" />
			</xsl:when>
			<xsl:when test="contains($tempTimeStamp, 'Z')">
				<xsl:value-of select="substring-before($tempTimeStamp, 'Z')" />
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$tempTimeStamp" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="l:replace-string"> <!--as="xs:replace-string">-->
		<xsl:param name="text" />
		<xsl:param name="replace" />
		<xsl:param name="with" />
		<xsl:choose>
			<xsl:when test="contains($text, $replace)">
				<xsl:value-of select="substring-before($text, $replace)" />
				<xsl:value-of select="$with" />
				<xsl:call-template name="l:replace-string">
					<xsl:with-param name="text" select="substring-after($text, $replace)" />
					<xsl:with-param name="replace" select="$replace" />
					<xsl:with-param name="with" select="$with" />
				</xsl:call-template>
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$text" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:variable name="l:upperCase" select="'ABCDEFGHIJKLMNOPQRSTUVWXYZÀÁÂÃÄÅÆÇÈÉÊËÌÍÎÏÐÑÒÓÔÕÖØÙÚÛÜÝÞŸŽŠŒ'" />
	<xsl:variable name="l:lowerCase" select="'abcdefghijklmnopqrstuvwxyzàáâãäåæçèéêëìíîïðñòóôõöøùúûüýþÿžšœ'" />

	<xsl:template name="l:toUpper">
		<xsl:param name="string" />
		<xsl:value-of select="translate($string, $l:lowerCase, $l:upperCase)" />
	</xsl:template>

	<xsl:template name="l:toLower">
		<xsl:param name="string" />
		<xsl:value-of select="translate($string, $l:upperCase, $l:lowerCase)" />
	</xsl:template>


	<!-- Get the last segment of a string, after the final occurrence of
			 $delimiter -->
	<xsl:template name="l:getLastSegment">
		<xsl:param name="value" />
		<xsl:param name="delimiter" select="'.'" />

		<xsl:choose>
			<xsl:when test="contains($value, $delimiter)">
				<xsl:call-template name="l:getLastSegment">
					<xsl:with-param name="value" select="substring-after($value, $delimiter)" />
					<xsl:with-param name="delimiter" select="$delimiter" />
				</xsl:call-template>
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="$value" />
				</xsl:otherwise>
			</xsl:choose>
		</xsl:template>
</xsl:stylesheet>
