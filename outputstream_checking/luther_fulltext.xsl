<?xml version="1.0" encoding="UTF-8"?>
<xsl:stylesheet version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:fo="http://www.w3.org/1999/XSL/Format"
	xmlns:d="http://www.w3.org/1999/XSL/Format"
	xmlns:pqfn="http://local/functions" exclude-result-prefixes="fo pqfn">
	<xsl:param name="ProdCode"/>

	<xsl:output method="xml" indent="yes" encoding="UTF-8"/>

	<xsl:template match="hebrew|IMG|figure">
		<div>
			<object class="mstar_link_to_media">
				<param name="mstar_lm_alignment" value="Center"/>
				<param name="mstar_lm_display_control" value="Embed"/>
				<param name="mstar_lm_media_type" value="Illustration"/>
				<param name="mstar_lm_media_id">
					<xsl:attribute name="value">
						<xsl:value-of select="." />
					</xsl:attribute>
				</param>
			</object>
		</div>
	</xsl:template>

	<!-- <xsl:template match="figure">
	<div>
		<object class="mstar_link_to_media">
			<param name="mstar_lm_alignment" value="Center"/>
			<param name="mstar_lm_display_control" value="Embed"/>
			<param name="mstar_lm_media_type" value="Illustration"/>
			<param name="mstar_lm_media_id"><xsl:value-of select="." /></param>
		</object>
	</div>
	</xsl:template> -->


	<xsl:template match="l">
		<xsl:variable name="indent">

		</xsl:variable>
		<div>
			<span>
				<xsl:choose>
					<xsl:when test="@indent">
						<xsl:value-of select="pqfn:indentation(@indent, 'blahh')" />
					</xsl:when>
					<xsl:otherwise>
						<xsl:text />
					</xsl:otherwise>
				</xsl:choose>
			</span>
			<xsl:apply-templates />
		</div>
		<!-- <xsl:variable name="indent" select="@indent"/>
		<xsl:variable name="space" select="pqfn:indentation($indent)" />
		<xsl:choose>
		<xsl:when test="$indent"/>
			<xsl:variable name="space" select="pqfn:indentation($indent)" />
			<div><xsl:value-of select="$space" /></div>
		<xsl:otherwise>
			<div><xsl:apply-templates /></div>
		</xsl:otherwise>
		</xsl:choose> -->
	</xsl:template>

	<xsl:template match="table">
		<table>
			<xsl:apply-templates />
		</table>
		<br/>
	</xsl:template>

	<xsl:template match="row">
		<tr>
			<xsl:apply-templates />
		</tr>
	</xsl:template>

	<xsl:template match="cell">
		<td>
			<xsl:apply-templates />
		</td>
	</xsl:template>

	<xsl:template match="list1|list2|list3">
		<dl>
			<xsl:apply-templates />
		</dl>
	</xsl:template>

	<xsl:template match="list1//headlabl">
		<dt>
			<xsl:apply-templates />
		</dt>
	</xsl:template>

	<xsl:template match="list1//headitem">
		<dd>
			<xsl:apply-templates />
		</dd>
	</xsl:template>

	<xsl:template match="list2//headlabl|list3//headlabl">
		<dt>
			<xsl:apply-templates />
		</dt>
	</xsl:template>

	<xsl:template match="list2//headitem|list3//headitem">
		<dd>
			<xsl:apply-templates />
		</dd>
	</xsl:template>

	<xsl:template match="list1//label|list2//label|list3//label">
		<dt>
			<xsl:apply-templates />
		</dt>
	</xsl:template>

	<xsl:template match="list1//item|list2//item|list3//item">
		<dd>
			<xsl:apply-templates />
		</dd>
	</xsl:template>

	<xsl:template match="attdate|pubtitle">
		<!--Newline needed in Z400000734-->
		<b>
			<xsl:apply-templates />
		</b>
		<br/>
	</xsl:template>

	<xsl:template match="app2">
		<span style="color:red">[			<xsl:apply-templates />
]</span>
	</xsl:template>

	<xsl:template match="app/a|go">
		<b>
			<xsl:apply-templates />
		</b>
	</xsl:template>

	<xsl:template match="x">
		[		<xsl:apply-templates />
]
	</xsl:template>

	<xsl:template match="x1|x">
		<xsl:variable name="rid" select="@rid"/>
		<xsl:variable name="linked_recid" select="pqfn:intradoc_check($rid, ancestor::div)" />
		<xsl:choose>
			<xsl:when test="$linked_recid='href'">
				<b>
					<xsl:value-of select="@text" />
				</b>
				<a>
					<xsl:attribute name="href">#						<xsl:value-of select = "$rid" />
					</xsl:attribute>
					<xsl:value-of select="." />
				</a>
				<br/>
			</xsl:when>
			<xsl:otherwise>
				<div>
					<object class="mstar_link_to_record">
						<param name="mstar_record_id_type" value="luther"/>
						<param name="mstar_record_id" value="{$linked_recid}"/>
						<param name="mstar_record_id_section" value="{$rid}"/>
						<div class="mstar_record_link_text">
							<span style="color:green">
								<xsl:value-of select="@text"/>
							</span>
						</div>
					</object>
				</div>
				<br/>
			</xsl:otherwise>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="target">
		<a hidden="True">
			<xsl:attribute name="id">
				<xsl:value-of select="."/>
			</xsl:attribute>
		</a>
	</xsl:template>


	<xsl:template name="pqp_search">
		<xsl:param name="search_type"/>
		<div style="display:inline" class="pqp_search_element" data-pqp-search-type="{$search_type}"><xsl:apply-templates /></div>
	</xsl:template>

	<xsl:template match="page|pb|col">
		<br/>
		<b>[Seite <xsl:value-of select="@n" />]</b>
		<br/>
	</xsl:template>

	<xsl:template match="list/item|stanza">
		<div>
			<xsl:apply-templates />
		</div>
	</xsl:template>

	<xsl:template match="edit">
		<sup>
			<xsl:apply-templates />
		</sup>
		<br/>
	</xsl:template>

	<xsl:template match="editorname">
		<b>
			<xsl:apply-templates />
		</b>
		<br/>
	</xsl:template>

	<xsl:template match="p">
		<p>
			<xsl:apply-templates />
		</p>
	</xsl:template>

	<xsl:template match="texthead|mainhead|comhd1|comhd2|comhd3|comhd4|comhd5|comhd6|comhd7|comhd8">
		<h4 style="text-align:center;">
			<xsl:apply-templates />
		</h4>
	</xsl:template>

	<xsl:template match="ln|v">
		<span style="color:red">[			<xsl:value-of select="@n" />
] </span>
	</xsl:template>

	<xsl:template match="mark">
		<b>
			<sup>
				<xsl:apply-templates />
			</sup>
		</b>
	</xsl:template>

	<xsl:template match="book|tp|title|imprint|grphead|noteedit">
		<div>
			<xsl:apply-templates />
		</div>
	</xsl:template>

	<xsl:template match="abbrev|ausgab|bl|dochead|entry|greek|side">
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="pp">
		<p>
			<xsl:apply-templates />
		</p>
		<br/>
	</xsl:template>

	<xsl:template match="sp">
		<!--This needs to be in a bigger font-->
		<span style="font-size:2em">
			<xsl:apply-templates/>
		</span>
	</xsl:template>

	<xsl:template match="caption">
		<p style="text-align:center;">
			<xsl:apply-templates/>
		</p>
	</xsl:template>

	<!-- <xsl:template match="attribs/version">
        <p style="text-align:left;"><b><span><xsl:apply-templates></xsl:apply-templates></span></b></p>
    </xsl:template>	 -->

	<xsl:template match="lacuna">
		<xsl:text>[...]</xsl:text>
	</xsl:template>

	<xsl:template match="nobr">
		<xsl:apply-templates />
	</xsl:template>

	<xsl:template match="lb">
		<br/>
	</xsl:template>

	<xsl:template match="gap">
		<xsl:text>&#160;&#160;&#160;&#160;</xsl:text>
	</xsl:template>

	<xsl:template match="margin">
        [		<xsl:apply-templates />
]
	</xsl:template>

	<xsl:template match="dedicat">
		<xsl:call-template name="pqp_search">
			<xsl:with-param name="search_type" select="'dedicat'"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template match="signed">
		<xsl:call-template name="pqp_search">
			<xsl:with-param name="search_type" select="'signature'"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template match="speaker">
		<xsl:call-template name="pqp_search">
			<xsl:with-param name="search_type" select="'speaker'"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template match="argument">
		<xsl:call-template name="pqp_search">
			<xsl:with-param name="search_type" select="'argument'"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template match="poem">
		<xsl:call-template name="pqp_search">
			<xsl:with-param name="search_type" select="'poem'"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template match="epigraph">
		<xsl:call-template name="pqp_search">
			<xsl:with-param name="search_type" select="'epigraph'"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template match="trailer">
		<xsl:call-template name="pqp_search">
			<xsl:with-param name="search_type" select="'trailer'"/>
		</xsl:call-template>
	</xsl:template>

	<xsl:template match="gloss">
		<!--Inline reference is being repeated twice-->
		<xsl:variable name="note_id" select=".//@idref" />
		<div>
			<xsl:attribute name="id">
				<xsl:value-of select="$note_id" />
			</xsl:attribute>
			<div class="pqp_search_element" data-pqp-search-type="note">
				<xsl:apply-templates />
			</div>
		</div>
	</xsl:template>

	<xsl:template match="app">
		<!--div element is putting everything between the square brackets on new lines-->
		<span style="color:red">[<xsl:call-template name="pqp_search"><xsl:with-param name="search_type" select="'apparat'"/><xsl:apply-templates /></xsl:call-template>]</span>
		<br/>
	</xsl:template>

	<xsl:template match="app1">
		<b>[			<xsl:call-template name="pqp_search">
				<xsl:with-param name="search_type" select="'apparat'"/>
				<xsl:apply-templates />
			</xsl:call-template>]
		</b>
	</xsl:template>

	<xsl:template match="anote">
		<span style="color:green">
			<small>[				<xsl:call-template name="pqp_search">
					<xsl:with-param name="search_type" select="'apparat'"/>
					<xsl:apply-templates />
				</xsl:call-template>]
			</small>
		</span>
	</xsl:template>

	<xsl:template match="enote">
		<span style="color:red">
			<small>[				<xsl:call-template name="pqp_search">
					<xsl:with-param name="search_type" select="'apparat'"/>
					<xsl:apply-templates />
				</xsl:call-template>]
			</small>
		</span>
		<br/>
	</xsl:template>

	<xsl:template match="note">
		<xsl:variable name="note_id" select=".//@idref" />
		<div>
			<xsl:attribute name="id">
				<xsl:value-of select="$note_id" />
			</xsl:attribute>
			<div class="pqp_search_element" data-pqp-search-type="apparat">
				<xsl:apply-templates />
			</div>
		</div>
	</xsl:template>

	<xsl:template match="cit">
		<!--div element is putting everything between the square brackets on new lines-->
		<!--If the fix doesn't work, consider using 'normalise-space'-->
		<span style="color:blue">[<xsl:call-template name="pqp_search"><xsl:with-param name="search_type" select="'bibleref'"/><xsl:apply-templates /></xsl:call-template>]</span>
	</xsl:template>

	<xsl:template match="hi">
		<xsl:choose>
			<xsl:when test='@r = "gothic"'>
				<b>
					<xsl:apply-templates />
				</b>
			</xsl:when>
			<xsl:when test='@r = "bold"'>
				<b>
					<xsl:apply-templates />
				</b>
			</xsl:when>
			<xsl:when test='@r = "smcap"'>
				<b>
					<xsl:apply-templates />
				</b>
			</xsl:when>
			<xsl:when test='@r = "roman"'>
				<xsl:apply-templates />
			</xsl:when>
			<xsl:when test='@r = "italic"'>
				<i>
					<xsl:apply-templates />
				</i>
			</xsl:when>
			<xsl:when test='@r = "boldgo"'>
				<b>
					<xsl:apply-templates />
				</b>
			</xsl:when>
			<xsl:when test='@r = "smcapit"'>
				<i>
					<xsl:apply-templates />
				</i>
			</xsl:when>
			<xsl:when test='@r = "smcapgo"'>
				<b>
					<xsl:apply-templates />
				</b>
			</xsl:when>
			<xsl:when test='@r = "uline"'>
				<u>
					<xsl:apply-templates />
				</u>
			</xsl:when>
			<xsl:when test='@r = "small"'>
				<small>
					<xsl:apply-templates />
				</small>
			</xsl:when>
			<xsl:when test='@r = "score"'>
				<xsl:apply-templates />
			</xsl:when>
			<xsl:when test='@r = "italgo"'>
				<i>
					<b>
						<xsl:apply-templates />
					</b>
				</i>
			</xsl:when>
		</xsl:choose>
	</xsl:template>

	<xsl:template match="it">
		<i>
			<xsl:apply-templates />
		</i>
	</xsl:template>

	<xsl:template match="sub">
		<sub>
			<xsl:apply-templates />
		</sub>
	</xsl:template>

	<xsl:template match="sup">
		<sup>
			<xsl:apply-templates />
		</sup>
	</xsl:template>

	<xsl:template match="dt">
		<h>
			<center>
				<xsl:apply-templates/>
			</center>
		</h>
	</xsl:template>

	<xsl:template match="attaccno|attbook|attbook2|attbytes|attvol|attdate2|ymd|ymd2|attsrch|bytes|comhd1|idref|lang|pubtitle|somhead|version" />

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

	<xsl:template match="copyrite" />

</xsl:stylesheet>
