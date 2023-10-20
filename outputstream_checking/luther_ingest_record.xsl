<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet xmlns:xsl="http://www.w3.org/1999/XSL/Transform" xmlns:xs="http://www.w3.org/2001/XMLSchema" xmlns:l="http://local.data" xmlns:pqfn="http://local/functions" xmlns:ext="http://exslt.org/common" xmlns:dyn="http://exslt.org/dynamic" xmlns:date="http://exslt.org/dates-and-times" xmlns:exsl="http://exslt.org/common" exclude-result-prefixes="dyn l pqfn exsl" extension-element-prefixes="dyn date ext xs exsl" version="1.0">
	<xsl:import href="utils.xsl" />
	<xsl:output method="xml"/>

	<!-- Variables -->

	<!-- NOTE: When passing in a string instead of an xpath, it needs to be
	wrapped in a nodeset: as follows: ext:node-set('CH') -->

	<!-- To add to the ingest record template, you need to define new variable and
	then if needed, a new template, then call the template in the IngestRecord
	block -->

	<xsl:variable name="platformorigin" select="ext:node-set('CH')" />
	<xsl:variable name="productorigin" select="'luther'" />
	<xsl:variable name="originalid">
		<xsl:value-of select="translate(.//@recordid, 'luther-', '')" />
	</xsl:variable>
	<xsl:variable name="prefixid">
		<xsl:value-of select="$productorigin" />-<xsl:value-of select="$originalid" />
	</xsl:variable>
	<xsl:variable name="isbn" select="blank" />
	<xsl:variable name="shelfmark" select="blank" />
	<xsl:variable name="mfnosrch" select="blank" />
	<xsl:variable name="pubid" select="pqfn:getCblid(.//@pubid)" />
	<xsl:variable name="sourcetype" select="'Books'" />
	<xsl:variable name="title" select=".//somhead/mainhead[text() != '']|.//somhead/mnihead[text() != '']" />
	<xsl:variable name="alternatetitle" select="blank" />
	<xsl:variable name="numericdate" select="pqfn:renderNumericDate(.//@pubdate)" />
	<xsl:variable name="displaydate" select=".//@pubdate" />
	<xsl:variable name="numericenddate" select="blank" />
	<xsl:variable name="numericstartdate" select="$numericdate" />
	<xsl:variable name="compdate" select=".//attribs/ymd" />
	<xsl:variable name="language" select="pqfn:getDocumentLanguage(.//attribs/lang)" />
	<xsl:variable name="copyrightdata" select=".//copyrite" />
	<xsl:variable name="startpage" select="pqfn:getPageNumbers(.//pb/@n|.//col/@n)/startpage" />
	<xsl:variable name="endpage" select="pqfn:getPageNumbers(.//pb/@n|.//col/@n)/endpage" />
	<xsl:variable name="pagination" select="pqfn:getPageNumbers(.//pb/@n|.//col/@n)/pagination" />
	<xsl:variable name="objecttype" select=".//@topcomhd" />
	<xsl:variable name="matterobjecttype" select=".//attribs/attsrch" />
	<xsl:variable name="accnum" select=".//attaccno" />
	<xsl:variable name="abstract" select="blank" />
	<xsl:variable name="dpmi" select="blank" />
	<xsl:variable name="dpmicount" select="blank" />
	<xsl:variable name="pdf" select="blank" />
	<xsl:variable name="pdfbytes" select="blank" />
	<!-- <xsl:variable name="keyedfulltext" select="pqfn:getfulltext(.//doc|.//index|.//div1)" /> -->
	<xsl:variable name="keyedfulltext" select="pqfn:getfulltext(/*)" />
	<!-- <xsl:variable name="keyedfulltext" select="blank" /> -->
	<xsl:variable name="imagecomprep" select="pqfn:getImageCompRep(.//IMG|.//figure)" />
	<!-- <xsl:variable name="imagecomprep" select="blank" /> -->
	<xsl:variable name="toc" select="pqfn:getToc(.//@pubid)" />
	<xsl:variable name="documentnote" select="blank" />
	<xsl:variable name="mfextent" select="blank" />
	<xsl:variable name="pubnote" select="blank" />
	<xsl:variable name="physdesc" select="blank" />
	<xsl:variable name="column" select="blank" />
	<xsl:variable name="pubtitle" select="blank" />
	<xsl:variable name="volume" select=".//dochead/pubtitle" />
	<xsl:variable name="issue" select="blank" />
	<xsl:variable name="generalsubj" select="blank" />
	<xsl:variable name="personalSubject" select="blank" />
	<xsl:variable name="geographicSubject" select="blank" />
	<xsl:variable name="companySubject" select="blank" />
	<xsl:variable name="location" select="blank" />
	<xsl:variable name="ncssubj" select="blank" />
	<xsl:variable name="sender" select=".//attribs/sender" />
	<xsl:variable name="recipient" select=".//attribs/address" />
	<xsl:variable name="biblebook" select=".//attribs/attbook" />
	<!-- <xsl:variable name="biblebook" select="blank" /> -->
	<!-- <xsl:variable name="greekkeyword" select=".//greek/nobr[text() != '']" /> -->
	<xsl:variable name="greekkeyword" select="pqfn:checkGreekText(.//greek/nobr[text() != ''])" />
	<!-- <xsl:variable name="greekkeyword" select="blank" /> -->
	<xsl:variable name="publisherorg" select="blank" />
	<xsl:variable name="publishercity" select="blank" />
	<xsl:variable name="publicationseries" select="blank" />
	<xsl:variable name="publicationimprint" select="blank" />
	<xsl:variable name="docfeatures" select="blank" />
	<!-- <xsl:variable name="simpleauthor" select="'Luther, Martin'" /> -->
	<xsl:variable name="authoreditor" select="pqfn:renderAuthorEditor(.//@editor)" />
	<xsl:variable name="birthdate" select="blank" />
	<xsl:variable name="deathdate" select="blank" />
	<xsl:variable name="epithet" select="blank" />
	<xsl:variable name="sourceinstitution" select="blank" />
	<xsl:variable name="nstcnumber" select="blank" />

	<!-- Element templates -->

	<xsl:template name="SourceType">
		<SourceType>
			<xsl:attribute name="SourceTypeOrigin"><xsl:value-of select="$platformorigin" /></xsl:attribute>
			<xsl:value-of select="$sourcetype" />
		</SourceType>
	</xsl:template>

	<xsl:template name="ObjectType">
		<xsl:choose>
			<xsl:when test="$objecttype">
				<xsl:for-each select="$objecttype">
					<ObjectType>
						<xsl:attribute name="ObjectTypeOrigin"><xsl:value-of select="$platformorigin" /></xsl:attribute>
						<xsl:value-of select="pqfn:getLutherDoctype(.)" />
					</ObjectType>
				</xsl:for-each>
			</xsl:when>
			<xsl:otherwise>
				<ObjectType>
					<xsl:attribute name="ObjectTypeOrigin"><xsl:value-of select="$platformorigin" /></xsl:attribute>
					<xsl:text>Register</xsl:text>
				</ObjectType>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="MatterObjectType">
		<xsl:if test="$matterobjecttype">
			<xsl:for-each select="$matterobjecttype">
				<ObjectType>
					<xsl:attribute name="ObjectTypeOrigin"><xsl:value-of select="$platformorigin" /></xsl:attribute>
					<xsl:value-of select="pqfn:getAuthorialEditorialMatter(.)" />
				</ObjectType>
			</xsl:for-each>
		</xsl:if>
	</xsl:template>

	<xsl:template name="Title">
		<xsl:choose>
			<xsl:when test="$title">
				<Title><xsl:value-of select="$title" /></Title>
			</xsl:when>
			<xsl:otherwise>
				<Title>[Synoptische Tabelle]</Title>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="AlternateTitle">
		<xsl:for-each select="ext:node-set($alternatetitle)">
			<AlternateTitle><xsl:value-of select="." /></AlternateTitle>
		</xsl:for-each>
	</xsl:template>

	<xsl:template name="ObjectNumericDate">
		<ObjectNumericDate>
			<xsl:choose>
				<xsl:when test="$numericdate"><xsl:value-of select="$numericdate" /></xsl:when>
				<xsl:otherwise>
					<xsl:attribute name="Undated">true</xsl:attribute>
					<xsl:text>00010101</xsl:text>
				</xsl:otherwise>
			</xsl:choose>
		</ObjectNumericDate>
	</xsl:template>

	<xsl:template name="ObjectEndDate">
		<xsl:if test="$numericenddate">
			<ObjectEndDate>
				<xsl:value-of select="$numericenddate" />
			</ObjectEndDate>
		</xsl:if>
	</xsl:template>

	<xsl:template name="ObjectStartDate">
		<xsl:if test="$numericstartdate">
			<ObjectStartDate>
				<xsl:value-of select="$numericstartdate" />
			</ObjectStartDate>
		</xsl:if>
	</xsl:template>

	<xsl:template name="DisplayDate">
		<xsl:choose>
			<xsl:when test="$displaydate">
				<ObjectRawAlphaDate><xsl:value-of select="$displaydate" /></ObjectRawAlphaDate>
			</xsl:when>
			<xsl:otherwise>
				<ObjectAlphaDate>
					<xsl:attribute name="Undated">true</xsl:attribute>
					<xsl:text>Jan 1, 1</xsl:text>
				</ObjectAlphaDate>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="Language">
		<Language>
			<RawLang>
				<xsl:call-template name="match_or_default">
					<xsl:with-param name="match_field" select="$language" />
					<xsl:with-param name="default_value" select="'English'" />
				</xsl:call-template>
			</RawLang>
		</Language>
	</xsl:template>

	<xsl:template name="CopyrightData">
		<xsl:choose>
			<xsl:when test="$copyrightdata">
				<Copyright>
					<CopyrightData HTMLContent="true">
						<xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
						<xsl:value-of select="$copyrightdata" />
						<xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
					</CopyrightData>
				</Copyright>
			</xsl:when>
			<xsl:otherwise>
				<Copyright>
					<CopyrightData HTMLContent="true">
						<xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
						<xsl:text>Die Originalausgabe der Werke von D. Martin Luther (Weimarer Ausgabe) wird seit 1883 ver&#246;ffentlicht und unterliegt dem Copyright &#169; des Verlages Hermann B&#246;hlaus Nachfolger Weimar GmbH &amp; Co. / The first edition of the works of Dr. Martin Luther (Weimar Edition) has been published since 1883 and is the copyright &#169; of Verlag Hermann B&#246;hlaus Nachfolger Weimar GmbH &amp; Co.</xsl:text>
						<xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
					</CopyrightData>
				</Copyright>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template name="PrintLocation">
		<xsl:if test="$startpage or $endpage or $pagination or $column">
			<PrintLocation>
				<xsl:call-template name="StartPage" />
				<xsl:call-template name="EndPage" />
				<xsl:call-template name="Pagination" />
				<xsl:call-template name="ColumnNumber" />
			</PrintLocation>
		</xsl:if>
	</xsl:template>

	<xsl:template name="StartPage">
		<xsl:if test="$startpage">
			<StartPage>
				<xsl:value-of select="$startpage" />
			</StartPage>
		</xsl:if>
	</xsl:template>

	<xsl:template name="EndPage">
		<xsl:if test="$endpage">
			<EndPage>
				<xsl:value-of select="$endpage" />
			</EndPage>
		</xsl:if>
	</xsl:template>

	<xsl:template name="Pagination">
		<xsl:if test="$pagination">
			<Pagination>
				<xsl:value-of select="$pagination" />
			</Pagination>
		</xsl:if>
	</xsl:template>

	<xsl:template name="ColumnNumber">
		<xsl:if test="$column">
			<ColumnNumber>
				<xsl:value-of select="$column" />
			</ColumnNumber>
		</xsl:if>
	</xsl:template>

	<xsl:template name="ObjectIDs">
		<ObjectIDs>
			<xsl:if test="$isbn">
				<ObjectID IDType="DocISBN">
					<xsl:value-of select="$isbn" />
				</ObjectID>
			</xsl:if>
			<ObjectID IDType="CHLegacyID" IDOrigin="CH">
				<xsl:value-of select="$prefixid" />
			</ObjectID>
			<ObjectID IDType="CHOriginalLegacyID" IDOrigin="CH">
				<xsl:value-of select="$originalid" />
			</ObjectID>
			<xsl:if test="$shelfmark">
				<ObjectID IDType="Shelfmark" IDOrigin="CH">
					<xsl:value-of select="$shelfmark" />
				</ObjectID>
			</xsl:if>
			<xsl:if test="$accnum">
				<ObjectID IDType="AccNum" IDOrigin="CH">
					<xsl:value-of select="$accnum" />
				</ObjectID>
			</xsl:if>
			<xsl:if test="$nstcnumber">
				<ObjectID IDType="NSTCNumber" IDOrigin="CH">
					<xsl:value-of select="$nstcnumber" />
				</ObjectID>
			</xsl:if>
		</ObjectIDs>
	</xsl:template>

	<xsl:template name="ComponentAbstract">
		<xsl:if test="$abstract">
			<Component ComponentType="Abstract">
				<Representation RepresentationType="Abstract">
					<MimeType>text/xml</MimeType>
					<Resides>FAST</Resides>
				</Representation>
			</Component>
		</xsl:if>
    </xsl:template>


	<xsl:template name="DisplayAbstract">
		<xsl:if test="$abstract">
			<Abstract>
				<xsl:attribute name="AbstractType">Summary</xsl:attribute>
				<AbsText HTMLContent="true">
					<xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
					<xsl:apply-templates select="$abstract" />
					<xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
				</AbsText>
			</Abstract>
		</xsl:if>
    </xsl:template>

	<xsl:template name="Contributors">
		<xsl:if test="$authoreditor">
			<Contributors>
				<xsl:call-template name="Contributor" />
			</Contributors>
		</xsl:if>
	</xsl:template>

	<xsl:template name="Contributor">
		<xsl:for-each select="$authoreditor/contributor">
			<Contributor>
				<xsl:attribute name="ContribRole"><xsl:value-of select="./role" /></xsl:attribute>
				<xsl:attribute name="ContribOrder"><xsl:value-of select="./order" /></xsl:attribute>
					<OriginalForm>
						<xsl:value-of select="./name" />
					</OriginalForm>
					<MappedNormalizedForm>
						<xsl:value-of select="./name" />
					</MappedNormalizedForm>
			</Contributor>
		</xsl:for-each>
	</xsl:template>

	<xsl:template name="Editor">
		<xsl:for-each select="$editor">
			<Contributor  ContribRole="Editor">
				<xsl:attribute name="ContribOrder"><xsl:value-of select="position()" /></xsl:attribute>
					<OriginalForm>
						<xsl:value-of select="." />
					</OriginalForm>
					<MappedNormalizedForm>
						<xsl:value-of select="." />
					</MappedNormalizedForm>
			</Contributor>
		</xsl:for-each>
	</xsl:template>

	<xsl:template name="SourceInstitution">
		<xsl:for-each select="$sourceinstitution">
			<Contributor>
				<xsl:attribute name="DoNotNormalize"><xsl:value-of select="'Y'"/></xsl:attribute>
				<xsl:attribute name="ContribRole">SourceInstitution</xsl:attribute>
				<xsl:attribute name="ContribOrder"><xsl:value-of select="position()" /></xsl:attribute>
					<LastName><xsl:value-of select="." /></LastName>
					<OriginalForm>
						<xsl:value-of select="." />
					</OriginalForm>
			</Contributor>
		</xsl:for-each>
	</xsl:template>


	<xsl:template name="BirthDate">
		<xsl:if test="pqfn:birthdate($birthdate)" >
			<BirthDate>
				<xsl:value-of select="pqfn:birthdate($birthdate)" />
			</BirthDate>
		</xsl:if>
	</xsl:template>

	<xsl:template name="DeathDate">
		<xsl:if test="pqfn:deathdate($deathdate)" >
			<DeathDate>
				<xsl:value-of select="pqfn:deathdate($deathdate)" />
			</DeathDate>
		</xsl:if>
	</xsl:template>

	<xsl:template name="ContribDesc">
		<xsl:for-each select="$epithet" >
			<ContribDesc>
				<xsl:value-of select="$epithet" />
			</ContribDesc>
		</xsl:for-each>
	</xsl:template>

	<xsl:template name="DateInfo">
		<xsl:if test="$compdate and pqfn:checkDateFormat($compdate)">
			<DateInfo>
				<NumDates NumDateType='PublicationDateFirstPub'>
					<xsl:value-of select="$compdate" />
				</NumDates>
			</DateInfo>
		</xsl:if>
	</xsl:template>

	<xsl:template name="TableOfContents">
		<xsl:if test="$toc">
			<TableOfContents>
				<xsl:copy-of select="$toc" />
			</TableOfContents>
		</xsl:if>
	</xsl:template>

	<xsl:template name="Notes">
		<xsl:if test="$compdate and pqfn:renderDateCompositionNote($compdate)">
			<Notes>
				<!-- <xsl:for-each select="ext:node-set($documentNote)">
					<xsl:call-template name="Note">
					<xsl:with-param name="type" select="'Document'" />
					<xsl:with-param name="content" select="." />
					</xsl:call-template>
				</xsl:for-each> -->
				<xsl:call-template name="Note">
					<xsl:with-param name="type" select="'Publication'" />
					<xsl:with-param name="content" select="ext:node-set(pqfn:renderDateCompositionNote($compdate))" />
				</xsl:call-template>
				<!-- <xsl:for-each select="ext:node-set($physDescNote)">
					<xsl:call-template name="Note">
					<xsl:with-param name="type" select="'PhysDesc'" />
					<xsl:with-param name="content" select="." />
					</xsl:call-template>
				</xsl:for-each>
				<xsl:for-each select="ext:node-set($mfextent)">
					<xsl:call-template name="Note">
					<xsl:with-param name="type" select="'Document'" />
					<xsl:with-param name="content" select="." />
					</xsl:call-template>
				</xsl:for-each> -->
			</Notes>
		</xsl:if>
	</xsl:template>


	<xsl:template name="Note">
		<xsl:param name="type" />
		<xsl:param name="content" />
		<Note HTMLContent="true">
			<xsl:attribute name="NoteType"><xsl:value-of select="$type"/></xsl:attribute>
			<xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
				<p>Date of composition / first publication: <xsl:apply-templates select="$content" /></p>
			<xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
		</Note>
	</xsl:template>


	<xsl:template name="Terms">
		<xsl:if test="$generalsubj or $location or $ncssubj or $sender or $recipient or $biblebook or $greekkeyword" >
			<Terms>
				<xsl:call-template name="CompanyTerm" />
				<xsl:call-template name="PersonalTerm" />
				<xsl:call-template name="GeographicTerm" />
				<xsl:call-template name="GenSubj" />
				<xsl:call-template name="FlexTerm" />
				<!-- <xsl:call-template name="Term" /> -->
			</Terms>
		</xsl:if>
	</xsl:template>

	<xsl:template name="GenSubj">
		<xsl:for-each select="$generalsubj">
			<GenSubjTerm>
				<GenSubjValue>
					<xsl:value-of select="." />
				</GenSubjValue>
			</GenSubjTerm>
		</xsl:for-each>
	</xsl:template>

	<xsl:template name="FlexTerm">
		<xsl:for-each select="$location">
			<FlexTerm>
			<xsl:attribute name="FlexTermName"><xsl:value-of select="@FlexTermName|../@FlexTermName" /></xsl:attribute>
				<FlexTermValue>
					<xsl:value-of select="." />
				</FlexTermValue>
			</FlexTerm>
		</xsl:for-each>
		<xsl:for-each select="$ncssubj">
			<FlexTerm>
			<xsl:attribute name="FlexTermName"><xsl:value-of select="@FlexTermName" />NSTCMFCollection</xsl:attribute>
				<FlexTermValue>
					<xsl:value-of select="." />
				</FlexTermValue>
			</FlexTerm>
		</xsl:for-each>
		<xsl:for-each select="$sender">
			<FlexTerm>
			<xsl:attribute name="FlexTermName"><xsl:value-of select="@FlexTermName" />Sender</xsl:attribute>
				<FlexTermValue>
					<xsl:value-of select="." />
				</FlexTermValue>
			</FlexTerm>
		</xsl:for-each>
		<xsl:for-each select="$recipient">
			<FlexTerm>
			<xsl:attribute name="FlexTermName"><xsl:value-of select="@FlexTermName" />Recipient</xsl:attribute>
				<FlexTermValue>
					<xsl:value-of select="." />
				</FlexTermValue>
			</FlexTerm>
		</xsl:for-each>
		<xsl:for-each select="$biblebook">
			<FlexTerm>
			<xsl:attribute name="FlexTermName"><xsl:value-of select="@FlexTermName" />BibleBook</xsl:attribute>
				<FlexTermValue>
					<xsl:value-of select="." />
				</FlexTermValue>
			</FlexTerm>
		</xsl:for-each>
		<xsl:for-each select="$greekkeyword">
			<FlexTerm>
			<xsl:attribute name="FlexTermName"><xsl:value-of select="@FlexTermName" />GreekKeyword</xsl:attribute>
				<FlexTermValue>
					<xsl:value-of select="." />
				</FlexTermValue>
			</FlexTerm>
		</xsl:for-each>
	</xsl:template>

	<xsl:template name="CompanyTerm">
		<xsl:for-each select="$companySubject">
				<CompanyTerm>
					<CompanyName><xsl:value-of select="." /></CompanyName>
				</CompanyTerm>
		</xsl:for-each>
	</xsl:template>

	<xsl:template name="PersonalTerm">
		<xsl:for-each select="$personalSubject">
			<Term TermType="Personal">
				<TermValue><xsl:value-of select="." /></TermValue>
			</Term>
		</xsl:for-each>
	</xsl:template>

	<xsl:template name="GeographicTerm">
		<xsl:for-each select="$geographicSubject">
			<Term TermType="Geographic">
				<TermValue><xsl:value-of select="." /></TermValue>
			</Term>
		</xsl:for-each>
	</xsl:template>


	<xsl:template name="KeyedFullText">
		<xsl:if test="$keyedfulltext">
			<TextInfo>
				<Text HTMLContent="true">
					<xsl:text disable-output-escaping="yes">&lt;![CDATA[</xsl:text>
						<xsl:copy-of select="$keyedfulltext" />
					<xsl:text disable-output-escaping="yes">]]&gt;</xsl:text>
				</Text>
			</TextInfo>
		</xsl:if>
	</xsl:template>

	<xsl:template name="ComponentFullText">
		<xsl:if test="$keyedfulltext">
			<Component ComponentType="FullText">
				<Representation RepresentationType="FullText">
					<MimeType>text/xml</MimeType>
					<Resides>FAST</Resides>
				</Representation>
			</Component>
		</xsl:if>
	</xsl:template>

	<xsl:template name="JPG">
		<xsl:for-each select="$imagecomprep">
			<Component ComponentType="InlineImage">
				<mstar_lm_media_id><xsl:value-of select="./imageid"/></mstar_lm_media_id>
				<!-- <mstar_lm_media_id><xsl:value-of select="." /></mstar_lm_media_id> -->
				<InlineImageCount>1</InlineImageCount>
      			<OrderCategory>Illustration</OrderCategory>
				<Order><xsl:value-of select="./order" /></Order>
				<Representation RepresentationType="Full">
					<MimeType>image/jpeg</MimeType>
					<Resides>HMS</Resides>
					<MediaKey>/media<xsl:value-of select="./key" /></MediaKey>
				</Representation>
			</Component>
		</xsl:for-each>
	</xsl:template>

	<xsl:template name="PublicationInfo">
		<xsl:if test="$pubtitle or $volume or $issue or $publisherorg or $publishercity or $publicationseries or $publicationimprint">
			<PublicationInfo>
				<xsl:call-template name="PublicationTitle" />
				<xsl:call-template name="Volume" />
				<xsl:call-template name="Issue" />
				<xsl:call-template name="Series" />
				<xsl:call-template name="Publisher" />
				<xsl:call-template name="Imprint" />
			</PublicationInfo>
		</xsl:if>
	</xsl:template>

	<xsl:template name="PublicationTitle">
		<xsl:if test="$pubtitle">
			<PublicationTitle>
				<xsl:value-of select="$pubtitle" />
			</PublicationTitle>
		</xsl:if>
	</xsl:template>

	<xsl:template name="Volume">
		<xsl:if test="$volume">
			<Volume>
				<xsl:value-of select="$volume" />
			</Volume>
		</xsl:if>
	</xsl:template>

	<xsl:template name="Issue">
		<xsl:if test="$issue">
			<Issue>
				<xsl:value-of select="$issue" />
			</Issue>
		</xsl:if>
	</xsl:template>


	<xsl:template name="Publisher">
		<xsl:if test="$publisherorg or $publishercity">
			<Publisher>
				<xsl:call-template name="OrganizationName" />
				<xsl:call-template name="CityName" />
			</Publisher>
		</xsl:if>
	</xsl:template>

	<xsl:template name="OrganizationName">
		<xsl:if test="$publisherorg">
			<OrganizationName>
				<xsl:value-of select="$publisherorg" />
			</OrganizationName>
		</xsl:if>
	</xsl:template>

	<xsl:template name="CityName">
		<xsl:if test="$publishercity">
			<CityName>
				<xsl:value-of select="$publishercity" />
			</CityName>
		</xsl:if>
	</xsl:template>

	<xsl:template name="Series">
		<xsl:if test="$publicationseries">
			<Series>
				<xsl:value-of select="$publicationseries" />
			</Series>
		</xsl:if>
	</xsl:template>

	<xsl:template name="Imprint">
		<xsl:if test="$publicationimprint">
			<Imprint>
				<xsl:value-of select="$publicationimprint" />
			</Imprint>
		</xsl:if>
	</xsl:template>

	<xsl:template name="PDF">
		<xsl:if test="$pdf">
			<Component ComponentType="FullText">
				<Representation RepresentationType="PDFFullText">
					<MimeType>application/pdf</MimeType>
					<Resides>HMS</Resides>
					<Bytes><xsl:value-of select="$pdfbytes" /></Bytes>
					<PDFType>300PDF</PDFType>
					<MediaKey>/media<xsl:value-of select="$pdf" /></MediaKey>
				</Representation>
			</Component>
		</xsl:if>
	</xsl:template>

	<xsl:template name="DPMI">
		<xsl:if test="$dpmi">
			<Component ComponentType="Pages">
				<PageCount><xsl:value-of select="$dpmicount" /></PageCount>
				<Representation RepresentationType="DPMI">
					<MimeType>text/xml</MimeType>
					<Resides>HMS</Resides>
					<MediaKey>/media<xsl:value-of select="$dpmi" /></MediaKey>
				</Representation>
			</Component>
		</xsl:if>
	</xsl:template>

	<xsl:template name="DocFeatures">
		<xsl:if test="$docfeatures">
			<DocFeatures>
				<xsl:call-template name="DocFeature" />
			</DocFeatures>
		</xsl:if>
	</xsl:template>

	<xsl:template name="DocFeature">
		<xsl:for-each select="$docfeatures">
			<DocFeature>
				<xsl:value-of select="." />
			</DocFeature>
		</xsl:for-each>
	</xsl:template>

	<!-- A template which accepts an input field but has defaults -->
	<xsl:template name="match_or_default">
		<xsl:param name="match_field" />
		<xsl:param name="default_value" />
		<xsl:choose>
			<xsl:when test="$match_field">
				<xsl:value-of select="$match_field" />
			</xsl:when>
			<xsl:otherwise>
				<xsl:value-of select="$default_value" />
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="@*|node()">
		<xsl:copy>
		<xsl:apply-templates select="@*|node()" />
		</xsl:copy>
  	</xsl:template>

	<!-- The main IngestRecord template, matching the whole input record -->
	<xsl:template match="/">
		<IngestRecord>
			<MinorVersion>
				<xsl:call-template name="match_or_default">
					<xsl:with-param name="match_field" select="MinorVersion" />
					<xsl:with-param name="default_value" select="'64'" />
				</xsl:call-template>
			</MinorVersion>
			<ControlStructure>
				<ActionCode>add</ActionCode>
				<LegacyPlatform>MSTAR</LegacyPlatform>
				<LegacyID>
					<xsl:value-of select="$prefixid" />
				</LegacyID>
                    <LastLegacyUpdateTime>
                        <xsl:call-template name="l:timeStamp">
                            <xsl:with-param name="dateString" select="date:date-time()" />
                        </xsl:call-template>
                    </LastLegacyUpdateTime>
				<PublicationInfo>
					<LegacyPubID>
						<xsl:value-of select="$pubid" />
					</LegacyPubID>
				</PublicationInfo>
				<Component ComponentType="Citation">
					<Representation RepresentationType="Citation">
						<MimeType>text/xml</MimeType>
						<Resides>FAST</Resides>
					</Representation>
				</Component>
                <xsl:call-template name="ComponentAbstract" />
				<xsl:call-template name="ComponentFullText" />
				<xsl:call-template name="PDF" />
				<xsl:call-template name="JPG" />
				<xsl:call-template name="DPMI" />
			</ControlStructure>

			<RECORD>
				<Version>Global_Schema_v5.1.xsd</Version>
				<ObjectInfo>
					<xsl:call-template name="SourceType" />
					<xsl:call-template name="ObjectType" />
					<xsl:call-template name="MatterObjectType" />
					<xsl:call-template name="Title" />
					<xsl:call-template name="ObjectNumericDate" />
					<xsl:call-template name="DisplayDate" />
					<xsl:call-template name="Language" />
					<xsl:call-template name="CopyrightData" />
					<xsl:call-template name="PrintLocation" />
					<xsl:call-template name="ObjectIDs" />
					<xsl:call-template name="Contributors" />
					<xsl:call-template name="DateInfo" />
					<xsl:call-template name="TableOfContents" />
					<xsl:call-template name="Notes" />
					<xsl:call-template name="Terms" />
					<xsl:call-template name="KeyedFullText" />
				</ObjectInfo>
				<xsl:call-template name="PublicationInfo" />
			</RECORD>
		</IngestRecord>
	</xsl:template>


<!-- NOTES - delete when no longer needed -->


<!-- <xsl:template match="Contributor|Contributor/item">
		<Contributor>
			<xsl:attribute name="ContribRole"><xsl:value-of select="@ContribRole" /></xsl:attribute>
			<xsl:attribute name="ContribOrder"><xsl:value-of select="position()" /></xsl:attribute>
			<xsl:apply-templates select="./OriginalForm|./ContribAffiliationSummary" />
		</Contributor>
	</xsl:template>

	<xsl:template match="//root/Contributor/OriginalForm|//root/Contributor/item">
		<OriginalForm><xsl:value-of select="." /></OriginalForm>
	</xsl:template>

	<xsl:template match="//root/Contributor/ContribAffiliationSummary">
		<ContribAffiliationSummary><xsl:value-of select="." /></ContribAffiliationSummary>
	</xsl:template>


	<xsl:template match="//root/GenSubjTerm/text()|//root/GenSubjTerm/item">
		<GenSubjTerm>
			<GenSubjValue>
				<xsl:value-of select="." />
			</GenSubjValue>
		</GenSubjTerm>
	</xsl:template>

	<xsl:template match="//root/Term/item|//root/Term/text()">
		<Term>
			<xsl:attribute name="TermType">
				<xsl:value-of select="../@Type" />
			</xsl:attribute>
			<TermValue>
				<xsl:value-of select="." />
			</TermValue>
		</Term>
	</xsl:template>

	<xsl:template match="//root/HistoryTerm/item">
		<HistoryTerm>
			<xsl:attribute name="HistoryTermName">
				<xsl:value-of select="../@TermName" />
			</xsl:attribute>
			<HistoryTermValue>
				<xsl:value-of select="." />
			</HistoryTermValue>
		</HistoryTerm>
	</xsl:template>

	<xsl:template match="//root/FlexTerm/text()|//root/FlexTerm/item">
		<FlexTerm>
			<xsl:attribute name="FlexTermName"><xsl:value-of select="@FlexTermName|../@FlexTermName" /></xsl:attribute>
			<FlexTermValue><xsl:value-of select="." /></FlexTermValue>
		</FlexTerm>
	</xsl:template>

	<xsl:template match="//root/GenericData">
		<GenericData>
			<xsl:attribute name="GenericDataName"><xsl:value-of select="@Type" /></xsl:attribute>
			<xsl:value-of select="." />
		</GenericData>
	</xsl:template> -->


</xsl:stylesheet>
