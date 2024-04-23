<?xml version="1.0"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:exsl="http://exslt.org/common"
	xmlns:str="http://exslt.org/strings"
	xmlns:l="http://local.data"
	exclude-result-prefixes="exsl l"
	extension-element-prefixes="exsl str" >

	<xsl:import href="utils.xsl" />

	<xsl:output method="xml" indent="yes" encoding="utf-8"/>

	<xsl:template match="rec">

		<xsl:variable name="thisBook" select="itemid" />

		<xsl:variable name="thisBookImages">
			<xsl:call-template name="pageImagesItem">
				<xsl:with-param name="images" select="//itemimagefiles" />
			</xsl:call-template>
		</xsl:variable>

		<mindex>
			<xsl:for-each select="exsl:node-set($thisBookImages)//pageImage">
				<xsl:if test="not(contains(filename, '000-0000T'))">
					<xsl:variable name="pageNumber" select="position()" />
					<comp>
						<xsl:attribute name="type">PG</xsl:attribute>
						<name>
							<xsl:value-of select="$pageNumber"/>
						</name>
						<order>
							<xsl:attribute name="category">PAGE</xsl:attribute>
							<xsl:value-of select="order"/>
						</order>
						<xsl:for-each select="pagecontent">
							<note>
								<xsl:value-of select="."/>
							</note>
						</xsl:for-each>
						<xsl:for-each select="orderlabel">
							<note>Page <xsl:value-of select="."/></note>
						</xsl:for-each>
						<tag>
							<xsl:choose>
								<xsl:when test="str:split(filename, '')[last()] = 'R'">Right</xsl:when>
								<xsl:otherwise>Left</xsl:otherwise>
							</xsl:choose>
						</tag>
						<xsl:for-each select="pagetype">
							<xsl:for-each select="str:split(., '|')">
								<xsl:if test="not(. = 'None')">
									<tag>
										<xsl:value-of select="."/>
									</tag>
								</xsl:if>
							</xsl:for-each>
						</xsl:for-each>
						<rep type="FULL">
							<path>EEB_<xsl:value-of select="filename"/>_<xsl:value-of select="$pageNumber"/>_image+FULL</path>
						</rep>
						<rep type="THUM">
							<path>EEB_<xsl:value-of select="filename"/>_<xsl:value-of select="$pageNumber"/>_image+THUM</path>
						</rep>
					</comp>
				</xsl:if>
			</xsl:for-each>
		</mindex>
	</xsl:template>

	<!-- Extract image information from the //itemimagefiles group -->
	<xsl:template name="pageImagesItem" >
		<xsl:param name="images" />
		<!-- <xsl:param name="thisBook" /> -->
		<pageImages>
			<xsl:for-each select="$images/itemimage">
				<pageImage>
					<filename><xsl:value-of select="itemimagefile1" /></filename>
					<order><xsl:value-of select="order" /></order>
					<imagenumber><xsl:value-of select="imagenumber" /></imagenumber>
					<xsl:if test="orderlabel">
						<orderlabel><xsl:value-of select="orderlabel" /></orderlabel>
					</xsl:if>
					<xsl:for-each select="pagecontent">
						<pagecontent><xsl:value-of select="." /></pagecontent>
					</xsl:for-each>
					<!-- <xsl:if test="pagecontent"> -->
					<!-- 	<pagecontent><xsl:value-of select="pagecontent" /></pagecontent> -->
					<!-- </xsl:if> -->
					<!-- <colour><xsl:value-of select="colour" /></colour> -->
					<pagetype><xsl:value-of select="pagetype" /></pagetype>
				</pageImage>
			</xsl:for-each>
		</pageImages>
	</xsl:template>

	<!-- Extract image information from the //volumeimagefiles group, filtering
			 them using the book ID ($thisBook) to include only edge/cover/ends and
			 images for the current book (-001, -002, -003, ..., -00n) -->
	<xsl:template name="pageImagesVolume" >
		<xsl:param name="images" />
		<xsl:param name="thisBook" />
		<pageImages>
			<xsl:for-each select="$images/volumeimage[contains(volumeimagefile, '-000-') or contains(volumeimagefile, $thisBook)]" >
				<pageImage>
					<filename><xsl:value-of select="volumeimagefile" /></filename>
					<order><xsl:value-of select="order" /></order>
					<imagenumber><xsl:value-of select="imagenumber" /></imagenumber>
					<xsl:if test="orderlabel">
						<orderlabel><xsl:value-of select="orderlabel" /></orderlabel>
					</xsl:if>
					<xsl:for-each select="pagecontent">
						<pagecontent><xsl:value-of select="." /></pagecontent>
					</xsl:for-each>
					<!-- <xsl:if test="pagecontent"> -->
					<!-- 	<pagecontent><xsl:value-of select="pagecontent" /></pagecontent> -->
					<!-- </xsl:if> -->
					<!-- <colour><xsl:value-of select="colour" /></colour> -->
					<pagetype><xsl:value-of select="pagetype" /></pagetype>
				</pageImage>
			</xsl:for-each>
		</pageImages>
	</xsl:template>

</xsl:stylesheet>
