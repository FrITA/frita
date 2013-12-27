#importOdt.py
#FrITA - Free Interactive Text Aligner

# Copyright (C) 2012  Gregory Vigo Torres

    # This program is free software: you can redistribute it and/or modify
    # it under the terms of the GNU General Public License as published by
    # the Free Software Foundation, either version 3 of the License, or
    # any later version.

    # This program is distributed in the hope that it will be useful,
    # but WITHOUT ANY WARRANTY; without even the implied warranty of
    # MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    # GNU General Public License for more details.

    # You should have received a copy of the GNU General Public License
    # along with this program. If not, see http://www.gnu.org/licenses/.



import zipfile
from xml.dom.pulldom import *

def get_writer_doc(fileName):

    F = zipfile.ZipFile(fileName, 'r')
    xmlCONTENT = F.open('content.xml', mode='r')
    FILE = xmlCONTENT.read()
    FILE = FILE.decode('utf-8')

    doc = xml.dom.pulldom.parseString(FILE)

    tokin = 'text'
    span = False

    all_notes = []
    this_note = []

    this_box = []
    all_boxes = []

    all_paras = []
    this_para = []

    all_comments = []
    this_comment = []

##show comments and tracked changes, there is currently no way to change these options from the GUI
    showComments = True
    showChanges = False


    for (event, node) in doc:

## filter start elements
        if event == 'START_ELEMENT':
            if node.localName == 'note-body':
                tokin = 'note'

        if node.nodeName == 'draw:text-box':    #text box
            tokin = 'box'

        if event == 'START_ELEMENT':     #note
            if node.nodeName == 'office:annotation':
                tokin = 'comment'

        if event == 'START_ELEMENT':    #changes
            if node.localName == 'tracked-changes':
                tokin = 'change'

## special case for note-citation numbers
        if event == 'START_ELEMENT':    #note-citation(number)
            if node.localName == 'note-citation':
                nxt = doc.__next__()
                cite = nxt[1].nodeValue
                this_note.append(cite+' ')
                this_para.append(cite)

        if event == 'START_ELEMENT':    #span
            if node.localName == 'span':
                span = True

        if event == 'START_ELEMENT':    #p
            if node.localName == 'p':
                p = True

## get text selectively

        if event == 'CHARACTERS':   #note
            if tokin == 'note':
                cur_text = node.nodeValue
                if len(cur_text) != 0:
                    this_note.append(cur_text)

        if event == 'CHARACTERS':   #text-box
            if tokin == 'box':
                cur_text = node.nodeValue
                this_box.append(cur_text.lstrip() )

        if event == 'CHARACTERS':   #normal text and span
            if  tokin == 'text':
                t = node.nodeValue
                if len(t) != 0 and t != '\n':
                    if span == True:
                        #if t[:].isalnum():
                            #this_para.append(t+' ')
                        #else:
                        this_para.append(t)
                    elif span == False:
                        #this_para.append(t.lstrip())
                        this_para.append(t)

        if event == 'CHARACTERS':   #comments
            if tokin == 'comment':
                cur_text = node.nodeValue
                if len(cur_text) != 0:
                    c = cur_text.strip()
                if len(c) > 0:
                    c = c+' '
                    this_comment.append(c)

## unset tokin using end elements
        if event == 'END_ELEMENT':  #note-body
            if node.localName == 'note-body':
                tokin = 'text'

        if event == 'END_ELEMENT':  #text-box
            if node.nodeName == 'draw:text-box':
                tokin = 'text'

        if event == 'END_ELEMENT': #comment
            if node.nodeName == 'office:annotation':
                tokin = 'text'

        if event == 'END_ELEMENT':  #tracked-changes
            if node.localName == 'tracked-changes':
                tokin = 'text'

        if event == 'END_ELEMENT':
            if node.localName == 'span':
                span = False

## IS a NOTE
            if tokin == 'note':
                if node.localName == 'p':
                    n = ''
                    n = n.join(this_note)
                    n = n+'\n'
                    all_notes.append(n)
                    this_note = []

## IS a TEXT-BOX
            if tokin == 'box':
                if node.localName == 'p' or node.localName == 'span':
                    b = ''
                    b = b.join(this_box)
                    all_boxes.append(b+'\n')
                    this_box = []

## IS a COMMENT
            if tokin == 'comment':
                if node.localName == 'span':
                    c = ''
                    c = c.join(this_comment)
                    c = c+' '
                    all_comments.append(c)
                    this_comment = []


## IS NORMAL TEXT
            if tokin == 'text':
                if node.localName == 'p' or node.localName == 'h':
                    p= ''
                    p = p.join(this_para)
                    p = p+'\n'
                    all_paras.append(p)
                    this_para = []


    L = all_paras + all_boxes + all_notes

    if showComments == True:
        L = L + all_comments

    F.close()

    return L
