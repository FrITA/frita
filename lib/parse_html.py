#! /usr/bin/env python3

from html.parser import HTMLParser
import re
import itertools

class html_parser(HTMLParser):
    """Returns a list of paragraphs
    options= get_meta, get_img_meta"""

    #parser options
    parser_options = {'get_meta':True, 'get_img_meta':False}
    get_meta = parser_options['get_meta']
    get_img_meta = parser_options['get_img_meta']

    meta_keys = ['name', 'property']
    meta_values = ['description', 'keywords', 'title']
    exclude_tags = ['script', 'code', 'applet', 'style', 'meta', 'img']

    line_breaking_tags =['p', 'div', 'br', 'tr', 'td', 'thead', 'tfoot',
                        'tbody', 'table', 'li', 'dd', 'dt',
                        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
                        'address', 'button', 'select', 'option',
                        'textarea', 'label', 'legend', 'form',
                        'noframes', 'noscript', 'section', 'article',
                        'aside', 'header', 'footer', 'nav', 'figcaption' ]

    special_line_breaks = ['ul', 'br']    # adds a line break at the START of the tag

    text = []
    cur_para = ''
    GET = False

    def set_options(self):
        self.get_meta = self.parser_options['get_meta']
        self.get_img_meta = self.parser_options['get_img_meta']

    def handle_starttag(self, tag, attrs):
        self.GET = False

        if tag == 'html':
            self.set_options()

        if tag not in self.exclude_tags:
            if tag in self.special_line_breaks:
                self.cur_para += '\n'
            self.GET = True

        if tag == 'title':
            self.GET = True

        if tag == 'meta' and self.get_meta == True:
            self.handle_meta(tag, attrs)

    def handle_meta(self, tag, attrs):
        content = None
        for attr in attrs:
            if attr[0].lower() in self.meta_keys and attr[1].lower() in self.meta_values:
                content = attrs[1][1]

        if content:
            self.text.append(content)

    def handle_endtag(self, tag):
        if tag in self.line_breaking_tags and self.GET == True:
            self.text.append(self.cur_para)
            self.cur_para = ''

    def handle_startendtag(self, tag, attrs):
        def get_content(attr):
            alt = None
            if len(attr[1]) > 0 and attr[1].isspace() == False:
                alt = attr[1]
            if alt:
                return alt

        if tag == 'img' and self.get_img_meta == True:
            alt = None
            title = None
            for attr in attrs:
                if attr[0].lower() == 'alt':
                    alt = get_content(attr)

                if attr[0].lower() == 'title':
                    title = get_content(attr)

            if alt:
                self.text.append(alt)
            if title:
                self.text.append(title)

        if tag == 'meta' and self.get_meta == True:
            self.handle_meta(tag, attrs)

    def handle_data(self, data):
        if self.GET == True:
            if data.isspace() == False:
                self.cur_para += data+' '

def decode_html(as_bytes):
    all_encodings = ['utf-8', 'latin_1', 'iso8859_2',
                    'iso8859_3', 'iso8859_4', 'iso8859_5',
                    'iso8859_6', 'iso8859_7', 'iso8859_8',
                    'iso8859_9', 'iso8859_10', 'iso8859_13',
                    'iso8859_14', 'iso8859_15', 'iso8859_16',
                    'ascii', 'big5', 'big5hkscs', 'cp037',
                    'cp424', 'cp437', 'cp500', 'cp720',
                    'cp737', 'cp775', 'cp850', 'cp852',
                    'cp855', 'cp856', 'cp857', 'cp858',
                    'cp860', 'cp861', 'cp862', 'cp863',
                    'cp864', 'cp865', 'cp866', 'cp869',
                    'cp874', 'cp875', 'cp932', 'cp949',
                    'cp950', 'cp1006', 'cp1026', 'cp1140',
                    'cp1250', 'cp1251', 'cp1252', 'cp1253',
                    'cp1254', 'cp1255', 'cp1256', 'cp1257',
                    'cp1258', 'euc_jp', 'euc_jis_2004', 'euc_jisx0213',
                    'euc_kr', 'gb2312', 'gbk', 'gb18030', 'hz',
                    'iso2022_jp', 'iso2022_jp_1', 'iso2022_jp_2',
                    'iso2022_jp_2004', 'iso2022_jp_3', 'iso2022_jp_ext',
                    'iso2022_kr', 'johab', 'koi8_r', 'koi8_u',
                    'mac_cyrillic', 'mac_greek', 'mac_iceland',
                    'mac_latin2', 'mac_roman', 'mac_turkish',
                    'ptcp154', 'shift_jis', 'shift_jis_2004',
                    'shift_jisx0213', 'utf_32', 'utf_32_be',
                    'utf_32_le', 'utf_16', 'utf_16_be',
                    'utf_16_le', 'utf_7', 'utf_8_sig' ]

    for enc in all_encodings:
        try:
            decoded_html = as_bytes.decode(enc, errors='strict')
            return decoded_html

        except:
            continue

def remove_extra_whitespace(line):
    """ Removes all line breaking characters.
    Collapses consecutive spaces into just one space """

    line = line.lstrip()
    line = re.sub('[\n\r\f\v\t]', ' ', line)
    line = re.sub('  +', ' ', line )

    return line


def to_text_list(filename, **kargs):
    """ get_meta default True, get_img_meta default False"""

    parser_options = {'get_img_meta':False, 'get_meta':True}
    html = None
    text = None
    p = html_parser(strict=False)

    if filename:
        file_obj = open(filename, mode='rb')
        raw_html = file_obj.read()
        html = decode_html(raw_html)
    else:
        return None

    # set parser options
    if kargs:
        for k in kargs.keys():
            if k in parser_options.keys():
                parser_options[k] = kargs[k]

        p.parser_options = parser_options

    if html:
        p.feed(html)
        clean_text = map(remove_extra_whitespace, p.text)
        ctext = list(clean_text)
        text = itertools.filterfalse(lambda l:l.isspace(), ctext)
        text = itertools.filterfalse(lambda i:len(i) < 1, text)
        text = list(text)

    p.close()

    if text:
        return text
    else:
        return None


