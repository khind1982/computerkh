<?xml version="1.0" encoding="utf-8"?>

<xsl:stylesheet
	version="1.0"
	xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
	xmlns:l="http://local.data">

<!-- Languages -->
	<xsl:key name="lang-lookup" match="l:language" use="l:name" />
	<xsl:variable name="language-code" select="document('')/*/l:languages"/>

	<xsl:template match="l:languages" as="xs:languages">
		<xsl:param name="curr-lang"/>
		<xsl:value-of select="key('lang-lookup', $curr-lang)/l:code"/>
	</xsl:template>

	<l:languages>
		<l:language><l:name>Albanian</l:name><l:code>ALB</l:code></l:language>
		<l:language><l:name>Arabic</l:name><l:code>ARA</l:code></l:language>
		<l:language><l:name>Armenian</l:name><l:code>ARM</l:code></l:language>
		<l:language><l:name>Azerbaijani</l:name><l:code>AZE</l:code></l:language>
		<l:language><l:name>Azeri</l:name><l:code>AZE</l:code></l:language>
		<l:language><l:name>Bahasa Indonesia</l:name><l:code>IND</l:code></l:language>
		<l:language><l:name>Bahasa</l:name><l:code>IND</l:code></l:language>
		<l:language><l:name>Bangla</l:name><l:code>BEN</l:code></l:language>
		<l:language><l:name>Belarusian</l:name><l:code>BEL</l:code></l:language>
		<l:language><l:name>Bengali</l:name><l:code>BEN</l:code></l:language>
		<l:language><l:name>Bosnian</l:name><l:code>BOS</l:code></l:language>
		<l:language><l:name>Bulgarian</l:name><l:code>BUL</l:code></l:language>
		<l:language><l:name>Burmese</l:name><l:code>BUR</l:code></l:language>
		<l:language><l:name>Chaldean</l:name><l:code>CLD</l:code></l:language>
		<l:language><l:name>Chinese</l:name><l:code>CHI</l:code></l:language>
		<l:language><l:name>Creole</l:name><l:code>XXX</l:code></l:language>
		<l:language><l:name>Croatian</l:name><l:code>HRV</l:code></l:language>
		<l:language><l:name>Czech</l:name><l:code>CZE</l:code></l:language>
		<l:language><l:name>Danish</l:name><l:code>DAN</l:code></l:language>
		<l:language><l:name>Dari</l:name><l:code>XXX</l:code></l:language>
		<l:language><l:name>Dutch</l:name><l:code>DUT</l:code></l:language>
		<l:language><l:name>English</l:name><l:code>ENG</l:code></l:language>
		<l:language><l:name>Estonian</l:name><l:code>EST</l:code></l:language>
		<l:language><l:name>Ethiopic</l:name><l:code>GEZ</l:code></l:language>
		<l:language><l:name>Farsi</l:name><l:code>PER</l:code></l:language>
		<l:language><l:name>Finnish</l:name><l:code>FIN</l:code></l:language>
		<l:language><l:name>French</l:name><l:code>FRE</l:code></l:language>
		<l:language><l:name>Georgian</l:name><l:code>GEO</l:code></l:language>
		<l:language><l:name>German</l:name><l:code>GER</l:code></l:language>
		<l:language><l:name>Greek</l:name><l:code>GRE</l:code></l:language>
		<l:language><l:name>Greek, Ancient</l:name><l:code>GRC</l:code></l:language>
		<l:language><l:name>Greek, Modern</l:name><l:code>GRE</l:code></l:language>
		<l:language><l:name>Haitian Creole</l:name><l:code>HAT</l:code></l:language>
		<l:language><l:name>Hebrew</l:name><l:code>HEB</l:code></l:language>
		<l:language><l:name>Hindi</l:name><l:code>HIN</l:code></l:language>
		<l:language><l:name>Hungarian</l:name><l:code>HUN</l:code></l:language>
		<l:language><l:name>Indonesian</l:name><l:code>IND</l:code></l:language>
		<l:language><l:name>Italian</l:name><l:code>ITA</l:code></l:language>
		<l:language><l:name>Japanese</l:name><l:code>JPN</l:code></l:language>
		<l:language><l:name>Kazakh</l:name><l:code>KAZ</l:code></l:language>
		<l:language><l:name>Khmer</l:name><l:code>KHM</l:code></l:language>
		<l:language><l:name>Kirghiz</l:name><l:code>KIR</l:code></l:language>
		<l:language><l:name>Korean</l:name><l:code>KOR</l:code></l:language>
		<l:language><l:name>Kurdish</l:name><l:code>KUR</l:code></l:language>
		<l:language><l:name>Kyrgyz</l:name><l:code>KIR</l:code></l:language>
		<l:language><l:name>Latin</l:name><l:code>LAT</l:code></l:language>
		<l:language><l:name>Macedonian</l:name><l:code>MAC</l:code></l:language>
		<l:language><l:name>Malay</l:name><l:code>MAY</l:code></l:language>
		<l:language><l:name>Mandarin</l:name><l:code>CHI</l:code></l:language>
		<l:language><l:name>Mongolian</l:name><l:code>MON</l:code></l:language>
		<l:language><l:name>Nepalese</l:name><l:code>NEP</l:code></l:language>
		<l:language><l:name>Nepali</l:name><l:code>NEP</l:code></l:language>
		<l:language><l:name>Norwegian</l:name><l:code>NOR</l:code></l:language>
		<l:language><l:name>Pashto</l:name><l:code>PUS</l:code></l:language>
		<l:language><l:name>Persian</l:name><l:code>PER</l:code></l:language>
		<l:language><l:name>Polish</l:name><l:code>POL</l:code></l:language>
		<l:language><l:name>Portuguese</l:name><l:code>POR</l:code></l:language>
		<l:language><l:name>Provencal</l:name><l:code>OCI</l:code></l:language>
		<l:language><l:name>Punjabi</l:name><l:code>PAN</l:code></l:language>
		<l:language><l:name>Romanes</l:name><l:code>ROM</l:code></l:language>
		<l:language><l:name>Romani</l:name><l:code>ROM</l:code></l:language>
		<l:language><l:name>Romanian</l:name><l:code>RUM</l:code></l:language>
		<l:language><l:name>Romany</l:name><l:code>ROM</l:code></l:language>
		<l:language><l:name>Russian</l:name><l:code>RUS</l:code></l:language>
		<l:language><l:name>Samaritan</l:name><l:code>SAM</l:code></l:language>
		<l:language><l:name>Serbian</l:name><l:code>SRP</l:code></l:language>
		<l:language><l:name>Serbo-Croatian</l:name><l:code>HRV</l:code></l:language>
		<l:language><l:name>Sinhala</l:name><l:code>SIN</l:code></l:language>
		<l:language><l:name>Slovak</l:name><l:code>SLO</l:code></l:language>
		<l:language><l:name>Slovene</l:name><l:code>SLV</l:code></l:language>
		<l:language><l:name>Slovenian</l:name><l:code>SLV</l:code></l:language>
		<l:language><l:name>Somali</l:name><l:code>SOM</l:code></l:language>
		<l:language><l:name>Spanish</l:name><l:code>SPA</l:code></l:language>
		<l:language><l:name>Swahili</l:name><l:code>SWA</l:code></l:language>
		<l:language><l:name>Swedish</l:name><l:code>SWE</l:code></l:language>
		<l:language><l:name>Syriac</l:name><l:code>SYR</l:code></l:language>
		<l:language><l:name>Tagalog</l:name><l:code>TGL</l:code></l:language>
		<l:language><l:name>Tajik</l:name><l:code>TGK</l:code></l:language>
		<l:language><l:name>Tamil</l:name><l:code>TAM</l:code></l:language>
		<l:language><l:name>Thai</l:name><l:code>THA</l:code></l:language>
		<l:language><l:name>Tibetan</l:name><l:code>TIB</l:code></l:language>
		<l:language><l:name>Tigrinya</l:name><l:code>TIR</l:code></l:language>
		<l:language><l:name>Turkish</l:name><l:code>TUR</l:code></l:language>
		<l:language><l:name>Ukranian</l:name><l:code>UKR</l:code></l:language>
		<l:language><l:name>Urdu</l:name><l:code>URD</l:code></l:language>
		<l:language><l:name>Uzbek</l:name><l:code>UZB</l:code></l:language>
		<l:language><l:name>Vietnamese</l:name><l:code>VIE</l:code></l:language>
		<l:language><l:name>Welsh</l:name><l:code>WEL</l:code></l:language>
		<l:language><l:name>Zulu</l:name><l:code>ZUL</l:code></l:language>
	</l:languages>
</xsl:stylesheet>
