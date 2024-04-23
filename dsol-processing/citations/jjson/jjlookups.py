# Assorted lookups used by jjson.py.

def getsearchmappings():
# identifies to which search fields each tag belongs

# order is important here. The search field listed first will be the one under which the tag actually
	# displays in the product; under all other fields the tag will be hidden.
	# So first term should be the field to which the tag specifically belongs; subsequent terms should
	# be for more general search fields.
	
	searchmappings = {
	'740': ['place_keyword'],
	'708': ['illsubj_keyword'],
	'709': ['illsubj_keyword'],
	'210': ['title_keyword'],
	'423': ['name_keyword'],
	'450': ['name_keyword'],
	'334': ['name_keyword'],
	'571': ['name_keyword'],
	'510': ['engraver_lithographer_keyword', 'name_keyword'],
	'700': ['subject_keyword'],
	'330': ['name_keyword'],
	'270': ['title_keyword'],
	'430': ['name_keyword'],
	'572': ['name_keyword'],
	'440': ['name_keyword'],
	'278': ['title_keyword'],
	'582': ['name_keyword'],
	'738': ['illsubj_keyword', 'name_keyword'],
	'690': ['date_keyword'],
	'691': ['date_keyword'],
	'101': ['doctype_keyword'],
	'950': ['shelfmark_keyword'],
	'720': ['illsubj_keyword'],
	'405': ['name_keyword'],
	'730': ['subject_keyword', 'name_keyword'],
	'320': ['name_keyword'],
	'732': ['subject_keyword', 'name_keyword'],
	'340': ['name_keyword'],
	'331': ['name_keyword'],
	'400': ['name_keyword'],
	'421': ['name_keyword'],
	'280': ['eventtitle_keyword', 'title_keyword'],
	'283': ['eventtitle_keyword', 'title_keyword'],
	'282': ['eventtitle_keyword', 'title_keyword'],
	'285': ['eventdate_keyword', 'date_keyword'],
	'284': ['eventvenue_keyword', 'place_keyword'],
	'500': ['name_keyword'],
	'408': ['name_keyword'],
	'353': ['name_keyword'],
	'200': ['title_keyword'],
	'570': ['printer_publisher_keyword', 'name_keyword'],
	'310': ['name_keyword'],
	'205': ['title_keyword'],
	'351': ['name_keyword'],
	'580': ['name_keyword'],
	'581': ['place_keyword', 'name_keyword'],
	'300': ['name_keyword'],
	'301': ['name_keyword'],
	'530': ['printer_publisher_keyword', 'name_keyword'],
	'710': ['illsubj_keyword'],
	'245': ['title_keyword'],
	'501': ['name_keyword'],
	'240': ['title_keyword'],
	'242': ['title_keyword'],
	'505': ['name_keyword'],
	'100': ['doctype_keyword'],
	'224': ['works_advertised_keyword','title_keyword'],
	'223': ['title_keyword'],
	'248': ['title_keyword'],
	'573': ['name_keyword'],
	'220': ['title_keyword'],
	'422': ['name_keyword'],
	'350': ['name_keyword'],
	'420': ['name_keyword'],
	'401': ['name_keyword'],
	'424': ['name_keyword'],
	'724': ['subject_keyword'],
	'354': ['name_keyword'],
	'689': ['date_keyword'],
	'352': ['name_keyword'],
	'438': ['product_keyword', 'name_keyword'],
	'439': ['product_keyword'],
	'436': ['trade_keyword'],
	'437': ['product_keyword'],
	'434': ['place_keyword'],
	'431': ['name_keyword'],
	'432': ['name_keyword'],
	'680': ['printproc_keyword'],
	'290': ['date_keyword'],
	'291': ['place_keyword'],
	'nodate': ['date_keyword'],
	'460': ['name_keyword'],
	'461': ['name_keyword'],
	'800': ['notes'],
	'681': ['printproc_keyword']
	
	}
	
	return searchmappings

def getcatcodes():

	catcodes = {

		'hp': 'hp',		#has prices
		'hc': 'hc',		#has receipt attached
		'ha': 'ha',		#has stamp
		'hd': 'hp|hc',		#has prices and receipt
		'hs': 'hp|ha',		#has prices and stamp
		'oa': 'oa',		#postally used
		'ob': 'ob',		#back not divided
		'oc': 'oc',		#divided back
		'od': 'oc|oe',		#divided back (not postally used)
		'oe': 'oe',		#not postally used
		'om': 'om',		#message on front of card
		'on': 'on',		#message on back of card
		'op': 'oa|oc',		#postally used with divided back
		'oq': 'oa|ob',		#postally used, no divided back
		'ow': 'oe|ob|on',	#not postally used, no divided back,  message on back
		'pp': 'pp',		#has ticket prices
		'pa': 'pa',		#has advertisements
		'pt': 'pp|pa',		#has ticket prices and advertisements
		'pm': 'pm',		#has music
		'pi': 'pp|pm',		#has ticket prices and music
		'pv': 'pa|pm',		#has advertisements and music
		'pd': 'pd',		#has dance
		'pe': 'pp|pd',		#has ticket prices and dance
		'pf': 'pa|pd',		#has advertisements and dance
		'pc': 'pm|pd',		#has music and dance
		'pw': 'pp|pm|pd',	#has ticket prices, music and dance
		'px': 'pa|pm|pd',	#has advertisements, music and dance
		'py': 'pp|pa|pm',	#has ticket prices, advertisements and music
		'pz': 'pp|pa|pm|pd',	#has ticket prices, advertisements, music and dance
		'rp': 'rp',		#has prices
		'rc': 'rc',		#has contents list
		'rd': 'rd',		#has subscription form
		're': 'rp|rc',		#has prices and contents list
		'rf': 'rp|rd',		#has prices and subscription form
		'rg': 'rc|rd',		#has contents list and subscription form
		'rh': 'rp|rc|rd',	#has prices, contents lists, and subscription form
		'ap': 'ap',		#has prices
		'ct': 'ct',		#has terms
		'gr': 'gr',		#has rules
		'bm': 'bm',		#has music
		'tp': 'tp',		#has prices
		'ms': 'ms'		#Entered at Stationer's Hall

		}
	return catcodes

        """
        catcodes = {
                    'pp': 'pt',
		    'pa': 'pa',
		    'pt': 'pt|pa',
		    'pm': 'pm',
		    'pi': 'pt|pm',
		    'pv': 'pa|pm',
		    'pd': 'pd',
		    'pe': 'pt|pd',
		    'pf': 'pa|pd',
		    'pc': 'pm|pd',
		    'pw': 'pt|pm|pd',
		    'px': 'pa|pm|pd',
		    'py': 'pt|pa|pm',
		    'pz': 'pt|pa|pm|pd'
			}
	"""


def getdisplayinfo():
# used to put a display attribute on tags and subtags indicating special formatting rules for display in product

	displaylup = {
		'270$f': 'parens',	#frequency_of_series	Bracket contents of this subfield
		'282$g': 'parens',	#entertainment_genre	Bracket contents of this subfield
		'283$g': 'parens',	#genre_of_forthcoming_ent	Bracket contents of this subfield
		#'300$q': 'parens',	#author_in_ex	Bracket contents of this subfield
		#101		sub_category	Concatenate this field with #100 (#101 then #100)
		#100		category	Concatenate this field with #101 (#101 then #100)
		'282$a': 'parens',	#ent_author	Delete
		'282$c': 'parens',	#composer_of_ent	Delete
		'282$d': 'none',	#dates_of_ent_author	Delete
		'282$i': 'none',	#author_of_ent_if	Delete
		'283$a': 'parens',	#author_of_forthcoming_ent	Delete
		'283$c': 'parens',	#composer_of_forthcoming_ent	Delete
		'283$d': 'none',	#dates_of_forthcoming_ent	Delete
		'283$i': 'none',	#forthcoming_ent_if	Delete
		'284$i': 'none',	#indexed_form_of_venue_of_event	Delete
		'284$x': 'none',	#town_of_venue_if	Delete
		'285$i': 'none',	#date_of_event_indexed_form	Delete
		'290$i': 'none',	#if_of_date_of_composition	Delete
		'291$i': 'none',	#place_of_composition_if	Delete
		'300$u': 'none',	#author_uniform_title	Delete
		'340$u': 'none',	#performer_uniform	Delete
		'689$i': 'none',	#production_date_if	Delete
		'690$i': 'none',	#indexable_form_date_of_pubdate	Delete
		'692': 'none',		#date_type	Delete
		'805': 'none',		#cataloguers_notes	Delete
		#300	$e	author_epithet	Display only if "if" subfield is displayed
		#301	$e	signatory_epithet	Display only if "if" subfield is displayed
		#310	$e	editor_epithet	Display only if "if" subfield is displayed
		#320	$e	translator_epithet	Display only if "if" subfield is displayed
		#330	$e	composer_epithet	Display only if "if" subfield is displayed
		#331	$e	arranger_epithet	Display only if "if" subfield is displayed
		#334	$e	librettist_epithet	Display only if "if" subfield is displayed
		#340	$e	performer_epithet	Display only if "if" subfield is displayed
		#350	$e	producer_director_epithet	Display only if "if" subfield is displayed
		#351	$e	scenery_designer_epithet	Display only if "if" subfield is displayed
		#352	$e	costume_designer_epithet	Display only if "if" subfield is displayed
		#353	$e	lighting_engineer_epithet	Display only if "if" subfield is displayed
		#354	$e	misc_thea_person_epithet	Display only if "if" subfield is displayed
		#400	$e	dedicatee_epithet	Display only if "if" subfield is displayed
		#401	$e	for_benefit_of_epithet	Display only if "if" subfield is displayed
		#420	$e	addresser_epithet	Display only if "if" subfield is displayed
		#421	$e	addressee_epithet	Display only if "if" subfield is displayed
		#424	$e	purchaser_epithet	Display only if "if" subfield is displayed
		#432	$e	advertiser_epithet	Display only if "if" subfield is displayed
		#440	$e	promoter_epithet	Display only if "if" subfield is displayed
		#500	$e	artist_epithet	Display only if "if" subfield is displayed
		#530	$e	printer_epithet	Display only if "if" subfield is displayed
		#570	$e	publisher_epithet	Display only if "if" subfield is displayed
		#571	$e	lessee_epithet	Display only if "if" subfield is displayed
		#573	$e	premises_owner_epithet	Display only if "if" subfield is displayed
		#580	$e	distributor_epithet	Display only if "if" subfield is displayed
		#581	$e	box_office_epithet	Display only if "if" subfield is displayed
		#582	$e	bookseller_epithet	Display only if "if" subfield is displayed
		#300	$i	author_if	Display this subfield if field contains |z 
		#301	$i	signatory_if	Display this subfield if field contains |z and "if" form is present
		#310	$i	editor_if	Display this subfield if field contains |z and "if" form is present
		#320	$i	translator_if	Display this subfield if field contains |z and "if" form is present
		#330	$i	composer_if	Display this subfield if field contains |z and "if" form is present
		#331	$i	arranger_if	Display this subfield if field contains |z and "if" form is present
		#334	$i	librettist_if	Display this subfield if field contains |z and "if" form is present
		#340	$i	performer_if	Display this subfield if field contains |z and "if" form is present
		#350	$i	producer_director_if	Display this subfield if field contains |z and "if" form is present
		#351	$i	scenery_designer_if	Display this subfield if field contains |z and "if" form is present
		#352	$i	costume_designer_if	Display this subfield if field contains |z and "if" form is present
		#353	$i	lighting_engineer_if	Display this subfield if field contains |z and "if" form is present
		#354	$i	misc_thea_person_if	Display this subfield if field contains |z and "if" form is present
		#400	$i	dedicatee_if	Display this subfield if field contains |z and "if" form is present
		#401	$i	for_benefit_of_if	Display this subfield if field contains |z and "if" form is present
		#408	$i	owner_if	Display this subfield if field contains |z and "if" form is present
		#420	$i	addresser_if	Display this subfield if field contains |z and "if" form is present
		#421	$i	addressee_if	Display this subfield if field contains |z and "if" form is present
		#422	$i	inviter_if	Display this subfield if field contains |z and "if" form is present
		#424	$i	purchaser_if	Display this subfield if field contains |z and "if" form is present
		#430	$i	company_if	Display this subfield if field contains |z and "if" form is present
		#432	$i	advertiser_if	Display this subfield if field contains |z and "if" form is present
		#434	$i	town_if	Display this subfield if field contains |z and "if" form is present
		#440	$i	promoter_if	Display this subfield if field contains |z and "if" form is present
		#500	$i	artist_if	Display this subfield if field contains |z and "if" form is present
		#501	$i	designer_if	Display this subfield if field contains |z and "if" form is present
		#505	$i	photographer_if	Display this subfield if field contains |z and "if" form is present
		#510	$i	engraver_lithog_if	Display this subfield if field contains |z and "if" form is present
		#530	$i	printer_indexable_form	Display this subfield if field contains |z and "if" form is present
		#570	$i	publisher_if	Display this subfield if field contains |z and "if" form is present
		#571	$i	lessee_if	Display this subfield if field contains |z and "if" form is present
		#573	$i	premises_owner_if	Display this subfield if field contains |z and "if" form is present
		#580	$i	distributor_if	Display this subfield if field contains |z and "if" form is present
		#581	$i	box_office_if	Display this subfield if field contains |z and "if" form is present
		#582	$i	bookseller_if	Display this subfield if field contains |z and "if" form is present
		'000': 'none',		#id	Do not display any of this field
		'080': 'none',		#copyright_status	Do not display any of this field
		'0rr': 'none',		#record_last_revised	Do not display any of this field
		'0rt': 'none',		#record_tag	Do not display any of this field
		#'200': 'quotes',	#	title	Enclose subfield with quotations
		#'205': 'quotes',	#	title_of_ballad	Enclose subfield with quotations
		#'220': 'quotes',	#	other_alternative_titles	Enclose subfield with quotations
		#'223': 'quotes',	#	alternative_title_when_included_in_main_title	Enclose subfield with quotations
		#'224': 'quotes',	#title_referred_to_from_main_title	Enclose subfield with quotations
		#'245': 'quotes',	#	name_of_tune	Enclose subfield with quotations
		#'270': 'quotes',	#main	series	Enclose subfield with quotations
		#'282': 'quotes',	#main	name_of_entertainment	Enclose subfield with quotations
		#'283': 'quotes',	#main	name_of_forthcoming_ent	Enclose subfield with quotations
		#300	main	author	If there is no |z in the field and no "if" subfield populated then display this subfield
		#301	main	signatory	If there is no |z in the field and no "if" subfield populated then display this subfield
		#310	main	editor	If there is no |z in the field and no "if" subfield populated then display this subfield
		#320	main	translator	If there is no |z in the field and no "if" subfield populated then display this subfield
		#330	main	composer	If there is no |z in the field and no "if" subfield populated then display this subfield
		#331	main	arranger	If there is no |z in the field and no "if" subfield populated then display this subfield
		#334	main	librettist	If there is no |z in the field and no "if" subfield populated then display this subfield
		#340	main	performer	If there is no |z in the field and no "if" subfield populated then display this subfield
		#350	main	producer_or_director	If there is no |z in the field and no "if" subfield populated then display this subfield
		#351	main	scenery_designer_or_painter	If there is no |z in the field and no "if" subfield populated then display this subfield
		#352	main	costume_designer	If there is no |z in the field and no "if" subfield populated then display this subfield
		#353	main	lighting_engineer	If there is no |z in the field and no "if" subfield populated then display this subfield
		#354	main	miscellaneous_theatrical_personnel	If there is no |z in the field and no "if" subfield populated then display this subfield
		#400	main	dedicatee	If there is no |z in the field and no "if" subfield populated then display this subfield
		#401	main	for_the_benefit_of	If there is no |z in the field and no "if" subfield populated then display this subfield
		#405	main	subject_of_elegy	If there is no |z in the field and no "if" subfield populated then display this subfield
		#408	main	owner	If there is no |z in the field and no "if" subfield populated then display this subfield
		#420	main	addresser	If there is no |z in the field and no "if" subfield populated then display this subfield
		#421	main	addressee	If there is no |z in the field and no "if" subfield populated then display this subfield
		#422	main	inviter	If there is no |z in the field and no "if" subfield populated then display this subfield
		#423	main	invitee	If there is no |z in the field and no "if" subfield populated then display this subfield
		#424	main	purchaser	If there is no |z in the field and no "if" subfield populated then display this subfield
		#430	main	company_name	If there is no |z in the field and no "if" subfield populated then display this subfield
		#431	main	alternative_company_names	If there is no |z in the field and no "if" subfield populated then display this subfield
		#432	main	advertiser	If there is no |z in the field and no "if" subfield populated then display this subfield
		#434	main	town	If there is no |z in the field and no "if" subfield populated then display this subfield
		#436	main	trades	If there is no |z in the field and no "if" subfield populated then display this subfield
		#437	main	products	If there is no |z in the field and no "if" subfield populated then display this subfield
		#438	main	brand_names	If there is no |z in the field and no "if" subfield populated then display this subfield
		#439	main	purchases	If there is no |z in the field and no "if" subfield populated then display this subfield
		#440	main	promoter	If there is no |z in the field and no "if" subfield populated then display this subfield
		#450	main	exhibitor	If there is no |z in the field and no "if" subfield populated then display this subfield
		#460	main	criminal	If there is no |z in the field and no "if" subfield populated then display this subfield
		#461	main	victim	If there is no |z in the field and no "if" subfield populated then display this subfield
		#500	main	artist	If there is no |z in the field and no "if" subfield populated then display this subfield
		#501	main	designer	If there is no |z in the field and no "if" subfield populated then display this subfield
		#505	main	photographer	If there is no |z in the field and no "if" subfield populated then display this subfield
		#510	main	engraver_lithographer	If there is no |z in the field and no "if" subfield populated then display this subfield
		#530	main	printer	If there is no |z in the field and no "if" subfield populated then display this subfield
		#570	main	publisher	If there is no |z in the field and no "if" subfield populated then display this subfield
		#571	main	lessee	If there is no |z in the field and no "if" subfield populated then display this subfield
		#572	main	licenser	If there is no |z in the field and no "if" subfield populated then display this subfield
		#573	main	owner_of_premises	If there is no |z in the field and no "if" subfield populated then display this subfield
		#580	main	distributor	If there is no |z in the field and no "if" subfield populated then display this subfield
		#581	main	box_office	If there is no |z in the field and no "if" subfield populated then display this subfield
		#582	main	bookseller	If there is no |z in the field and no "if" subfield populated then display this subfield
		#590	main	extended_imprint	If there is no |z in the field and no "if" subfield populated then display this subfield
		'270$n': 'comma',	#number_in_series	prefix with ",[space]"
		'282$n': 'comma',	#notes	prefix with ",[space]"
		'283$n': 'comma',	#notes_on_forthcoming_ent	prefix with ",[space]"
		'284$a': 'comma',	#address_of_venue	prefix with ",[space]"
		'284$n': 'comma',	#notes_on_venue	prefix with ",[space]"
		'284$t': 'comma',	#venue_of_event_town	prefix with ",[space]"
		'300$a': 'comma',	#address_of_author	prefix with ",[space]"
		'300$d': 'comma',	#dates_of_author	prefix with ",[space]"
		'300$n': 'parens',	#author_notes	prefix with ",[space]"
		'301$a': 'comma',	#address_of_signatory	prefix with ",[space]"
		'301$d': 'comma',	#dates_of_signatory	prefix with ",[space]"
		'301$n': 'parens',	#signatory_notes	prefix with ",[space]"
		'310$d': 'comma',	#dates_of_editor	prefix with ",[space]"
		'310$n': 'parens',	#editor_notes	prefix with ",[space]"
		'320$d': 'comma',	#dates_of_translator	prefix with ",[space]"
		'330$a': 'comma',	#address_of_composer	prefix with ",[space]"
		'330$d': 'comma',	#dates_of_composer	prefix with ",[space]"
		'330$n': 'parens',	#composer_notes	prefix with ",[space]"
		'331$d': 'comma',	#dates_of_arranger	prefix with ",[space]"
		'331$n': 'parens',	#arranger_notes	prefix with ",[space]"
		'334$d': 'comma',	#dates_of_librettist	prefix with ",[space]"
		'334$n': 'parens',	#librettist_notes	prefix with ",[space]"
		'340$a': 'comma',	#address_of_performer	prefix with ",[space]"
		'340$d': 'comma',	#dates_of_performer	prefix with ",[space]"
		'340$n': 'parens',	#performer_notes 	prefix with ",[space]"
		'340$o': 'comma',	#performer_occupation	prefix with ",[space]"
		'350$d': 'comma',	#producer_director_dates	prefix with ",[space]"
		'350$n': 'parens',	#producer_director_notes	prefix with ",[space]"
		'350$o': 'comma',	#producer_director_occupation	prefix with ",[space]"
		'351$a': 'comma',	#scenery_designer_address	prefix with ",[space]"
		'351$d': 'comma',	#scenery_designer_dates	prefix with ",[space]"
		'351$n': 'parens',	#scenery_designer_notes	prefix with ",[space]"
		'351$o': 'comma',	#scenery_designer_occupation	prefix with ",[space]"
		'352$a': 'comma',	#costume_designer_address	prefix with ",[space]"
		'352$d': 'comma',	#costume_designer_dates	prefix with ",[space]"
		'352$n': 'parens',	#costume_designer_notes	prefix with ",[space]"
		'352$o': 'comma',	#costume_designer_occupation	prefix with ",[space]"
		'353$a': 'comma',	#lighting_engineer_address	prefix with ",[space]"
		'353$n': 'parens',	#lighting_engineer_notes	prefix with ",[space]"
		'353$o': 'comma',	#lighting_engineer_occupation	prefix with ",[space]"
		'354$a': 'comma',	#misc_thea_person_address	prefix with ",[space]"
		'354$d': 'comma',	#misc_thea_person_dates	prefix with ",[space]"
		'354$n': 'parens',	#misc_thea_person_notes	prefix with ",[space]"
		'354$o': 'comma',	#misc_thea_person_occupation	prefix with ",[space]"
		'400$d': 'comma',	#dedicatee_dates	prefix with ",[space]"
		'401$a': 'comma',	#for_benefit_of_address	prefix with ",[space]"
		'401$d': 'comma',	#for_benefit_of_dates	prefix with ",[space]"
		'401$n': 'parens',	#for_benefit_of_notes	prefix with ",[space]"
		'420$n': 'parens',	#addresser_notes	prefix with ",[space]"
		'421$d': 'comma',	#addressee_dates	prefix with ",[space]"
		'424$d': 'comma',	#purchaser_dates	prefix with ",[space]"
		'430$a': 'comma',	#company_address	prefix with ",[space]"
		'430$n': 'parens',	#company_notes	prefix with ",[space]"
		'432$a': 'comma',	#advertiser_address	prefix with ",[space]"
		'432$d': 'comma',	#advertiser_dates	prefix with ",[space]"
		'432$n': 'parens',	#advertiser_notes	prefix with ",[space]"
		'434$a': 'comma',	#town_address	prefix with ",[space]"
		'440$d': 'comma',	#promoter_dates	prefix with ",[space]"
		'500$d': 'comma',	#artist_dates	prefix with ",[space]"
		'500$n': 'parens',	#artist_notes	prefix with ",[space]"
		'505$a': 'comma',	#photographer_address	prefix with ",[space]"
		'505$d': 'comma',	#photographer_dates	prefix with ",[space]"
		'505$n': 'parens',	#photographer_notes	prefix with ",[space]"
		'510$a': 'comma',	#engraver_lithog_address	prefix with ",[space]"
		'510$d': 'comma',	#engraver_lithog_dates	prefix with ",[space]"
		'510$n': 'parens',	#engraver_lithog_notes	prefix with ",[space]"
		'530$a': 'comma',	#printers_address	prefix with ",[space]"
		'530$d': 'comma',	#printer_dates	prefix with ",[space]"
		'530$n': 'parens',	#printer_notes	prefix with ",[space]"
		'570$a': 'comma',	#publisher_address	prefix with ",[space]"
		'570$d': 'comma',	#publisher_dates	prefix with ",[space]"
		'570$n': 'parens',	#publisher_notes	prefix with ",[space]"
		'571$a': 'comma',	#lessee_address	prefix with ",[space]"
		'571$d': 'comma',	#lessee_dates	prefix with ",[space]"
		'571$n': 'parens',	#lessee_notes	prefix with ",[space]"
		'573$d': 'comma',	#premises_owner_dates	prefix with ",[space]"
		'573$n': 'parens',	#premises_owner_notes	prefix with ",[space]"
		'580$a': 'comma',	#distributor_address	prefix with ",[space]"
		'580$d': 'comma',	#distributor_dates	prefix with ",[space]"
		'580$n': 'parens',	#distributor_notes	prefix with ",[space]"
		'581$a': 'comma',	#box_office_address	prefix with ",[space]"
		'581$d': 'comma',	#box_office_dates	prefix with ",[space]"
		'581$n': 'parens',	#box_office_notes	prefix with ",[space]"
		'582$a': 'comma',	#bookseller_address	prefix with ",[space]"
		'582$d': 'comma',	#bookseller_dates	prefix with ",[space]"
		'582$n': 'parens',	#bookseller_notes	prefix with ",[space]"
		'600$d': 'comma',	#dimensions_of_whole_item	prefix with ",[space]"
		'600$p': 'comma',	#number_of_pages	prefix with ",[space]"
		#600	$m	dimensions_to_plate_mark	prefix with ",[space]to plate mark:"
		#'710$t': 'none',	#iconclass_term	leave as is
		#300	$r	author_romans	prefix with "[space]"
		#340	$r	peformer_romans	prefix with "[space]"
		'710$c': 'none',	#iconclass_image_count	do not display
		'710': 'none',		# iconclass - do not display
		'700$x': 'mdash',	#subject_gen	prefix with "[space]&mdash;[space]"
		'700$y': 'mdash',	#subject_chrono	prefix with "[space]&mdash;[space]"
		'700$z': 'mdash',	#subject_geog	prefix with "[space]&mdash;[space]"
		'724$i': 'mdash',	#LCSH_form	prefix with "[space]&mdash;[space]"
		'724$x': 'mdash',	#LCSH_general_subdiv	prefix with "[space]&mdash;[space]"
		'724$y': 'mdash',	#LCSH_chronological_subdiv	prefix with "[space]&mdash;[space]"
		'724$z': 'mdash',	#LCSH_geographical_subdiv	prefix with "[space]&mdash;[space]"
		'730$c': 'mdash',	#pers_name_sub_subdiv	prefix with "[space]&mdash;[space]"
		'730$d': 'mdash',	#pers_name_sub_dates	prefix with "[space]&mdash;[space]"
		'730$e': 'mdash',	#pers_name_sub_epithet	prefix with "[space]&mdash;[space]"
		'730$n': 'mdash',	#pers_name_sub_notes	prefix with "[space]&mdash;[space]"
		'730$q': 'mdash',	#pers_name_sub_in_ex	prefix with "[space]&mdash;[space]"
		'730$r': 'mdash',	#pers_name_sub_romans	prefix with "[space]&mdash;[space]"
		'730$u': 'mdash',	#pers_name_sub_uniform	prefix with "[space]&mdash;[space]"
		'730$x': 'mdash',	#pers_name_sub_gen_subdiv	prefix with "[space]&mdash;[space]"
		'730$y': 'mdash',	#pers_name_sub_chrono	prefix with "[space]&mdash;[space]"
		'730$z': 'mdash',	#pers_name_sub_geog	prefix with "[space]&mdash;[space]"
		'740$i': 'mdash',	#place_name_as_subject_form	prefix with "[space]&mdash;[space]"
		'740$x': 'mdash',	#place_name_as_subject_gen	prefix with "[space]&mdash;[space]"
		'740$y': 'mdash',	#place_name_as_subject_chrono	prefix with "[space]&mdash;[space]"
		'740$z': 'mdash',	#place_name_as_subject_geog	prefix with "[space]&mdash;[space]"
		#224$a	title_referred_to_from_main_title_author	prefix with "[space]by[space]"
		#600$i	page_dimensions	prefix with "[space]Image:[space]"
		#330$o	composer_opus_number	prefix with "[space]op.[space]"
		#460$s	criminal_sentence	prefix with "[space]Sentence:[space]"
		'285$s': 'parens',	#source_of_date_of_event
		'689$s': 'parens',	#production_date_source
		'690$s': 'parens',	#source_of_pubdate
		#090		material_related_codes	See look-ups (on sheet three)
		#091		category_specific_codes	See look-ups (on sheet three)
		#095		production_related_codes	See look-ups (on sheet three)
		#098		country_code	See look-ups (on sheet three)
		'724$v': 'mdash',
		'740$v': 'mdash',
		'340$e': 'comma'

	}
	
	return displaylup


""" This part is for assigning XML tagnames to tag/subtag combinations.
For now I'm assuming it's more convenient to copy this information into the tables for tags and subtags than
to use an SQL table and pull the names out when we generate xml, but I suppose that's inefficient spacewise.
Let's see how it turns out... 
"""

def getfieldlup():

	fieldlup =  {
		'095': 'production_related_codes',
		'100': 'category',
		'101': 'sub_category',
		'102': 'special_feature',
		'200': 'title',
		'205': 'title_of_ballad',
		'210': 'short_title',
		'220': 'other_alternative_titles',
		'223': 'alternative_title_when_included_in_main_title',
		'224': 'title_referred_to_from_main_title',
		'240': 'first_line',
		'242': 'full_text',
		'245': 'name_of_tune',
		'248': 'motto',
		'270': 'series',
		'278': 'source_of_item',
		'282$g': 'entertainment_genre',
		'284': 'event_venue',
		'291': 'place_of_composition',
		'300': 'author',
		'301': 'signatory',
		'310': 'editor',
		'320': 'translator',
		'330': 'composer',
		'331': 'arranger',
		'334': 'librettist',
		'340': 'performer',
		'340$o': 'performer_occupation',
		'350': 'producer_or_director',
		'351': 'scenery_designer_or_painter',
		'352': 'costume_designer',
		'353': 'lighting_engineer',
		'354': 'miscellaneous_theatrical_personnel',
		'400': 'dedicatee',
		'401': 'for_the_benefit_of',
		'405': 'subject_of_elegy',
		'408': 'owner',
		'420': 'addresser',
		'421': 'addressee',
		'422': 'inviter',
		'423': 'invitee',
		'424': 'purchaser',
		'430': 'company_name',
		'431': 'alternative_company_names',
		'432': 'advertiser',
		'434': 'town',
		'436': 'trades',
		'437': 'products',
		'438': 'brand_names',
		'439': 'purchases',
		'440': 'promoter',
		'450': 'exhibitor',
		'500': 'artist',
		'501': 'designer',
		'505': 'photographer',
		'510': 'engraver_lithographer',
		'530': 'printer',
		'570': 'publisher',
		'571': 'lessee',
		'572': 'licenser',
		'573': 'owner_of_premises',
		'580': 'distributor',
		'581': 'box_office',
		'582': 'bookseller',
		'590': 'extended_imprint',
		'600': 'physical_form',
		'680': 'text_printing_process',
		'681': 'illustration_printing_process',
		'690': 'pub_date',
		'691': 'period_of_work',
		'700': 'subject',
		'708': 'illustration_subject',
		'709': 'bookplate_iconography',
		'710': 'iconclass_classification',
		'720': 'loc_thesaurus_graphic_material',
		'724': 'locsh',
		'730': 'locna_personal_name_as_subject',
		'732': 'fictional_character_as_subject',
		'738': 'personal_name_as_subject_of_illustration',
		'740': 'place_name_as_subject',
		'950': 'shelfmark',
		'091': 'category_specific_codes',
		'0rr': 'record_last_revised',
		'282': 'name_of_entertainment',
		'284$i': 'indexed_form_of_venue_of_event',
		'284$t': 'venue_of_event_town',
		'285': 'date_of_event',
		'285$i': 'date_of_event_indexed_form',
		'530$a': 'printer_address',
		'530$i': 'printer_indexable_form',
		'600$d': 'dimensions_of_whole_item',
		'610': 'medium',
		'690$i': 'indexable_form_date_of_pubdate',
		'690$s': 'source_of_pubdate',
		'724$x': 'LCSH_general_subdiv',
		'724$y': 'LCSH_chronological_subdiv',
		'724$z': 'LCSH_geographical_subdiv',
		'080': 'copyright_status',
		'090': 'material_related_codes',
		'098': 'country_code',
		'0cl': 'cataloguing_level',
		'140': 'literary_genre',
		'224$a': 'title_referred_to_from_main_title_author',
		'270$f': 'frequency_of_series',
		'270$n': 'number_in_series',
		'271': 'miscellaneous_numbers_on_item',
		'280': 'name_of_event',
		'282$a': 'ent_author',
		'282$c': 'composer_of_ent',
		'282$d': 'dates_of_ent_author',
		'282$i': 'author_of_ent_if',
		'282$n': 'name_of_entertainment_notes',
		'283': 'name_of_forthcoming_ent',
		'283$a': 'author_of_forthcoming_ent',
		'283$c': 'composer_of_forthcoming_ent',
		'283$d': 'dates_of_forthcoming_ent',
		'283$g': 'genre_of_forthcoming_ent',
		'283$i': 'forthcoming_ent_if',
		'283$n': 'notes_on_forthcoming_ent',
		'284$a': 'address_of_venue',
		'284$n': 'notes_on_venue',
		'284$x': 'town_of_venue_if',
		'285$s': 'source_of_date_of_event',
		'290': 'date_of_composition',
		'290$i': 'if_of_date_of_composition',
		'300$a': 'address_of_author',
		'300$c': 'subdiv_of_corp_name_author',
		'300$d': 'dates_of_author',
		'300$e': 'author_epithet',
		'300$i': 'author_if',
		'300$n': 'author_notes',
		'300$q': 'author_in_ex',
		'300$u': 'author_uniform_title',
		'301$a': 'address_of_signatory',
		'301$d': 'dates_of_signatory',
		'301$e': 'signatory_epithet',
		'301$i': 'signatory_if',
		'301$n': 'signatory_notes',
		'310$d': 'dates_of_editor',
		'310$e': 'editor_epithet',
		'310$i': 'editor_if',
		'310$n': 'editor_notes',
		'310$q': 'editor_in_ex',
		'320$d': 'dates_of_translator',
		'320$e': 'translator_epithet',
		'320$i': 'translator_if',
		'320$q': 'translator_in_ex',
		'330$a': 'address_of_composer',
		'330$d': 'dates_of_composer',
		'330$e': 'composer_epithet',
		'330$i': 'composer_if',
		'330$n': 'composer_notes',
		'330$o': 'composer_opus_number',
		'330$q': 'composer_in_ex',
		'330$u': 'composer_uniform_title',
		'331$d': 'dates_of_arranger',
		'331$e': 'arranger_epithet',
		'331$i': 'arranger_if',
		'331$n': 'arranger_notes',
		'331$q': 'arranger_in_ex',
		'334$d': 'dates_of_librettist',
		'334$e': 'librettist_epithet',
		'334$i': 'librettist_if',
		'334$n': 'librettist_notes',
		'334$q': 'librettist_in_ex',
		'340$a': 'address_of_performer',
		'340$c': 'subdiv_of_corp_name_performer',
		'340$d': 'dates_of_performer',
		'340$e': 'performer_epithet',
		'340$i': 'performer_if',
		'340$n': 'performer_notes', 
		'340$q': 'performer_in_ex',
		'340$r': 'peformer_romans',
		'350$d': 'producer_director_dates',
		'350$e': 'producer_director_epithet',
		'350$i': 'producer_director_if',
		'350$n': 'producer_director_notes',
		'350$o': 'producer_director_occupation',
		'350$q': 'producer_director_in_ex',
		'351$a': 'scenery_designer_address',
		'351$d': 'scenery_designer_dates',
		'351$e': 'scenery_designer_epithet',
		'351$i': 'scenery_designer_if',
		'351$n': 'scenery_designer_notes',
		'351$o': 'scenery_designer_occupation',
		'351$q': 'scenery_designer_in_ex',
		'352$a': 'costume_designer_address',
		'352$d': 'costume_designer_dates',
		'352$e': 'costume_designer_epithet',
		'352$i': 'costume_designer_if',
		'352$n': 'costume_designer_notes',
		'352$o': 'costume_designer_occupation',
		'352$q': 'costume_designer_in_ex',
		'353$a': 'lighting_engineer_address',
		'353$e': 'lighting_engineer_epithet',
		'353$i': 'lighting_engineer_if',
		'353$n': 'lighting_engineer_notes',
		'353$o': 'lighting_engineer_occupation',
		'354$a': 'misc_thea_person_address',
		'354$d': 'misc_thea_person_dates',
		'354$e': 'misc_thea_person_epithet',
		'354$i': 'misc_thea_person_if',
		'354$n': 'misc_thea_person_notes',
		'354$o': 'misc_thea_person_occupation',
		'354$q': 'misc_thea_person_in_ex',
		'400$d': 'dedicatee_dates',
		'400$e': 'dedicatee_epithet',
		'400$i': 'dedicatee_if',
		'401$a': 'for_benefit_of_address',
		'401$d': 'for_benefit_of_dates',
		'401$e': 'for_benefit_of_epithet',
		'401$i': 'for_benefit_of_if',
		'401$n': 'for_benefit_of_notes',
		'401$q': 'for_benefit_of_in_ex',
		'408$i': 'owner_if',
		'420$e': 'addresser_epithet',
		'420$i': 'addresser_if',
		'420$n': 'addresser_notes',
		'421$d': 'addressee_dates',
		'421$e': 'addressee_epithet',
		'421$i': 'addressee_if',
		'422$i': 'inviter_if',
		'424$d': 'purchaser_dates',
		'424$e': 'purchaser_epithet',
		'424$i': 'purchaser_if',
		'430$a': 'company_address',
		'430$i': 'company_if',
		'430$n': 'company_notes',
		'432$a': 'advertiser_address',
		'432$d': 'advertiser_dates',
		'432$e': 'advertiser_epithet',
		'432$i': 'advertiser_if',
		'432$n': 'advertiser_notes',
		'434$a': 'town_address',
		'434$i': 'town_if',
		'440$d': 'promoter_dates',
		'440$e': 'promoter_epithet',
		'440$i': 'promoter_if',
		'500$d': 'artist_dates',
		'500$e': 'artist_epithet',
		'500$i': 'artist_if',
		'500$n': 'artist_notes',
		'500$q': 'artist_in_ex',
		'501$i': 'designer_if',
		'505$a': 'photographer_address',
		'505$d': 'photographer_dates',
		'505$i': 'photographer_if',
		'505$n': 'photographer_notes',
		'510$a': 'engraver_lithog_address',
		'510$d': 'engraver_lithog_dates',
		'510$i': 'engraver_lithog_if',
		'510$n': 'engraver_lithog_notes',
		'530$d': 'printer_dates',
		'530$e': 'printer_epithet',
		'530$n': 'printer_notes',
		'570$a': 'publisher_address',
		'570$d': 'publisher_dates',
		'570$e': 'publisher_epithet',
		'570$i': 'publisher_if',
		'570$n': 'publisher_notes',
		'571$a': 'lessee_address',
		'571$d': 'lessee_dates',
		'571$e': 'lessee_epithet',
		'571$i': 'lessee_if',
		'571$n': 'lessee_notes',
		'571$q': 'lessee_in_ex',
		'573$d': 'premises_owner_dates',
		'573$e': 'premises_owner_epithet',
		'573$i': 'premises_owner_if',
		'573$n': 'premises_owner_notes',
		'580$a': 'distributor_address',
		'580$d': 'distributor_dates',
		'580$e': 'distributor_epithet',
		'580$i': 'distributor_if',
		'580$n': 'distributor_notes',
		'581$a': 'box_office_address',
		'581$d': 'box_office_dates',
		'581$e': 'box_office_epithet',
		'581$i': 'box_office_if',
		'581$n': 'box_office_notes',
		'581$q': 'box_office_in_ex',
		'582$a': 'bookseller_address',
		'582$d': 'bookseller_dates',
		'582$e': 'bookseller_epithet',
		'582$i': 'bookseller_if',
		'582$n': 'bookseller_notes',
		'582$o': 'bookseller_occupation',
		'600$i': 'page_dimensions',
		'600$m': 'dimensions_to_plate_mark',
		'600$p': 'number_of_pages',
		'680$n': 'text_print_process_notes',
		'681$n': 'illus_print_process_notes',
		'689': 'production_date',
		'689$i': 'production_date_if',
		'689$s': 'production_date_source',
		'730$c': 'pers_name_sub_subdiv',
		'730$d': 'pers_name_sub_dates',
		'730$e': 'pers_name_sub_epithet',
		'730$n': 'pers_name_sub_notes',
		'730$q': 'pers_name_sub_in_ex',
		'730$r': 'pers_name_sub_romans',
		'730$u': 'pers_name_sub_uniform',
		'730$x': 'pers_name_sub_gen_subdiv',
		'732$d': 'fict_name_sub_dates',
		'732$e': 'fict_name_sub_epithet',
		'732$n': 'fict_name_sub_notes',
		'732$r': 'fict_name_sub_romans',
		'738$c': 'pers_name_sub_illus_subdiv',
		'738$d': 'pers_name_sub_illus_dates',
		'738$e': 'pers_name_sub_illus_epithet',
		'738$n': 'pers_name_sub_illus_notes',
		'738$q': 'pers_name_sub_illus_in_ex',
		'738$r': 'pers_name_sub_illus_romans',
		'950$c': 'shelfmark_copy_note',
		'950$f': 'shelfmark_film_number',
		'950$p': 'shelfmark_provenance',
		'950$s': 'shelfmark_subsection',
		'800': 'notes',
		'000': 'id',
		'0rt': 'record_tag',
		'143': 'musical_genre',
		'291$i': 'place_of_composition_if',
		'299': 'statement_of_responsibility',
		'300$r': 'author_romans',
		'340$u': 'performer_uniform',
		'460': 'criminal',
		'461': 'victim',
		'460$i': 'criminal_if',
		'460$d': 'dates_of_criminal',
		'460$m': 'crime',
		'460$s': 'sentence',
		'461$i': 'victim_if',
		'461$e': 'victim_epithet',
		'461$d': 'dates_of_victim',
		'460$e': 'criminal_epithet',
		'460$n': 'criminal_notes',
		'460$t': 'criminal_town',
		'460$a': 'criminal_address',
		'460$x': 'criminal_town_if',
		'461$n': 'victim_notes',
		'461$t': 'victim_town',
		'461$x': 'victim_town_if',
		'461$a': 'victim_town',
		'692': 'date_type',
		'700$x': 'subject_gen',
		'700$y': 'subject_chrono',
		'700$z': 'subject_geog',
		'710$c': 'iconclass_image_count',
		'710$t': 'iconclass_term',
		'724$i': 'LCSH_form',
		'730$y': 'pers_name_sub_chrono',
		'730$z': 'pers_name_sub_geog',
		'740$i': 'place_name_as_subject_form',
		'740$x': 'place_name_as_subject_gen',
		'740$y': 'place_name_as_subject_chrono',
		'740$z': 'place_name_as_subject_geog',
		'805': 'cataloguers_notes',
		'809': 'work_description',
		'810': 'bm_number',
		'811': 'franks_number',
		'812': 'foxon_number',
		'814': 'estc_number',
		'815': 'estc_heading',
		'817': 'nister_number',
		'260': 'edition',
		'310$a': 'editor_address',
		'350$a': 'producer_director_address',
		'408$d': 'owner_dates',
		'408$n': 'owner_notes',
		'420$d': 'addresser_dates',
		'421$n': 'addressee_notes',
		'421$q': 'addressee_in_ex',
		'423$d': 'invitee_dates',
		'423$i': 'invitee_if',
		'430$e': 'name_of_company_epithet',
		'450$d': 'exhibitor_dates',
		'450$e': 'exhibitor_epithet',
		'450$i': 'exhibitor_if',
		'450$n': 'exhibitor_notes',
		'450$q': 'exhibitor_in_ex',
		'450$r': 'exhibitor_romans',
		'461$r': 'victim_romans',
		'500$a': 'artist_address',
		'501$a': 'designer_address',
		'501$e': 'designer_epithet',
		'501$n': 'designer_notes',
		'505$q': 'photographer_in_ex',
		'510$e': 'engraver_lithographer_epithet',
		'510$q': 'engraver_lithographer_in_ex',
		'530$q': 'printer_in_ex',
		'500$q': 'artist_in_ex',
		'950$x': 'shelfmark_former_shelfmark',
		'818': 'renier_number',
		'301$q': 'signatory_in_ex',
		'408$a': 'owner_address',
		'408$e': 'owner_epithet',
		'432$q': 'advertiser_in_ex',
		'440$n': 'promoter_notes',
		'440$q': 'promoter_in_ex',
		'570$q': 'publisher_in_ex',
		'582$q': 'bookseller_in_ex',
		'691$s': 'jidi_source',
		'724$v': 'locsh_form',
		'740$v': 'place_name_as_subject_form',

		}

	return fieldlup


def getsomhierarchies():

	hierarchies = {
			'Entertainment':	{
						'titleprior':	[
								'282',
								'200',
								'283',
								'242',
								'248',
								'280'
								],
						'nameprior':	[
								'340',
								'300',
								'330',
								'401',
								'738',
								'571',
								'573',
								'350',
								'351',
								'352',
								'354',
								'581',
								'500',
								'421',
								'301',
								'730',
								'732',
								'440'
								],
						'placeprior':	[
								'284'
								],
						'prodprior':	[],
						'dateprior':	[
								'285',
								'690',
								'691'
								],
						'imgsubjprior':	[
								'720',
								'710',
								'738',
								'708'
								]
						},
			# Temporary default entry for when collection is missing
			'':			{
						'titleprior':	[
								'282',
								'200',
								'283',
								'242',
								'248',
								'280'
								],
						'nameprior':	[
								'340',
								'300',
								'330',
								'401',
								'738',
								'571',
								'573',
								'350',
								'351',
								'352',
								'354',
								'581',
								'500',
								'421',
								'301',
								'730',
								'732',
								'440'
								],
						'placeprior':	[
								'284'
								],
						'prodprior':	[],
						'dateprior':	[
								'285',
								'690',
								'691'
								],
						'imgsubjprior':	[
								'720',
								'710',
								'738',
								'708'
								]
						},
			#Provisional crime hierarchy - copied from Entertainment
			'Crime':		{
						'titleprior':	[
								'282',
								'200',
								'283',
								'242',
								'248',
								'280'
								],
						'nameprior':	[
								'460',
								'461',
								'340',
								'300',
								'330',
								'401',
								'738',
								'571',
								'573',
								'350',
								'351',
								'352',
								'354',
								'581',
								'500',
								'421',
								'301',
								'730',
								'732',
								'440'
								],
						'placeprior':	[
								'284'
								'434'
								],
						'prodprior':	[],
						'dateprior':	[
								'285',
								'690',
								'691'
								],
						'imgsubjprior':	[
								'720',
								'710',
								'738',
								'708'
								]
						},
			'Advertising':		{
						'titleprior':	[
								'200',
								'220',
								'270',
								'278',
								'242',
								'280'
								],
						'nameprior':	[
								'430',
								'432',
								'431',
								'730',
								'732'
								],
						'placeprior':	[
								'434'
								# are subtags going to mess things up?
								# oh yes. deactivate for time being
								#'530$t',
								#'580$t'
								],
						'prodprior':	[
								'437',
								'438'
								],
						'dateprior':	[
								'690',
								'691'
								],
						'imgsubjprior':	[
								'720',
								'710',
								'738',
								'708'
								]
						},
			'Booktrade':		{
						'titleprior':	[
								'224',
								'270',
								'200',
								'220',
								'248',
								'242'
								],
						'nameprior':	[
								'300',
								'310',
								'580',
								'408',
								'730',
								'732'
								],
						'placeprior':	[
								'434',
								#'408$t',
								'740'
								],
						'prodprior':	[],
						'dateprior':	[
								'690',
								'285',
								'691'
								],
						'imgsubjprior':	[
								'710',
								'720',
								'738',
								'709',
								'708'
								]
						},
			'Prints':	{
						'titleprior':	[
								'200',
								'220',
								'270',
								'242'
								],
						'nameprior':	[
								'730',
								'732'
								],
						'placeprior':	[
								'740',
								'530$t',
								'570$t'
								],
						'prodprior':	[],
						'dateprior':	[
								'690',
								'691'
								],
						'imgsubjprior':	[
								'710',
								'720',
								'738'
								]
						}
			}
	
	return hierarchies



	"""
		Town of person named rules now superseded
		But it would be a shame to have to recreate all this again if we change our minds...
		(And by 'we' I mean the Bodleian)
		'300$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'301$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'310$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'320$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'330$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'331$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'334$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'340$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'350$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'351$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'352$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'353$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'354$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'400$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'401$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'405$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'408$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'420$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'421$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'422$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'423$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'424$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'430$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'431$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'432$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'434$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'436$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'437$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'438$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'439$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'440$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'450$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'500$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'501$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'505$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'510$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'530$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'570$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'571$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'572$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'573$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'580$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'581$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'582$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'590$t': 'comma',	#town_of_person_named	prefix with "[space],[space]"
		'300$x': 'none',	#if_town_of_person_named	do not display
		'301$x': 'none',	#if_town_of_person_named	do not display
		'310$x': 'none',	#if_town_of_person_named	do not display
		'320$x': 'none',	#if_town_of_person_named	do not display
		'330$x': 'none',	#if_town_of_person_named	do not display
		'331$x': 'none',	#if_town_of_person_named	do not display
		'334$x': 'none',	#if_town_of_person_named	do not display
		'340$x': 'none',	#if_town_of_person_named	do not display
		'350$x': 'none',	#if_town_of_person_named	do not display
		'351$x': 'none',	#if_town_of_person_named	do not display
		'352$x': 'none',	#if_town_of_person_named	do not display
		'353$x': 'none',	#if_town_of_person_named	do not display
		'354$x': 'none',	#if_town_of_person_named	do not display
		'400$x': 'none',	#if_town_of_person_named	do not display
		'401$x': 'none',	#if_town_of_person_named	do not display
		'405$x': 'none',	#if_town_of_person_named	do not display
		'408$x': 'none',	#if_town_of_person_named	do not display
		'420$x': 'none',	#if_town_of_person_named	do not display
		'421$x': 'none',	#if_town_of_person_named	do not display
		'422$x': 'none',	#if_town_of_person_named	do not display
		'423$x': 'none',	#if_town_of_person_named	do not display
		'424$x': 'none',	#if_town_of_person_named	do not display
		'430$x': 'none',	#if_town_of_person_named	do not display
		'431$x': 'none',	#if_town_of_person_named	do not display
		'432$x': 'none',	#if_town_of_person_named	do not display
		'434$x': 'none',	#if_town_of_person_named	do not display
		'436$x': 'none',	#if_town_of_person_named	do not display
		'437$x': 'none',	#if_town_of_person_named	do not display
		'438$x': 'none',	#if_town_of_person_named	do not display
		'439$x': 'none',	#if_town_of_person_named	do not display
		'440$x': 'none',	#if_town_of_person_named	do not display
		'450$x': 'none',	#if_town_of_person_named	do not display
		'500$x': 'none',	#if_town_of_person_named	do not display
		'501$x': 'none',	#if_town_of_person_named	do not display
		'505$x': 'none',	#if_town_of_person_named	do not display
		'510$x': 'none',	#if_town_of_person_named	do not display
		'530$x': 'none',	#if_town_of_person_named	do not display
		'570$x': 'none',	#if_town_of_person_named	do not display
		'571$x': 'none',	#if_town_of_person_named	do not display
		'572$x': 'none',	#if_town_of_person_named	do not display
		'573$x': 'none',	#if_town_of_person_named	do not display
		'580$x': 'none',	#if_town_of_person_named	do not display
		'581$x': 'none',	#if_town_of_person_named	do not display
		'582$x': 'none',	#if_town_of_person_named	do not display
		'590$x': 'none'		#if_town_of_person_named	do not display
	"""



	
"""
booktrade = 
	
Name keyword	'300',
	'301',
	'310',
	'320',
	'330',
	'331',
	'334',
	'340',
	'350',
	'351',
	'352',
	'353',
	'354',
	'400',
	'401',
	'405',
	'408',
	'420',
	'421',
	'422',
	'423',
	'424',
	'430',
	'431',
	'432',
	'438',
	'440',
	'450',
	'500',
	'501',
	'505',
	'510',
	'530',
	'570',
	'571',
	'572',
	'573',
	'580',
	'581',
	'582',
	'730',
	'732',
	'738',
Title/First Line Keyword	'200',
	'205',
	'210',
	'220',
	'223',
	'224',
	'240',
	'242',
	'245',
	'248',
	'270',
	'278',
	'282',
	'283',
Subject Keyword	'282', SUBFIELD $g
	'340', SUBFIELD $o
	'439',
	'700',
	'724',
	'730',
	'732',
Subject of illustration keyword	'708',
	'709',
	'710',
	'720',
	'738',
Place Keyword	'284',
	'291',
	'434',
	'740',
	$t (or, if present, $x overrides $t) subfield from any '3xx',, '4xx', and '5xx', field.
Document type	'100',
	'101',
Printing process	'680',
Limit to printing process of illustrations	'681',
Printer/Engraver	'530',
	'510',
Date	'285',
	'290',
	'689',
	'690',
Include items dated approximately TICK BOX	'691',
John Johnson Collection Shelfmark	'950',
Limit according to physical form TICK BOXES	'600',
Limit to items TICK BOXES	'095',
	
	
	
	
	
	
	
	
	
	
	
Limit to items with price	'091',
	
	
Advertising Search	
Search Fields	Data fields searched
Keyword	Entire record
Name keyword	'300',
	'301',
	'310',
	'320',
	'330',
	'331',
	'334',
	'340',
	'350',
	'351',
	'352',
	'353',
	'354',
	'400',
	'401',
	'405',
	'408',
	'420',
	'421',
	'422',
	'423',
	'424',
	'430',
	'431',
	'432',
	'438',
	'440',
	'450',
	'500',
	'501',
	'505',
	'510',
	'530',
	'570',
	'571',
	'572',
	'573',
	'580',
	'581',
	'582',
	'730',
	'732',
	'738',
Title/First Line Keyword	'200',
	'205',
	'210',
	'220',
	'223',
	'224',
	'240',
	'242',
	'245',
	'248',
	'270',
	'278',
	'282',
	'283',
Product keyword	'437',
	'439',
	'438',
Trade keyword	'436',
Subject Keyword	'282', SUBFIELD $g
	'340', SUBFIELD $o
	'439',
	'700',
	'724',
	'730',
	'732',
	'740',
Illustration subject keyword	'708',
	'709',
	'710',
	'720',
	'738',
Place Keyword	'284',
	'291',
	'434',
	'740',
	$t (or, if present, $x overrides $t) subfield from any '3xx',, '4xx', and '5xx', field.
Document type	'100',
	'101',
Printing process	'680',
Limit to printing process of illustrations	'681',
Printer/Engraver	'530',
	'510',
Date	'285',
	'290',
	'689',
	'690',
Include items dated approximately TICK BOX	'691',
John Johnson Collection Shelfmark	'950',
Limit according to physical form TICK BOXES	'600',
Limit to items TICK BOXES	'095',
	
	
	
	
	
	
	
	
	
	
	
Limit to items with price	'091',
"""

"""
def makedictionary():
# Get a dictionary mapping tag no. to all the basic search fields that shd cover it.
# starting from one mapping search fields to tags.
# Used in setting up getsearchmappings. No longer needed?
	
	basic = {
	'name_keyword':	['300',
		'301',
		'310',
		'320',
		'330',
		'331',
		'334',
		'340',
		'350',
		'351',
		'352',
		'353',
		'354',
		'400',
		'401',
		'405',
		'408',
		'420',
		'421',
		'422',
		'423',
		'424',
		'430',
		'431',
		'432',
		'438',
		'440',
		'450',
		'500',
		'501',
		'505',
		'510',
		'530',
		'570',
		'571',
		'572',
		'573',
		'580',
		'581',
		'582',
		'730',
		'732',
		'738'],
	'title_keyword': ['200',
		'205',
		'210',
		'220',
		'223',
		'224',
		'240',
		'242',
		'245',
		'248',
		'270',
		'278',
		'282',
		'283'],
	'eventtitle_keyword':	['280',
		'282',
		'283'],
	'eventvenue_keyword':	['284'],
	'eventdate_keyword':	['285'],
	'subject_keyword':	[
		'439',
		'436',
		'437',
		'700',
		'724',
		'730',
		'732'],
	'illsubj_keyword':	['708',
		'709',
		'710',
		'720',
		'738'],
	'place_keyword':	['284',
		'291',
		'434',
		'581',
		'740'],
	'doctype_keyword':	['100',
		'101'],
	'printproc_keyword':	['680'],
	'printer_engraver_keyword':	['530',
		'510'],
	'date_keyword':	['285',
		'290',
		'689',
		'690'],
	'shelfmark_keyword':	['950'],
	'product_keyword':	['437',
		'439',
		'438'],
	'trade_keyword':	['436']
		}
	
	searches = {}
	for srch in basic.keys():
		for tag in basic[srch]:
			if not searches.has_key(tag):
				searches[tag] = [srch]
			else:
				searches[tag].append(srch)
			
	outf = open('srches.log', 'w')
	print >> outf, searches
	outf.close()

"""