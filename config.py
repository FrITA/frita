## config module contains variables for app level scope

from PyQt4.QtCore import QDir
import os.path

app = None
APP_NAME = 'FrITA'
VERSION = '1.0_dev'
OTMF = 'FrITA TMX'
BASE_DIR = QDir.homePath()
CONF_DIR = os.path.join(BASE_DIR, '.frita_conf')
RULESDB = os.path.join(CONF_DIR, 'segmentation_rules.sqlite')
INSTALL_PATH = None
project_save_path = None
FILE_TYPES = '*.odt *.docx *.txt *.html *.xhtml *.htm *.php *.tmx ;; All files *'
cur_text = ''
text_changed = False
undostack = None
FONT = None

real_row_count = (0, 0)     # this is set in view_model.rowCount() or fetch_more()

SOURCE = ['Source segments']
TARGET = ['Target segments']

PROJECT_PROPERTIES = {'slang':None,
                      'tlang':None,
                      'sfilename':None,
                      'tfilename':None,
                      'segmentation':'sentence',
                      'inc_tmx_opts':False,
                      'save_path':'Nowhere'
                      }

TMX_OPTIONS ={'creationdate':None, 'creationid':None}

LCODES = ['Albanian  Albania  sq-AL' ,
'Arabic  Algeria  ar-DZ' ,
'Arabic  Bahrain  ar-BH' ,
'Arabic  Egypt  ar-EG' ,
'Arabic  Iraq  ar-IQ' ,
'Arabic  Jordan  ar-JO' ,
'Arabic  Kuwait  ar-KW' ,
'Arabic  Lebanon  ar-LB' ,
'Arabic  Libya  ar-LY' ,
'Arabic  Morocco  ar-MA' ,
'Arabic  Oman  ar-OM' ,
'Arabic  Qatar  ar-QA' ,
'Arabic  Saudi Arabia  ar-SA' ,
'Arabic  Sudan  ar-SD' ,
'Arabic  Syria  ar-SY' ,
'Arabic  Tunisia  ar-TN' ,
'Arabic  United Arab Emirates  ar-AE ' ,
'Arabic  Yemen  ar-YE' ,
'Basque  Spain eu-ES',
'Belorussian  Belorussia  be-BY' ,
'Bulgarian  Bulgaria  bg-BG' ,
'Catalan  Spain  ca-ES' ,
'Chinese  Hong Kong  zh-HK' ,
'Chinese (Simplified)  China  zh-CN' ,
'Chinese (Traditional)  Taiwan  zh-TW' ,
'Croatian  Croatia  hr-HR' ,
'Czech  Czech Republic  cs-CZ' ,
'Danish  Denmark  da-DK' ,
'Dutch  Belgium  nl-BE' ,
'Dutch  Netherlands  nl-NL' ,
'English  Australia  en-AU' ,
'English  Canada  en-CA' ,
'English  India  en-IN' ,
'English  Ireland  en-IE' ,
'English  New Zealand  en-NZ' ,
'English  South Africa  en-ZA' ,
'English  United Kingdom  en-GB' ,
'English  United States  en-US' ,
'Estonian  Estonia  et-EE' ,
'Finnish  Finland  fi-FI' ,
'French  Belgium  fr-BE' ,
'French  Canada  fr-CA' ,
'French  France  fr-FR' ,
'French  Luxembourg  fr-LU' ,
'French  Switzerland  fr-CH' ,
'Galician Spain gl-ES',
'German  Austria  de-AT' ,
'German  Germany  de-DE' ,
'German  Luxembourg  de-LU' ,
'German  Switzerland  de-CH' ,
'Greek  Greece  el-GR' ,
'Hebrew  Israel  iw-IL' ,
'Hindi  India  hi-IN' ,
'Hungarian  Hungary  hu-HU' ,
'Icelandic  Iceland  is-IS' ,
'Italian  Italy  it-IT' ,
'Italian  Switzerland  it-CH' ,
'Japanese  Japan  ja-JP' ,
'Korean  South Korea  ko-KR' ,
'Latvian  Latvia  lv-LV' ,
'Lithuanian  Lithuania  lt-LT' ,
'Macedonian  Macedonia  mk-MK' ,
'Norwegian (Bokmål)  Norway  no-NO' ,
'Polish  Poland  pl-PL' ,
'Portuguese  Brazil  pt-BR' ,
'Portuguese  Portugal  pt-PT' ,
'Romanian  Romania  ro-RO' ,
'Russian  Russia  ru-RU' ,
'Serbian (Cyrillic)  Yugoslavia  sr-YU' ,
'Serbo-Croatian  Yugoslavia  sh-YU' ,
'Slovak  Slovakia  sk-SK' ,
'Slovenian  Slovenia  sl-SI' ,
'Spanish  Argentina  es-AR' ,
'Spanish  Bolivia  es-BO' ,
'Spanish  Chile  es-CL' ,
'Spanish  Colombia  es-CO' ,
'Spanish  Costa Rica  es-CR' ,
'Spanish  Dominican Republic  es-DO' ,
'Spanish  Ecuador  es-EC' ,
'Spanish  El Salvador  es-SV' ,
'Spanish  Guatemala  es-GT' ,
'Spanish  Honduras  es-HN' ,
'Spanish  Mexico  es-MX' ,
'Spanish  Nicaragua  es-NI' ,
'Spanish  Panama  es-PA' ,
'Spanish  Paraguay  es-PY' ,
'Spanish  Peru  es-PE' ,
'Spanish  Puerto Rico  es-PR' ,
'Spanish  Spain  es-ES' ,
'Spanish  Uruguay  es-UY' ,
'Spanish  Venezuela  es-VE' ,
'Swedish  Sweden  sv-SE' ,
'Thai (Western digits)  Thailand  th-TH' ,
'Turkish  Turkey  tr-TR' ,
'Ukrainian  Ukraine  uk-UA'
]

RTL_LANGS = ['Arabic  Algeria  ar-DZ',
'Arabic  Bahrain  ar-BH',
'Arabic  Egypt  ar-EG',
'Arabic  Iraq  ar-IQ',
'Arabic  Jordan  ar-JO',
'Arabic  Kuwait  ar-KW',
'Arabic  Lebanon  ar-LB',
'Arabic  Libya  ar-LY',
'Arabic  Morocco  ar-MA',
'Arabic  Oman  ar-OM',
'Arabic  Qatar  ar-QA',
'Arabic  Saudi Arabia  ar-SA',
'Arabic  Sudan  ar-SD',
'Arabic  Syria  ar-SY',
'Arabic  Tunisia  ar-TN',
'Arabic  United Arab Emirates  ar-AE ',
'Arabic  Yemen  ar-YE',
'Hebrew  Israel  iw-IL'
]


