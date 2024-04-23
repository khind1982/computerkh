<?xml version="1.0" encoding="utf8"?>
<xsl:stylesheet
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:xs="http://www.w3.org/2001/XMLSchema"
	xmlns:l="http://local.data"
	xmlns:pqfn="http://local/functions"
	xmlns:ext="http://exslt.org/common"
	xmlns:dyn="http://exslt.org/dynamic"
	xmlns:date="http://exslt.org/dates-and-times"
	xmlns:exsl="http://exslt.org/common"
	exclude-result-prefixes="dyn l pqfn exsl"
	extension-element-prefixes="dyn date ext xs exsl"
	version="1.0">

	<xsl:import href="eeb-lookups.xsl" />
	<xsl:import href="utils.xsl" />

	<xsl:param name="ProdCode" />
	<xsl:param name="MinVer" />

	<!-- END OF USER TUNABLES! HERE BE DRAGONS. -->
	<!-- Upper cased version of the product code -->
	<xsl:variable name="PRODCODE"
		select="translate($ProdCode, $l:lowerCase, $l:upperCase)" />

	<xsl:variable name="dataSource" select="'CH'" />

	<xsl:output method="xml" indent="yes" encoding="utf-8"
		cdata-section-elements="AbsText" />

	<!--  two possible approaches to allowing user-defined XPaths to be
			evaluated in the template. This should make it possible, with a
			well written stylesheet, to allow users to configure the transform
			to the particular requirements of the content set at hand.

			In either case, such declarations could be constructed from a flat
			text file by the Python app at runtime, making it even simpler for
			users to configure the tool. Testing is needed to assess the possible
			hit on performance of using the dyn:evaluate approach, and if we're
			using flat text files, it's really not necessary, I guess. Nice to
			know it's possible, though.
			-->

	<!-- This is the more traditional approach, but is more verbose so more
			susceptible to typos. -->
	<!-- <xsl:variable name="pageCount" select="count(//itemimagefile1)" /> -->

	<!-- This uses the EXSLT dynamic extension, allowing for simpler
	declarations by the user. -->
	<xsl:variable name="pageCount">count(//itemimagefile1)</xsl:variable>
	<!-- <xsl:variable name="objId" select="rec_search/pqid" /> -->
	<xsl:variable name="objId">rec_search/pqid</xsl:variable>

	<!-- Deduplicate the CERL variant groups using the Meunchian Grouping method
			(http://www.jenitennison.com/xslt/grouping/muenchian.html)
	-->
	<xsl:key name="publisher-name" match="aut_cerl_variant" use="aut_cerl_variant" />
	<xsl:key name="publisher-location" match="pop_cerl_mainentry|pop_cerl_variant"
		use="pop_cerl_mainentry|pop_cerl_variant" />

	<xsl:template match="/rec">
		<!-- VARIABLES EXTRACTED FROM THE INPUT -->
		<!-- <xsl:variable name="objId" select="rec_search/pqid" /> -->
		<xsl:variable name="title" select="rec_search/title" />
		<xsl:variable name="altTitle" select="rec_search/alt_title" />
		<xsl:variable name="docLanguage" select="rec_search/language" />
		<xsl:variable name="sourceLibrary" select="rec_search/source_library" />
		<xsl:variable name="collectionId" select="subscription/unit" />
		<xsl:variable name="docFeatures" select="rec_search/illustrations/illustration" />
		<xsl:variable name="genSubjTerms" select="rec_search/subject" />
		<xsl:variable name="flexTermUSTC" select="rec_search/classification1" />
		<xsl:variable name="USTCNumber" select="rec_search/ustc_number" />
		<xsl:variable name="displayDate" select="rec_search/displaydate" />
		<xsl:variable name="startDate" select="rec_search/startdate" />
		<xsl:variable name="endDate" select="rec_search/enddate" />
		<xsl:variable name="publisherLocation"
			select="rec_search/place_of_publication" />
		<xsl:variable name="publisherCountryName"
			select="rec_search/country_of_publication" />
		<xsl:variable name="publisherOriginalForm"
			select="rec_search/publisher_printer" />
		<xsl:variable name="imprint" select="rec_search/imprint" />
		<xsl:variable name="links" select="linksec/link" />
		<xsl:variable name="physicalDescription" select="rec_search/size" />
		<xsl:variable name="accessionNumber" select="rec_search/bibliographic_reference" />
		<xsl:variable name="shelfmark" select="rec_search/shelfmark" />
		<xsl:variable name="documentNote"
			select="rec_search/general_note|rec_search/content_note" />
		<xsl:variable name="explicitNote" select="rec_search/explicit" />
		<xsl:variable name="incipitNote" select="rec_search/incipit" />
		<xsl:variable name="scanObvs" select="rec_search/commentcode" />
		<xsl:variable name="sectNote" select="rec_search/section_note" />
		<xsl:variable name="pageDetailNote" select="rec_search/page_detail_note" />
		<xsl:variable name="publicationNote" select="rec_search/edition_note" />
		<xsl:variable name="bibRefNote" select="/.." />
		<xsl:variable name="imgColorDef" select="'color'" />

		<xsl:variable name="primaryContributors" 
			select="pqfn:primaryContributors(//author_main|//aut_cerl)"/>
		<xsl:variable name="secondaryContributors" 
			select="pqfn:secondaryContributors(//author_other|//aut_other_cerl)"/>
		
		<!-- dynamic flags to control output of certain sections, such as the
				Notes group. If all the variables are empty or null, this is also
				empty. Reduces the amount of typing to test lots of variables to
				activate an output section. Don't rely on the user to set a flag
				themselves - it's much safer, if a lot more verbose, to do it
				like this. -->

		<xsl:variable name="NotesFlag">
			<xsl:choose>
				<xsl:when test="$links or $physicalDescription or $scanObvs or $sectNote or $pageDetailNote or $explicitNote or $incipitNote">
					<xsl:value-of select="true()" />
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="false()" />
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>

		<xsl:variable name="DocNotesFlag">
			<xsl:choose>
				<xsl:when test="$documentNote or $scanObvs or $sectNote or $pageDetailNote or $explicitNote or $incipitNote">
					<xsl:value-of select="true()" />
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="false()" />
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>

		<!--
		This is a little more explicit in its intent than just splattering
		a load of tests of $Minver all over the place...
		-->
		<xsl:variable name="IncludeCERL">
			<xsl:choose>
				<xsl:when test="number($MinVer) >= 61">
					<xsl:value-of select="true()" />
				</xsl:when>
				<xsl:otherwise>
					<xsl:value-of select="false()" />
				</xsl:otherwise>
			</xsl:choose>
		</xsl:variable>

		<!--
		This calls back to a function in the python code, which returns the values
		extracted from the JSON files as an XML fragment. -->
		<xsl:variable name="bookId">
			<xsl:value-of select="dyn:evaluate($objId)" />
		</xsl:variable>
		<xsl:variable name="hmsKeys" select="pqfn:hmsKeys($bookId)" />

		<xsl:variable name="authorInfo" select="//author_main|//author_other|//aut_cerl|//aut_other_cerl" />

		<IngestRecord>
			<MinorVersion><xsl:value-of select="$MinVer" /></MinorVersion>
			<ControlStructure>
				<ActionCode>add</ActionCode>
				<LegacyPlatform><xsl:value-of select="$dataSource" /></LegacyPlatform>
				<LegacyID>
					<xsl:value-of select="$ProdCode" />-<xsl:value-of select="dyn:evaluate($objId)" />
				</LegacyID>
				<LastLegacyUpdateTime>
					<xsl:call-template name="l:timeStamp">
						<xsl:with-param name="dateString" select="date:date-time()" />
					</xsl:call-template>
				</LastLegacyUpdateTime>
				<xsl:variable name="libcode">
					<xsl:apply-templates select="$library-code">
						<xsl:with-param name="curr-lib" select="$sourceLibrary" />
					</xsl:apply-templates>
				</xsl:variable>
				<PublicationInfo>
					<LegacyPubID>
						<xsl:value-of select="$libcode" />
					</LegacyPubID>
				</PublicationInfo>
				<ObjectBundleData>
					<ObjectBundleType>CHProductCode</ObjectBundleType>
					<ObjectBundleValue>
						<xsl:value-of select="$PRODCODE" />
						<xsl:value-of select="$collectionId" />
					</ObjectBundleValue>
				</ObjectBundleData>
				<xsl:variable name="geoipCode" select="pqfn:geoipCode($libcode)" />
				<xsl:if test="$geoipCode">
					<ObjectBundleData>
						<ObjectBundleType>CHProductCode</ObjectBundleType>
						<ObjectBundleValue>
							<xsl:value-of select="$geoipCode" />
						</ObjectBundleValue>
					</ObjectBundleData>
				</xsl:if>
				<Component ComponentType="Citation">
					<Representation RepresentationType="Citation">
						<MimeType>text/xml</MimeType>
						<Resides>FAST</Resides>
					</Representation>
				</Component>
				<xsl:if test="$hmsKeys/dpmi-key">
					<Component ComponentType="Pages">
						<PageCount>
							<xsl:value-of select="dyn:evaluate($pageCount)" />
						</PageCount>
						<Representation RepresentationType="DPMI">
							<MimeType>text/xml</MimeType>
							<Resides>HMS</Resides>
							<MediaKey>/media<xsl:value-of select="$hmsKeys/dpmi-key" /></MediaKey>
						</Representation>
					</Component>
				</xsl:if>
				<xsl:if test="$hmsKeys/pdf-key or $hmsKeys/thumb-key">
					<Component ComponentType="FullText">
						<xsl:if test="$hmsKeys/pdf-key">
							<Representation RepresentationType="PDFFullText">
								<MimeType>application/pdf</MimeType>
								<Resides>HMS</Resides>
								<Bytes><xsl:value-of select="$hmsKeys/pdf-size" /></Bytes>
								<PDFType>300PDF</PDFType>
								<MediaKey>/media<xsl:value-of select="$hmsKeys/pdf-key" /></MediaKey>
							</Representation>
						</xsl:if>
						<xsl:if test="$hmsKeys/thumb-key">
							<Representation RepresentationType="Thumb">
								<MimeType>image/jpeg</MimeType>
								<Resides>HMS</Resides>
								<Color><xsl:value-of select="$imgColorDef" /></Color>
								<MediaKey>/media<xsl:value-of select="$hmsKeys/thumb-key" /></MediaKey>
							</Representation>
						</xsl:if>
					</Component>
				</xsl:if>
			</ControlStructure>
			<RECORD>
				<Version>Global_Schema_v5.1.xsd</Version>
				<ObjectInfo>
					<SourceType SourceTypeOrigin="{$ProdCode}">Books</SourceType>
					<ObjectType ObjectTypeOrigin="{$ProdCode}">Book</ObjectType>
					<Title><xsl:value-of select="$title" /></Title>
					<xsl:for-each select="$altTitle">
						<AlternateTitle>
							<xsl:value-of select="."  />
						</AlternateTitle>
					</xsl:for-each>
					<xsl:choose>
						<xsl:when test="$startDate">
							<ObjectNumericDate>
								<xsl:value-of select="$startDate" />
							</ObjectNumericDate>
							<ObjectStartDate>
								<xsl:value-of select="$startDate" />
							</ObjectStartDate>
						</xsl:when>
						<xsl:otherwise>
							<ObjectNumericDate>
								<xsl:call-template name="fix-start-date">
									<xsl:with-param name="display-date" select="$displayDate"/>
								</xsl:call-template>
							</ObjectNumericDate>
							<ObjectStartDate>
								<xsl:call-template name="fix-start-date">
									<xsl:with-param name="display-date" select="$displayDate" />
								</xsl:call-template>
							</ObjectStartDate>
						</xsl:otherwise>
					</xsl:choose>
					<xsl:choose>
						<xsl:when test="$endDate">
							<ObjectEndDate>
								<xsl:value-of select="$endDate" />
							</ObjectEndDate>
						</xsl:when>
						<xsl:otherwise>
							<ObjectEndDate>
								<xsl:call-template name="fix-end-date">
									<xsl:with-param name="display-date" select="$displayDate" />
								</xsl:call-template>
							</ObjectEndDate>
						</xsl:otherwise>
					</xsl:choose>
					<ObjectRawAlphaDate>
						<xsl:value-of select="$displayDate" />
					</ObjectRawAlphaDate>
					<PageCount><xsl:value-of select="dyn:evaluate($pageCount)" /></PageCount>
					<xsl:for-each select="$docLanguage">
						<Language>
							<RawLang>
								<xsl:value-of select="." />
							</RawLang>
						</Language>
					</xsl:for-each>
					<Copyright>
						<CopyrightData><xsl:value-of select="$copyrightText" /></CopyrightData>
					</Copyright>
					<PrintLocation>
						<Pagination><xsl:value-of select="rec_search/pagination" /></Pagination>
					</PrintLocation>
					<ObjectIDs>
						<ObjectID IDType="CHLegacyID" IDOrigin="{$dataSource}">
							<xsl:value-of select="$ProdCode" />-<xsl:value-of
								select="dyn:evaluate($objId)" />
						</ObjectID>
						<ObjectID IDType="CHOriginalLegacyID" IDOrigin="{$dataSource}">
							<xsl:value-of select="dyn:evaluate($objId)" />
						</ObjectID>
						<xsl:for-each select="$accessionNumber">
							<ObjectID IDType="AccNum" IDOrigin="{$dataSource}">
								<xsl:value-of select="." />
							</ObjectID>
						</xsl:for-each>
						<xsl:if test="$USTCNumber">
							<ObjectID IDType="USTCNumber" IDOrigin="{$dataSource}">
								<xsl:value-of select="$USTCNumber" />
							</ObjectID>
						</xsl:if>
						<xsl:if test="$shelfmark">
							<ObjectID IDType="Shelfmark" IDOrigin="{$dataSource}">
								<xsl:value-of select="$shelfmark" />
							</ObjectID>
						</xsl:if>
					</ObjectIDs>
					<xsl:if test="$docFeatures">
						<DocFeatures>
							<xsl:for-each select="$docFeatures">
								<DocFeature><xsl:value-of select="." /></DocFeature>
							</xsl:for-each>
						</DocFeatures>
					</xsl:if>
					<Contributors>
						<xsl:for-each select="exsl:node-set($primaryContributors)/result">
							<Contributor ContribRole="Author">
								<xsl:attribute name="ContribOrder">
									<xsl:value-of select="'1'" />
								</xsl:attribute>
								<OriginalForm>
									<xsl:value-of select="./main" />
								</OriginalForm>
								<xsl:if test="./lionid">
									<RefCode RefCodeType="LIONID">
										<xsl:value-of select="./lionid" />
									</RefCode>
								</xsl:if>
								<xsl:if test="./viaf">
									<RefCode>
										<xsl:attribute name="RefCodeType">VIAFID</xsl:attribute>
										<xsl:call-template name="l:getLastSegment">
											<xsl:with-param name="value" select="./viaf" />
											<xsl:with-param name="delimiter" select="'/'" />
										</xsl:call-template>
									</RefCode>
								</xsl:if>
								<xsl:if test="$IncludeCERL = 'true'">
									<xsl:for-each select="./variants/variant">
										<AltOriginalForm>
											<xsl:value-of select="." />
										</AltOriginalForm>
									</xsl:for-each>
								</xsl:if>
							</Contributor>
						</xsl:for-each>
						<xsl:for-each select="exsl:node-set($secondaryContributors)/result">
							<Contributor ContribRole="Author">
								<xsl:attribute name="ContribOrder">
									<xsl:value-of select="position() + 1" />
								</xsl:attribute>
								<OriginalForm>
									<xsl:value-of select="./main" />
								</OriginalForm>								
								<xsl:if test="./lionid">
									<RefCode RefCodeType="LIONID">
										<xsl:value-of select="./lionid" />
									</RefCode>
								</xsl:if>
								<xsl:if test="./viaf">
									<RefCode>
										<xsl:attribute name="RefCodeType">VIAFID</xsl:attribute>
										<xsl:call-template name="l:getLastSegment">
											<xsl:with-param name="value" select="./viaf" />
											<xsl:with-param name="delimiter" select="'/'" />
										</xsl:call-template>
									</RefCode>
								</xsl:if>
								<xsl:if test="$IncludeCERL = 'true'">
									<xsl:for-each select="./variants/variant">
										<AltOriginalForm>
											<xsl:value-of select="." />
										</AltOriginalForm>
									</xsl:for-each>
								</xsl:if>
							</Contributor>
						</xsl:for-each>
					</Contributors>
					<!-- Notes section -->
					<xsl:if test="not($NotesFlag = 'false')">
						<Notes>
							<xsl:for-each select="$physicalDescription">
								<Note NoteType="PhysDesc">
									<xsl:value-of select="." />
								</Note>
							</xsl:for-each>
							<xsl:if test="not($DocNotesFlag = 'false')">
								<Note NoteType="Document" HTMLContent="true">
									<xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
									<xsl:for-each select="$documentNote">
										<p>
											<xsl:value-of select="." />
										</p>
									</xsl:for-each>
									<xsl:for-each select="$scanObvs">
										<p>
											Observations: <xsl:value-of select="." />
										</p>
									</xsl:for-each>
									<xsl:for-each select="$sectNote">
										<p>
											Section Note: <xsl:value-of select="." />
										</p>
									</xsl:for-each>
									<xsl:if test="$pageDetailNote">
										<p>
											Page Detail Note: <xsl:value-of select="$pageDetailNote" />
										</p>
									</xsl:if>
									<xsl:if test="$incipitNote">
										<p>
											<xsl:for-each select="$incipitNote">
												Incipit: <xsl:value-of select="." />
											</xsl:for-each>
										</p>
									</xsl:if>
									<xsl:if test="$explicitNote">
										<p>
											<xsl:for-each select="$explicitNote">
												Explicit: <xsl:value-of select="." />
											</xsl:for-each>
										</p>
									</xsl:if>
									<xsl:if test="$bibRefNote">
										<p>
											Bibliographic reference(s):
										</p>
										<xsl:for-each select="$bibRefNote">
											<p>
												<xsl:value-of select="." />
											</p>
										</xsl:for-each>
									</xsl:if>
									<xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
								</Note>
							</xsl:if>
							<xsl:for-each select="$publicationNote">
								<Note NoteType="Publication">
									<xsl:value-of select="." />
								</Note>
							</xsl:for-each>
							<!-- See note below about this how it works with CDATA -->
							<xsl:if test="$links">
								<Note NoteType="RelatedItem" HTMLContent="true">
									<xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
									<xsl:for-each select="$links">
										<p>
											<object class="mstar_link_to_record">
												<param name="mstar_record_id_type" value="{$ProdCode}" />
												<param name="mstar_record_id" value="{linkid}" />
												<div class="mstar_record_link_text">
													<xsl:value-of select="linktitle" />
												</div>
											</object>
										</p>
									</xsl:for-each>
									<xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
								</Note>
							</xsl:if>
						</Notes>
					</xsl:if>
					<!-- END Notes section -->
					<xsl:if test="$genSubjTerms or $flexTermUSTC">
						<Terms>
							<xsl:for-each select="$genSubjTerms">
								<GenSubjTerm>
									<GenSubjValue><xsl:value-of select="." /></GenSubjValue>
								</GenSubjTerm>
							</xsl:for-each>
							<xsl:for-each select="$flexTermUSTC">
								<FlexTerm FlexTermName="USTC">
									<FlexTermValue><xsl:value-of select="." /></FlexTermValue>
								</FlexTerm>
							</xsl:for-each>
						</Terms>
					</xsl:if>
				</ObjectInfo>
				<PublicationInfo>
					<Publisher>
						<xsl:for-each select="$publisherLocation">
							<xsl:variable name="thisPubLocSeq" select="position()" />
							<CityName>
								<xsl:value-of select="." />
							</CityName>
							<PublisherLocation>
								<xsl:if test="$IncludeCERL = 'true'">
									<xsl:attribute name="Id">
										<xsl:value-of select="$thisPubLocSeq" />
									</xsl:attribute>
								</xsl:if>
								<xsl:value-of select="." />
							</PublisherLocation>
							<xsl:if test="$IncludeCERL = 'true'">
								<xsl:variable name="thisPubLoc" select="." />
								<xsl:variable name="thisPopCerl" select="following-sibling::pop_cerl[1]/*[text() = $thisPubLoc]/.." />
								<xsl:variable name="altPubLoc" select="$thisPopCerl/pop_cerl_variant[not(.=preceding-sibling::pop_cerl_variant)]"/>
								<!-- <xsl:copy-of select="$altPubLoc" /> -->
								<xsl:for-each select="$thisPopCerl/pop_cerl_mainentry|$thisPopCerl/pop_cerl_variant">
									<AltPublisherLocation>
										<xsl:attribute name="Id">
											<xsl:value-of select="$thisPubLocSeq" />
										</xsl:attribute>
										<xsl:value-of select="." />
									</AltPublisherLocation>
								</xsl:for-each>
							</xsl:if>
						</xsl:for-each>
						<xsl:for-each select="$publisherOriginalForm">
							<xsl:variable name="thisOrigFormSeq" select="position()" />
							<OriginalForm>
								<xsl:if test="$IncludeCERL = 'true'">
									<xsl:attribute name="Id">
										<xsl:value-of select="$thisOrigFormSeq" />
									</xsl:attribute>
								</xsl:if>
								<xsl:value-of select="." />
							</OriginalForm>
							<xsl:if test="$IncludeCERL = 'true'">
								<xsl:variable name="thisOrigForm" select="." />
								<xsl:variable name="thisPubCerl" select="following-sibling::pub_cerl[1]/*[text() = $thisOrigForm[text()]]/.." />
								<xsl:for-each select="$thisPubCerl/*">
									<AltOriginalForm>
										<xsl:attribute name="Id">
											<xsl:value-of select="$thisOrigFormSeq" />
										</xsl:attribute>
										<xsl:value-of select="." />
									</AltOriginalForm>
								</xsl:for-each>
							</xsl:if>
						</xsl:for-each>
						<xsl:if test="$publisherCountryName">
							<CountryName>
								<xsl:value-of select="$publisherCountryName" />
							</CountryName>
						</xsl:if>
					</Publisher>
					<xsl:if test="$imprint">
						<Imprint><xsl:value-of select="$imprint" /></Imprint>
					</xsl:if>
				</PublicationInfo>
			</RECORD>
		</IngestRecord>
	</xsl:template>
</xsl:stylesheet>
