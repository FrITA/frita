## import text from tmx

import xml.dom
import xml.dom.minidom
import xml.etree.ElementTree as etree
from itertools import zip_longest
import config

class write_tmx():
    def __init__(self, source, target, tmxpath ):
        """version 1.0
        Expects source and target as lists of strings. The finished tmx is self.tmx.
        The optional attributes are included in the header,
        because the tmx is created at one go and there is no functionality for editing individual segments.
        Tags for inline formatting or markup visible as text are preserved as escaped text and only a level 1 tmx is created."""

        self.srclang = config.PROJECT_PROPERTIES['slang']
        self.tarlang = config.PROJECT_PROPERTIES['tlang']

        self.srclang = self.srclang[-5:].lower()
        self.tarlang = self.tarlang[-5:].lower()

        self.header_properties = {'srclang':self.srclang,
                            'creationtool':config.APP_NAME,
                            'creationtoolversion':config.VERSION,
                            'segtype':config.PROJECT_PROPERTIES['segmentation'],
                            'o-tmf':config.OTMF,
                            'adminlang':'en-us',
                            'datatype':'plaintext' }

        self.tmx = self.create_document()
        self.add_headers_and_such()
        body = self.tmx.getElementsByTagName('body')
        body = body[0]
        srctar = zip_longest(source, target, fillvalue=' ')
        self.populate_tmx(srctar, body)

        self.save_tmx(tmxpath)

    def make_tuv(self):
        tuv = self.tmx.createElement('tuv')
        lattr = self.tmx.createAttribute('xml:lang')
        tuv.setAttributeNode(lattr)

        return tuv

    def make_seg(self, text):
        seg = self.tmx.createElement('seg')
        tn = self.tmx.createTextNode(text.strip() )
        seg.appendChild(tn)

        return seg

    def populate_tmx(self, srctar, body):
        """iterates over source and target and appends tu and tuv elements to tmx"""
        srclang = self.srclang
        tarlang = self.tarlang

        for src, tar in srctar:
            tu = self.tmx.createElement('tu')
            tu = body.appendChild(tu)

            # do source
            stuv = self.make_tuv()
            stuv.setAttribute('xml:lang', srclang)
            src_tuv = tu.appendChild(stuv)
            seg = self.make_seg(src)
            src_tuv.appendChild(seg)

             # do target
            ttuv = self.make_tuv()
            ttuv.setAttribute('xml:lang', tarlang)
            tar_tuv = tu.appendChild(ttuv)
            seg = self.make_seg(tar)
            tar_tuv.appendChild(seg)


    def create_document(self):
        """uses xml.dom to create document with correct doctype"""
        dom = xml.dom.getDOMImplementation()
        tmxdoctype = dom.createDocumentType("tmx", None, "tmx14.dtd")
        tmx = dom.createDocument("http://www.lisa.org/tmx14", "tmx", tmxdoctype )

        return tmx


    def add_opt_attrs(self):
        header = self.tmx.getElementsByTagName('header')
        header = header[0]

        for a in config.TMX_OPTIONS.keys():
            value = config.TMX_OPTIONS[a]
            if value is not None:
                attr = self.tmx.createAttribute(a)
                header.setAttributeNode(attr)
                header.setAttribute(a, value)


    def add_headers_and_such(self):
        root = self.tmx.documentElement
        attr = self.tmx.createAttribute('version')
        root.setAttributeNode(attr)
        root.setAttribute('version', '1.4')

        headerelem = self.tmx.createElement('header')
        for k in self.header_properties.keys():
            attr = self.tmx.createAttribute(k)
            headerelem.setAttributeNode(attr)
            headerelem.setAttribute(k, self.header_properties[k])

        root.appendChild(headerelem)

        #add note to header
        note = self.tmx.createElement('note')
        note_text = self.tmx.createTextNode('TMX Level 1')
        note.appendChild(note_text)
        headerelem.appendChild(note)

        # include optional attributes
        if config.PROJECT_PROPERTIES['inc_tmx_opts'] == True:
            self.add_opt_attrs()

        bodyelem = self.tmx.createElement('body')
        self.tmx.documentElement.appendChild(bodyelem)

    def save_tmx(self, tmxpath):
        tmxstr = self.tmx.toprettyxml()
        # write to file!
        try:
            with open(tmxpath, mode='w') as tm:
                self.tmx.writexml(tm, indent='', addindent='   ', newl='\n', encoding='UTF-8')
                tm.close()
        except:
            return None


class read_tmx():
    def __init__(self, tmxfile):
        self.source = []
        self.target = []

        with xml.dom.minidom.parse(tmxfile) as tmxdoc:
            ##self.get_tmx_version(tmxdoc)  #put this back later to show the tmx version in properties
            #make sure it's really a tmx
            if tmxdoc.documentElement.tagName == 'tmx':
                all_tuvs = tmxdoc.getElementsByTagName('tuv')
                self.lang_attr = 'xml:lang'

                for i in all_tuvs[:4]:
                    if i.hasAttribute('lang'):
                        self.lang_attr = 'lang'
                    if i.hasAttribute('xml:lang'):
                        self.lang_attr = 'xml:lang'

                langs = self.get_tmx_langs(tmxdoc, all_tuvs)
                srclang = langs[0]
                tarlangs = list(langs[1])
# assumes only two languages in the tmx!
# add a language selection option if there are more than two languages!
# raise an error here if the srclang is not in tarlangs
                del tarlangs[tarlangs.index(srclang)]

                if len(tarlangs) > 1:
                    print('Choose a target language', tarlangs)
                else:
                    tarlang = tarlangs[0]

                self.get_segments(all_tuvs, srclang, tarlang)

            else:
# raise nasty error and exit
                print('It seems like the file you\'re trying to open isn\'t a tmx file.')

    def get_seg_text(self, tuv):
        this_seg = ''
        seg = tuv.getElementsByTagName('seg')
        children = seg[0].childNodes
        for c in children:
            # 3 is text node
            # 1 is element
            if c.nodeType == 3:
                nv = c.nodeValue
                if nv:
                    this_seg += nv
            if c.nodeType == 1:
                cc = c.childNodes
                for child in cc:
                    if child.nodeType == 3:
                        nv = child.nodeValue
                        if nv:
                            this_seg += nv

        return this_seg


    def get_segments(self, all_tuvs, srclang, tarlang):
        source = []
        target = []

        for i in all_tuvs:
            tuvlang = i.getAttribute(self.lang_attr).lower()
            if tuvlang == srclang:
                this_seg = self.get_seg_text(i)
                source.append(this_seg)

            if tuvlang == tarlang:
                this_seg = self.get_seg_text(i)
                target.append(this_seg)

        self.source = source
        self.target = target


    def get_tmx_langs(self, tmxdoc, all_tuvs):
        tmx_langs = set()
        header = tmxdoc.getElementsByTagName('header')
        srclang = header[0].getAttribute('srclang').lower()

        for i in all_tuvs:
            lattr = i.getAttributeNode(self.lang_attr)
            lang = lattr.value.lower()
            tmx_langs.add(lang)

        return srclang, tmx_langs


##    def get_tmx_version(self, tmxdoc):
## put this back at some point later to show version of imported tmx in project properties
##        tmx_version = tmxdoc.doctype.systemId
##
##        if tmx_version == 'tmx14.dtd':
##            self.tmxversion = '1.4'
##        if tmx_version == 'tmx11.dtd':
##            self.tmxversion = '1.1'

