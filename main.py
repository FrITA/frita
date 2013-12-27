#!/usr/bin/env python3

#FrITA - Free Interactive Text Aligner

            # Copyright (C) 2013 Gregory Vigo Torres

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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import types
import os
import os.path
import re
import shelve
import pickle
import zipfile
from datetime import datetime
import time
import itertools

from lib import importOdt
from lib import parse_html
from lib import docx
from lib import tmxlib
from lib import segment

import main_view
from commands import *
import config

## global variables are in config

class tmx_dialog(QDialog):
    def __init__(self):
        super(tmx_dialog, self).__init__()

        self.utcdate = None

        frame_style = QFrame.Plain | QFrame.Panel
        title = config.app.translate('tmx_dialog', 'TMX Properties', 'window title')
        self.setWindowTitle(title)

        # source lang chooser
        slang_label = QLabel(config.app.translate('tmx_dialog', 'Source language', 'tmx options'))
        self.slang_chooser = QComboBox()
        self.slang_chooser.addItems(config.LCODES)

        if config.PROJECT_PROPERTIES['slang'] is not None:
            self.slang_ind = config.LCODES.index(config.PROJECT_PROPERTIES['slang'])
            self.slang_chooser.setCurrentIndex(self.slang_ind)
        sl_layout = QHBoxLayout()
        sl_layout.addWidget(slang_label)
        sl_layout.addWidget(self.slang_chooser)

         # target lang chooser
        tlang_label = QLabel(config.app.translate('tmx_dialog', 'Target language', 'tmx options'))
        self.tlang_chooser = QComboBox()
        self.tlang_chooser.addItems(config.LCODES)

        # get index of current slang
        if config.PROJECT_PROPERTIES['tlang'] is not None:
            self.tlang_ind = config.LCODES.index(config.PROJECT_PROPERTIES['tlang'])
            self.tlang_chooser.setCurrentIndex(self.tlang_ind)
        tl_layout = QHBoxLayout()
        tl_layout.addWidget(tlang_label)
        tl_layout.addWidget(self.tlang_chooser)

        # standard buttons
        butt_box = QDialogButtonBox()
        self.ok = butt_box.addButton(QDialogButtonBox.Ok )
        self.reset = butt_box.addButton(QDialogButtonBox.Reset )
        self.cancel = butt_box.addButton(QDialogButtonBox.Cancel )

        # more button
        self.more_butt = QPushButton(config.app.translate('tmx_dialog', 'More options', 'tmx options'))
        self.more_butt.setCheckable(True)
        self.more_butt.setAutoDefault(False)

    # more options
        self.more_options = QWidget()
        self.more_butt.toggled.connect(self.toggle_options_butt)
        # creation date
        self.yes_crdate = QCheckBox(config.app.translate('tmx_dialog', 'Include creation date? dd/mm/yyyy hh:mm:ss', 'tmx options'))

        self.nice_date = self.get_dates()
        crid_date_edit = QLineEdit()
        crid_date_edit.setText(self.nice_date)
        crid_date_edit.setReadOnly(True)

        # creation id
        self.yes_crid = QCheckBox(config.app.translate('tmx_dialog', 'Include creation id?', 'tmx options'))
        self.id_linedit = QLineEdit()

        #moptions layout
        moptions_layout = QGridLayout()
        moptions_layout.addWidget(self.yes_crdate, 0, 0)
        moptions_layout.addWidget(crid_date_edit, 0, 1)
        moptions_layout.addWidget(self.yes_crid, 1, 0)
        moptions_layout.addWidget(self.id_linedit, 1, 1)
        self.more_options.setLayout(moptions_layout)

    # main layout
        layout = QGridLayout()
        layout.addLayout(sl_layout, 0, 0)
        layout.addLayout(tl_layout, 1, 0)
        layout.addWidget(self.more_butt, 2, 0, Qt.AlignLeft)
        layout.addWidget(butt_box, 3, 0, Qt.AlignRight)
        layout.addWidget(self.more_options)
        layout.setColumnMinimumWidth(0, 650)

        self.cancel.clicked.connect(self.reject)
        self.reset.clicked.connect(self.reset_fields)
        self.ok.clicked.connect(self.generate_tmx)

        self.setLayout(layout)
        self.more_options.hide()

        self.setAttribute(Qt.WA_DeleteOnClose)

    def error_message(self, err):
        err_msg = QMessageBox()
        err_msg.setText(err)
        title = config.app.translate('tmx_dialog', 'TMX error', 'Title of error message box')
        err_msg.setWindowTitle(title)
        err_msg.exec_()

    def toggle_options_butt(self):
        if self.more_options.isVisible() == False:
            self.more_options.setVisible(True)
        else:
            self.more_options.hide()

        if self.more_butt.text() == 'More options':
            self.more_butt.setText(config.app.translate('tmx_dialog', 'Fewer options', 'tmx options'))
        else:
            self.more_butt.setText(config.app.translate('tmx_dialog', 'More options', 'tmx options'))

    def get_dates(self):
        UTCnow = datetime.utcnow()
        UTCdate = UTCnow.utctimetuple()
        crdate = time.strftime('%Y%m%dT%H%M%SZ', UTCdate )
        nice_crdate = time.strftime('%d/%m/%Y %H:%M:%S')
        self.utcdate = crdate

        return nice_crdate

    def reset_fields(self):
        self.id_linedit.setText('')
        self.yes_crid.setCheckState(Qt.Unchecked)
        self.yes_crdate.setCheckState(Qt.Unchecked)
        self.tlang_chooser.setCurrentIndex(self.tlang_ind)
        self.slang_chooser.setCurrentIndex(self.slang_ind)

    def generate_tmx(self):
        if self.yes_crdate.isChecked() == True:
            config.TMX_OPTIONS['creationdate'] = self.utcdate
            config.PROJECT_PROPERTIES['inc_tmx_opts'] = True

        crid = self.id_linedit.displayText()

        if self.yes_crid.isChecked() == True:
            if len(crid) > 0 and crid.isspace() == False:
                config.TMX_OPTIONS['creationid'] = crid
                config.PROJECT_PROPERTIES['inc_tmx_opts'] = True
            else:
                err = config.app.translate('tmx_dialog', 'No creation ID was entered.', 'No creation ID entered')
                self.error_message(err)
                return None

        if self.yes_crid.isChecked() == False and len(self.id_linedit.displayText()) > 0:
            err = config.app.translate('tmx_dialog', 'Do you want to include a creation ID in your TMX?',\
                                        'Creation ID entered but box not checked')
            cont = config.app.translate('tmx_dialog', 'Yes', 'Include creation ID button text')
            title = config.app.translate('tmx_dialog', 'Include ID', 'Include ID creation warning box title')
            cancel = config.app.translate('tmx_dialog', 'No', 'Do not include creation ID, button text')
            inc_id = QMessageBox.warning(self, title, err, cont, button1Text=cancel)
            if inc_id == 0:
                config.TMX_OPTIONS['creationid'] = crid
                config.PROJECT_PROPERTIES['inc_tmx_opts'] = True

# source and target validation
        s = 0
        slen = [s+1 for i in config.SOURCE if len(i)>0 and i.isspace() == False ]
        slen = sum(slen)

        t = 0
        tlen = [s+1 for i in config.TARGET if len(i)>0 and i.isspace() == False ]
        tlen = sum(tlen)

        carryon = 0
        if slen == tlen:
            carryon = 0
        else:
            # source and target are NOT the same length
            err = config.app.translate('tmx_dialog',\
                                    'Source and target are not the same length.\nThere will be empty segments in your TMX',\
                                    'TMX validation error')
            cont = config.app.translate('tmx_dialog', 'Continue', 'Unequal number of segments but continue anyway')
            cancel = config.app.translate('tmx_dialog', 'Cancel', 'Unequal number of segments, do not continue')
            title = config.app.translate('tmx_dialog', 'TMX error', 'Unequal number of segments, title')
            warn = QMessageBox()
            carryon = warn.warning(self, title, err, cont, button1Text=cancel)   # returns 1 0r 0

        if carryon == 0:
            fd_caption = config.app.translate('tmx_dialog', 'Save TMX', 'tmx options file dialog caption')
            tmxpath = QFileDialog().getSaveFileName(caption=fd_caption, directory=config.BASE_DIR,\
                                                     filter='*.tmx', options=QFileDialog.DontConfirmOverwrite )
            if tmxpath[-4:] != '.tmx':
                tmxpath = tmxpath+'.tmx'

            # make sure file doesn't already exist
            exists = os.path.exists(tmxpath)
            overwrite = 1

            if exists == False:
                tmxlib.write_tmx(config.SOURCE, config.TARGET, tmxpath)
                overwrite = 0
            if exists == True:
                title = config.app.translate('tmx_dialog', 'Overwrite?', 'Overwrite warning dialog title')
                err = config.app.translate('tmx_dialog', 'Overwrite existing TMX? {0}'.format(tmxpath), 'Overwrite warning dialog message')
                cont = config.app.translate('tmx_dialog', 'Continue', 'Overwrite existing file')
                cancel = config.app.translate('tmx_dialog', 'Cancel', 'Do not overwrite existing file')
                overwrite = QMessageBox.warning(self, title, err, cont, button1Text=cancel)
                if overwrite == 0:
                    tmxlib.write_tmx(config.SOURCE, config.TARGET, tmxpath)

            self.close()

            msg = ''
            saved = QMessageBox()

            def show_msg():
                saved.close()

            if os.path.exists(tmxpath) and overwrite == 0:
                msg = config.app.translate('tmx_dialog', 'Saved {0}'.format(tmxpath), 'Saved successfully message')
                saved.setText(msg)
                saved.open()
                QTimer.singleShot(2000, show_msg )
            elif os.path.exists(tmxpath) == False and overwrite == 1:
                msg = config.app.translate('tmx_dialog', "{0} Wasn't saved !".format(tmxpath), 'could not save tmx')
                saved.setText(msg)
                saved.open()
                QTimer.singleShot(2500, show_msg)

        else:
            self.close()


class new_dialog(QDialog):
    def __init__(self):
        super(new_dialog, self).__init__()

        frame_style = QFrame.Plain | QFrame.Panel

        self.slabel = QLabel()
        self.slabel.setText(config.app.translate('new_dialog', 'Source', 'label') )
        self.tlabel = QLabel()
        self.tlabel.setText(config.app.translate('new_dialog', 'Target', 'label') )

        self.slang_label = QLabel()
        self.slang_label.setFrameStyle(frame_style)
        self.slang_button = QPushButton(config.app.translate('new_dialog', 'Choose source language', 'button') )
        self.tlang_label = QLabel()
        self.tlang_label.setFrameStyle(frame_style)
        self.tlang_button = QPushButton(config.app.translate('new_dialog', 'Choose target language', 'button') )

        self.source_filename_label = QLabel()
        self.source_filename_label.setFrameStyle(frame_style)
        self.source_filename_button = QPushButton(config.app.translate('new_dialog', 'Choose source file', 'button') )
        self.target_filename_label = QLabel()
        self.target_filename_label.setFrameStyle(frame_style)
        self.target_filename_button = QPushButton(config.app.translate('new_dialog', 'Choose target file', 'button') )

        self.butt_box = QDialogButtonBox()
        self.ok = self.butt_box.addButton(QDialogButtonBox.Ok)
        self.reset = self.butt_box.addButton(QDialogButtonBox.Reset)
        self.cancel = self.butt_box.addButton(QDialogButtonBox.Cancel)

        # seg checkbox
        self.seg_checkbox = QCheckBox()
        self.seg_checkbox.setText(config.app.translate('new_dialog', 'Segment by paragraph', 'checkbox') )
        self.seg_checkbox.setCheckState(Qt.Unchecked)

        #connect
        self.slang_button.clicked.connect(self.get_slang)
        self.tlang_button.clicked.connect(self.get_tlang)
        self.source_filename_button.clicked.connect(self.get_source_filename)
        self.target_filename_button.clicked.connect(self.get_target_filename)
        self.ok.clicked.connect(self.close_ok)
        self.cancel.clicked.connect(self.reject)
        self.reset.clicked.connect(self.clear_fields)

        #layout
        grid = QGridLayout()
        grid.setColumnMinimumWidth(1, 275)

        grid.addWidget(self.slabel, 0, 0)
        grid.addWidget(self.slang_button, 1, 0)
        grid.addWidget(self.slang_label, 1, 1)
        grid.addWidget(self.source_filename_button, 2, 0)
        grid.addWidget(self.source_filename_label, 2, 1)

        grid.addWidget(self.tlabel, 3, 0)
        grid.addWidget(self.tlang_button, 4, 0)
        grid.addWidget(self.tlang_label, 4, 1)
        grid.addWidget(self.target_filename_button, 5, 0)
        grid.addWidget(self.target_filename_label, 5, 1)
        grid.addWidget(self.seg_checkbox, 6, 0)

        grid.addWidget(self.butt_box, 7, 1)

        self.setLayout(grid)

#
        self.setWindowTitle(config.app.translate('new_dialog', 'Project properties', 'window title') )
        self.exec()

#actions
    def clear_fields(self):
        self.source_filename_label.setText('')
        self.target_filename_label.setText('')
        self.slang_label.setText('')
        self.tlang_label.setText('')

    def get_slang(self):
        item, ok = QInputDialog.getItem(self, "QInputDialog.getItem()", \
                                        config.app.translate('new_dialog', "Source lang:", 'file dialog label'), \
                                        config.LCODES, 0, False)

        # SET THE TITLE FOR THE INPUT DIALOG!!!

        if ok and item:
            self.slang_label.setText(item)

    def get_tlang(self):
        item, ok = QInputDialog.getItem(self, "QInputDialog.getItem()", \
                                        config.app.translate('new_dialog', "Target lang:", 'file dialog label'), \
                                        config.LCODES, 0, False)
        if ok and item:
            self.tlang_label.setText(item)

    def get_source_filename(self):
        filename = QFileDialog.getOpenFileName(self, caption=config.app.translate('new_dialog', 'Select a file', 'file dialog caption'), \
                                               directory=config.BASE_DIR, filter=config.FILE_TYPES)
        if filename:
            self.source_filename_label.setText(filename)
            config.BASE_DIR = os.path.split(filename)[0]

    def get_target_filename(self):
        filename = QFileDialog.getOpenFileName(self, caption=config.app.translate('new_dialog', 'Select a file', 'file dialog caption'), \
                                                                                  directory=config.BASE_DIR, filter=config.FILE_TYPES)
        if filename:
            self.target_filename_label.setText(filename)
            config.BASE_DIR = os.path.split(filename)[0]

    def error_message(self, err):
        err_msg = QMessageBox()
        err_msg.setText(err)
        err_msg.exec_()

    def close_ok(self):
        sfn = self.source_filename_label.text()
        tfn = self.target_filename_label.text()
        sl = self.slang_label.text()
        tl = self.tlang_label.text()

        config.PROJECT_PROPERTIES['slang'] = sl
        config.PROJECT_PROPERTIES['tlang'] = tl
        config.PROJECT_PROPERTIES['sfilename'] = sfn
        config.PROJECT_PROPERTIES['tfilename'] = tfn

        para = self.seg_checkbox.checkState()  #0 is unchecked

        if para == 0:
            config.PROJECT_PROPERTIES['segmentation'] = 'sentence'
        elif para == 2:
            config.PROJECT_PROPERTIES['segmentation']  = 'paragraph'

# catch empty options!
        keys = {'slang':'Source language', 'tlang':'Target language', 'sfilename':'Source file', 'tfilename':'Target file'}
        has_error = False
        for i in config.PROJECT_PROPERTIES.keys():
            if isinstance(config.PROJECT_PROPERTIES[i], str) and len(config.PROJECT_PROPERTIES[i]) < 1:
                error1 = config.app.translate('new_dialog', 'You must choose a {property}'.format(property=keys[i]), 'file dialog error')
                self.error_message(error1)
                has_error = True

        if has_error == False:
            self.accept()
##s
class project_properties_info(QDialog):
    def __init__(self):
        super(project_properties_info, self).__init__()

        if config.PROJECT_PROPERTIES['slang'] is not None:
            frame_style = QFrame.Plain | QFrame.Panel
            self.setWindowTitle(config.app.translate('project_properties_info', 'Project properties') )
            self.layout = QGridLayout()
            self.setLayout(self.layout)

            if config.project_save_path is None:
                project_save_path = config.app.translate('project_properties_info', 'Nowhere', 'refers to file path')
                config.PROJECT_PROPERTIES['save_path'] = project_save_path
            else:
                project_save_path = config.project_save_path
                config.PROJECT_PROPERTIES['save_path'] = project_save_path

            properties = config.app.translate('project_properties_info',
            """<html><head><meta name="properties" content="1" />
            <meta http-equiv="Content-Type" content="text/html; charset=UTF-8" />
            <title>Project properties</title></head>
            <body><p>
            <span style="font-weight:800; color:#008CC1;">Source language:&nbsp;</span>
            {slang}</p><p>
            <span style="font-weight:800; color:#008CC1;">Target language:&nbsp;</span>
            {tlang}</p><p>
            <span style="font-weight:800; color:#008CC1;">Source file:&nbsp;</span>
            {sfilename}</p><p>
            <span style="font-weight:800; color:#008CC1;">Target file:&nbsp;</span>
            {tfilename}</p><p>
            <span style="font-weight:800; color:#008CC1;">Segmentation:&nbsp;</span>
            {segmentation}</p><p>
            <span style="font-weight:800; color:#008CC1;">Project saved to:&nbsp;</span>
            {save_path}
            </p></body></html>""".format(**config.PROJECT_PROPERTIES), 'project properties')


            main_wid = QTextEdit()
            main_wid.setReadOnly(True)
            doc = QTextDocument()
            doc.setHtml(properties)
            main_wid.setDocument(doc)

            main_wid.setFixedWidth(550)

            close_butt = QPushButton(config.app.translate('project_properties_info', 'Close') )
            self.layout.addWidget(close_butt, 1, 0, alignment=Qt.AlignRight)
            self.layout.addWidget(main_wid, 0, 0)
            close_butt.clicked.connect(self.reject )

            self.exec()



class main_window(QMainWindow):

    def __init__(self, parent=None):
        super(main_window, self).__init__()

## cli things to get rid of later...
        pyqt_ver = PYQT_VERSION_STR
        qt_ver = QT_VERSION_STR
        print('pyqt version:', pyqt_ver)
        print('qt version:', qt_ver)
        print('Python version:', sys.version)
##
        #set window geometry
        self.setWindowTitle(config.APP_NAME)
        screen = QDesktopWidget().screenGeometry()
        width = screen.width()
        height = screen.height()
        self.resize(width, height)

        # self.view
        self.view = main_view.view(self)
        self.view.setSortingEnabled(False)

        #undostack
        self.undostack = QUndoStack(self)
        self.undostack.setUndoLimit(100)
        config.undostack = self.undostack

        #toolbar
        self.toolbar = QToolBar()
        #icons
        self.create_icons()
        # status bar
        self.statusbar = QStatusBar()
        self.statusbar.setSizeGripEnabled(False)
        self.seg_status_label = QLabel()
        self.statusbar.addPermanentWidget(self.seg_status_label, 0)
        self.setStatusBar(self.statusbar)

        # menus and actions
        self.define_actions()
        self.create_menus()
        config.undostack.undoTextChanged.connect(self.watch_undostack)
        config.undostack.redoTextChanged.connect(self.watch_redostack)
        config.undostack.redoTextChanged.connect(self.update_statusbar)

        # toolbar and icons, again
        IF = QImageReader.supportedImageFormats()       # why is this here?
        self.populate_toolbar()
        self.addToolBar(self.toolbar)

# central widget!
        self.setCentralWidget(self.view)

    def update_statusbar(self):
        scnt = 0
        slen = sum([ scnt +1 for i in config.SOURCE if len(i) > 0 ])
        tcnt = 0
        tlen = sum([ tcnt +1 for i in config.TARGET if len(i) > 0 ])

        seg_msg = config.app.translate('main_window', 
                    'source segments: {0} - target segments: {1}'.format(str(slen), str(tlen)) )
        
        self.seg_status_label.setText(seg_msg)

    def watch_undostack(self, cmd):
        cmd = config.app.translate('main_window', 'Undo {0}'.format(cmd) , 'tooltip')
        self.undo_act.setToolTip(cmd)
        self.update_statusbar()

    def watch_redostack(self, cmd):
        cmd = config.app.translate('main_window', 'Redo {0}'.format(cmd), 'tooltip')
        self.redo_act.setToolTip(cmd)
        self.update_statusbar()

    def error_message(self, err, title):
        err_msg = QMessageBox()
        err_msg.setText(err)
        err_msg.setWindowTitle(title)
        err_msg.exec_()

    def create_menus(self):
        # file menu
        self.file_menu = self.menuBar().addMenu(config.app.translate('main_window', '&File', 'menu name') )
        self.file_menu.addAction(self.new_act)
        self.file_menu.addAction(self.save_project_act)
        self.file_menu.addAction(self.save_project_as_act)
        self.file_menu.addAction(self.open_project_act)
        self.file_menu.addAction(self.proj_prop_act)
        self.file_menu.addSeparator()
        self.file_menu.addAction(self.close_project_act)
        self.file_menu.addAction(self.quit_act)
        #edit menu
        self.edit_menu = self.menuBar().addMenu(config.app.translate('main_window', '&Edit', 'menu name') )
        self.edit_menu.addAction(self.merge_down_act)
        self.edit_menu.addAction(self.merge_up_act)
        self.edit_menu.addAction(self.merge_selected_act)
        self.edit_menu.addAction(self.split_act)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.del_row_act)
        self.edit_menu.addAction(self.add_row_act)
        self.edit_menu.addAction(self.del_cell_act)
        self.edit_menu.addAction(self.add_cell_act)
        self.edit_menu.addAction(self.next_mismatch_act)
        self.edit_menu.addAction(self.goto_seg_act)
        self.edit_menu.addSeparator()
        self.edit_menu.addAction(self.undo_act)
        self.edit_menu.addAction(self.redo_act)
        # tmx
        self.tmx_menu = self.menuBar().addMenu(config.app.translate('main_window', 'TMX', 'menu name') )
#        self.tmx_menu.addAction(self.change_tmx_prop_act)
        self.tmx_menu.addAction(self.create_tmx_act)
        #About
        self.about_menu = self.menuBar().addMenu(config.app.translate('main_window', 'About', 'menu name') )
        self.about_menu.addAction(self.show_about_frita_act)


    def define_actions(self):
## file/project actions
        self.new_act = QAction(config.app.translate('main_window', '&New project', 'actions'), \
                               self, statusTip=config.app.translate('main_window', 'Create new alignment project', 'actions'), \
                               triggered=self.call_new_dialog)
        self.new_act.setShortcut(QKeySequence.New)      #ctrl+n
        self.quit_act = QAction(config.app.translate('main_window', 'Quit', 'actions'), \
                                self, statusTip=config.app.translate('main_window', 'Quit FrITA', 'actions'), \
                                triggered=self.quit)
        self.quit_act.setIcon(self.close_icon)
        self.save_project_act = QAction(config.app.translate('main_window', '&Save', 'actions'), \
                                        self, statusTip=config.app.translate('main_window', 'Save project', 'actions'), \
                                        triggered=self.project_save)
        self.save_project_as_act = QAction(config.app.translate('main_window', 'Save as', 'actions'), \
                                           self, statusTip=config.app.translate('main_window', 'Save project to a different file', 'actions'),\
                                           triggered=self.save_as)
        self.save_project_act.setShortcut(QKeySequence.Save)        #ctrl+s
        self.save_project_as_act.setShortcut(QKeySequence.SaveAs)   #ctrl+shift+s
        #
        self.open_project_act = QAction(config.app.translate('main_window', '&Open FrITA project', 'actions'), \
                                        self, statusTip=config.app.translate('main_window', 'Open project', 'actions'), \
                                        triggered=self.project_open)
        self.open_project_act.setShortcut(QKeySequence.Open)      #ctrl+o
        self.open_project_act.setIcon(self.new_icon)

        self.show_about_frita_act = QAction(config.app.translate('main_window', 'About {0}'.format(config.APP_NAME), 'actions'), \
                                            self,\
                                            statusTip=config.app.translate('main_window', 'About {0}'.format(config.APP_NAME), 'actions') \
                                            , triggered=self.about_frita)


    # setIcons...
        self.close_project_act = QAction(config.app.translate('main_window', '&Close', 'actions'), \
                                         self, statusTip=config.app.translate('main_window', 'Close project', 'actions'), \
                                         triggered=self.close_project)
        self.close_project_act.setShortcut(QKeySequence.Close)  # ctrl+w

        self.proj_prop_act = QAction(config.app.translate('main_window', 'Project properties', 'actions'), \
                                     self, triggered=project_properties_info)

## segment manipulation actions
        self.add_row_act = QAction(config.app.translate('main_window', 'Insert row', 'actions'), \
                                   self, triggered=self.view.add_row)
        self.add_row_act.setIcon(self.add_icon)
        self.add_row_act.setShortcut('Alt+Shift+a')
        self.del_row_act = QAction(config.app.translate('main_window', 'Delete row', 'actions'), \
                                   self, triggered=self.view.del_row)
        self.del_row_act.setIcon(self.delete_row_icon)
        self.del_row_act.setShortcut('Alt+Shift+d')
        self.del_cell_act = QAction(config.app.translate('main_window', 'Delete segment', 'actions'), \
                                    self, triggered=self.view.remove_cell)
        self.del_cell_act.setIcon(self.delete_cell_icon)
        self.del_cell_act.setShortcut('Alt+d')
        self.add_cell_act = QAction(config.app.translate('main_window', 'Insert segment', 'actions'),\
                                     self, triggered=self.view.add_cell)
        self.add_cell_act.setIcon(self.add_cell_icon)
        self.add_cell_act.setShortcut('Alt+a')

        self.merge_down_act = QAction(config.app.translate('main_window', 'Merge with next', 'actions'),\
                                       self, triggered=self.view.merge_down)
        self.merge_down_act.setIcon(self.down_icon)
        self.merge_down_act.setShortcut('Alt+m')

        self.merge_up_act = QAction(config.app.translate('main_window', 'Merge with previous', 'actions'),\
                                       self, triggered=self.view.merge_up)
        self.merge_up_act.setIcon(self.up_icon)
#        self.merge_up_act.setShortcut('Ctrl+m')

        self.merge_selected_act = QAction(config.app.translate('main_window', 'Merge selected', 'actions'),\
                                           self, triggered=self.view.merge_selected)
        self.merge_selected_act.setIcon(self.merge_sel_icon)
        self.merge_selected_act.setShortcut('Alt+Shift+m')
        self.split_act = QAction(config.app.translate('main_window', 'Split segment', 'actions' ), \
                                 self, triggered=self.view.split_segment)
        self.split_act.setIcon(self.split_icon)
        self.split_act.setShortcut('Alt+s')

        self.next_mismatch_act = QAction(config.app.translate('main_window', 'Go to next mismatch', 'actions'),\
                                          self, triggered=self.view.next_mismatch)
        self.next_mismatch_act.setShortcut('Ctrl+u')
        self.next_mismatch_act.setIcon(self.next_icon)

        self.goto_seg_act = QAction(config.app.translate('main_window', 'Go to row', 'action, go to row by number'), \
                                    self, triggered=self.view.goto_seg)
        self.goto_seg_act.setShortcut('Ctrl+j')

        self.undo_act = QAction(config.app.translate('main_window', 'Undo', 'actions'), self, triggered=self.undostack.undo)
        self.redo_act = QAction(config.app.translate('main_window', 'Redo', 'actions'), self, triggered=self.undostack.redo)
        self.undo_act.setIcon(self.undo_icon)
        self.redo_act.setIcon(self.redo_icon)
        self.redo_act.setShortcut(QKeySequence.Redo)
        self.undo_act.setShortcut(QKeySequence.Undo)

## tmx actions
#        self.change_tmx_prop_act = QAction(config.app.translate('main_window', 'Edit tmx properties', 'actions'), \
#                                           self, triggered=self.change_tmx_properties)
        self.create_tmx_act = QAction(config.app.translate('main_window', 'Create tmx', 'actions'), self, triggered=self.create_tmx)

    def populate_toolbar(self):
        self.toolbar.addAction(self.quit_act)
        self.toolbar.insertSeparator (self.open_project_act)
        self.toolbar.addAction(self.open_project_act)
        self.toolbar.insertSeparator(self.add_row_act)
        self.toolbar.addAction(self.add_row_act)
        self.toolbar.addAction(self.del_row_act)

        self.toolbar.addAction(self.add_cell_act)
        self.toolbar.addAction(self.del_cell_act)

        self.toolbar.insertSeparator(self.merge_down_act)
        self.toolbar.addAction(self.merge_down_act)
        self.toolbar.addAction(self.merge_up_act)
        self.toolbar.addAction(self.merge_selected_act)
        self.toolbar.insertSeparator(self.split_act)
        self.toolbar.addAction(self.split_act)
        self.toolbar.insertSeparator(self.undo_act)
        self.toolbar.addAction(self.undo_act)
        self.toolbar.addAction(self.redo_act)
        self.toolbar.insertSeparator(self.next_mismatch_act)
        self.toolbar.addAction(self.next_mismatch_act)


    def create_icons(self):
        icon_dir = os.path.join(config.INSTALL_PATH, 'icons')

        ni = os.path.join(icon_dir, 'document-new.svg' )
        self.new_icon = QIcon(ni)

        close = os.path.join(icon_dir, 'application-exit.svg')
        self.close_icon = QIcon(close)

        add = os.path.join(icon_dir, 'add-row.svg')
        self.add_icon = QIcon(add)

        delete_row = os.path.join(icon_dir, 'remove-row.svg')
        self.delete_row_icon = QIcon(delete_row)

        delete_cell = os.path.join(icon_dir, 'remove-cell.svg')
        self.delete_cell_icon = QIcon(delete_cell)

        add_cell = os.path.join(icon_dir, 'add-cell.svg')
        self.add_cell_icon = QIcon(add_cell)

        down = os.path.join(icon_dir, 'down.svg')
        self.down_icon = QIcon(down)

        up = os.path.join(icon_dir, 'up.svg')
        self.up_icon = QIcon(up)

        merge_sel = os.path.join(icon_dir, 'merge_selected.svg')
        self.merge_sel_icon = QIcon(merge_sel)

        split = os.path.join(icon_dir, 'split-segment.svg')
        self.split_icon = QIcon(split)

        next = os.path.join(icon_dir, 'next.svg')
        self.next_icon = QIcon(next)

        undo = os.path.join(icon_dir, 'edit-undo.svg')
        self.undo_icon = QIcon(undo)

        redo = os.path.join(icon_dir, 'edit-redo.svg')
        self.redo_icon = QIcon(redo)



## actions
    def close_project(self):
        config.SOURCE = []
        config.TARGET = []
        self.view.MODEL.reset()
        self.update_statusbar()
        config.project_save_path = None
        config.PROJECT_PROPERTIES = {'slang':None, 'tlang':None, 'sfilename':None, 'tfilename':None, 'segmentation':'sentence'}


    def call_new_dialog(self):
        """ ... and project file properties are parsed for opening files. """
        nd = new_dialog()
        values = list(config.PROJECT_PROPERTIES.values() )
        if None not in values:
            self.file_filter()
        else:
            return None

    def save_as(self):
        """Only exists to call get_save_path"""
        save_path = self.get_save_path()
        if save_path is not None:
            self.really_save(save_path[0], save_path[1])
        else:
            return None

    def get_save_path(self):
        """returns path to save project to and checks whether file already exists"""
        # get save file name
        file_name = QFileDialog.getSaveFileNameAndFilter(self, \
                                                         caption=config.app.translate('main_window', 'Save project', 'get save path')\
                                                        , directory=config.BASE_DIR, filter='*.frita')

        file_name = file_name[0]

        if len(file_name) == 0:
            return None

        if file_name.endswith('.frita') == False:
            save_path = file_name+'.frita'
        else:
            save_path = file_name

        config.project_save_path = save_path
        show_dialog = True
        # confirm overwrite
        if os.path.exists(save_path):
            msg = config.app.translate('main_window', 'Overwrite {0}?'.format(save_path), 'really save')
            # there might be a more cross platform way to do this
            msgbox = QMessageBox(2, config.app.translate('main_window', 'Overwrite file', 'get save path'), msg)
            ok = msgbox.addButton(config.app.translate('main_window', 'Overwrite', 'get save path'), QMessageBox.AcceptRole)
            ok = msgbox.addButton(config.app.translate('main_window', 'Cancel', 'get save path'), QMessageBox.RejectRole)
            if msgbox.exec_() == QMessageBox.AcceptRole:
                return save_path, show_dialog
            else:
                config.project_save_path = None
                return None
        else:
            return save_path, show_dialog


    def project_save(self):
        """saves SOURCE TARGET and PROJECT_PROPERTIES to a shelve object/file"""
        if config.project_save_path == None:  #saving for first time this session
            save_path = self.get_save_path()
            if save_path is not None:
                self.really_save(save_path[0], save_path[1])
            else:
                return None

        else:   # saving for at least second time in current session
            save_path = config.project_save_path
            show_dialog = False
            self.really_save(save_path, show_dialog)

    def really_save(self, save_path, show_dialog):

        psource = pickle.dumps(config.SOURCE)
        ptarget = pickle.dumps(config.TARGET)
        pproperties = pickle.dumps(config.PROJECT_PROPERTIES)

        save_target = zipfile.ZipFile(save_path, mode='w')
        save_target.writestr('SOURCE', psource)
        save_target.writestr('TARGET', ptarget)
        save_target.writestr('PROJECT_PROPERTIES', pproperties)
        save_target.close()

        if show_dialog == True:
            msg = config.app.translate('main_window', 'Project saved to: {0}'.format(save_path), 'really_save')
            msgbox = QMessageBox(1, config.app.translate('main_window', 'Save FrITA project', 'really_save msgbox title'), msg)
            msgbox.exec_()

        svmsg = config.app.translate('main_window', 'Saved to {0}'.format(save_path), 'really_save')
        self.statusbar.showMessage(svmsg, 2500)

    def project_open(self):
        open_path = QFileDialog.getOpenFileName(self, caption=config.app.translate('main_window', 'Open', 'project open')\
                                                , directory=config.BASE_DIR, filter='*.frita')
        config.project_save_path = open_path
        try:
            open_zip = zipfile.ZipFile(open_path)
        except:
            # show an error to the user
            return None

        is_fritaproj = False
        namelist = open_zip.namelist()

        if 'SOURCE' in namelist and 'TARGET' in namelist and 'PROJECT_PROPERTIES' in namelist:
            is_fritaproj = True

        if is_fritaproj == True:
            for name in namelist:
                obj = open_zip.open(name, mode='r')
                unp_obj = pickle.load(obj)
                if name == 'SOURCE':
                    config.SOURCE = unp_obj
                if name == 'TARGET':
                    config.TARGET = unp_obj
                if name == 'PROJECT_PROPERTIES':
                    config.PROJECT_PROPERTIES = unp_obj

            self.view.MODEL.reset()
            source = []
            target = []
            self.update_statusbar()
            self.setup_model()

            print('880>>', len(config.SOURCE), len(config.TARGET))

        else:
            err = config.app.translate('main_window', 'Cannot open file: {0} '.format(open_path), 'error message, {pathname}')
            title = config.app.translate('main_window', 'File error', 'error message title')
            self.error_message(err, title)

        open_zip.close()
        config.undostack.clear()

    def not_implemented(self):      #DON'T TRANSLATE THIS
        title = 'not implemented'
        err = 'Not implemented yet!'
        self.error_message(err, title)


    def create_tmx(self):
        vmod = self.view.model()
#        lengths = (len(config.SOURCE), len(config.TARGET) )
        rc = max((len(config.SOURCE), len(config.TARGET)) )
        proceed = True
    # be sure to validate tmx options before trying to create a tmx!
        for v in config.PROJECT_PROPERTIES.values():
            if v == None:
                proceed = False

        if proceed == True:
            tmx_options_dialog = tmx_dialog()
            tmx_options_dialog.exec_()
        else:
            err = config.app.translate('main_window', 'Your project is empty!', 'no project,tmx validation')
            title = config.app.translate('main_window', 'TMX error', 'no project,tmx validation')
            self.error_message(err, title)


    def about_frita(self):
        """License info for FrITA and third party code distributed with the bare package."""
        dial = QDialog(self)
        dial.setWindowTitle(config.app.translate('main_window', 'About {0}'.format(config.APP_NAME), 'about frita'))

        tab_widget = QTabWidget()
        # license text and label strings
        icon_path = os.path.join(config.INSTALL_PATH, 'icons', 'app_icon.png')

        name_version = config.app.translate('main_window', """<p><img src="{iconpath}">
                                            &nbsp;&nbsp;&nbsp;&nbsp;<b>This is {appname}</b>
                                            <b>&nbsp;&nbsp;Version: {version}</b></p>
                                            <p>Copyright &copy; <b>Gregory Vigo Torres</b> 2013</p>
                                            <p>Unless otherwise stated,
                                            all modules or libraries included with this software
                                            are licensed under the GPL v.3.</p>
                                            """.format(iconpath = icon_path, appname=config.APP_NAME, version=config.VERSION )\
                                            , 'about frita')


        bfile = os.path.join(config.INSTALL_PATH, 'backers')
        obfile = open(bfile, mode='r')
        backers_html = obfile.read()
        obfile.close()

        li = os.path.join(config.INSTALL_PATH, 'license', 'gplv3.html')
        olf = open(li, mode='r')
        gplv3 = olf.read()
        olf.close()

        li = os.path.join(config.INSTALL_PATH, 'license', 'third_party')
        olf = open(li, mode='r')
        mit_html = olf.read()
        olf.close()

        # widgets
        browser = QTextBrowser()
        browser.setHtml(gplv3)
        browser.setReadOnly(True)

        about = QTextEdit()
        about.setHtml(name_version)
        about.setReadOnly(True)

        backers = QTextEdit()
        backers.setHtml(backers_html)
        backers.setReadOnly(True)

        thirdparty = QTextEdit()
        thirdparty.setHtml(mit_html)
        thirdparty.setReadOnly(True)

        # insert widgets into tabwidget
        tab_widget.insertTab(0, about, config.app.translate('main_window', 'About FrITA', 'about frita tab') )
        tab_widget.insertTab(1, browser, config.app.translate('main_window', 'GPL v.3', 'about frita tab') )
        tab_widget.insertTab(2, backers, config.app.translate('main_window', 'v 1.0 Backers', 'about frita tab') )
        tab_widget.insertTab(3, thirdparty, config.app.translate('main_window', 'Third party', 'about frita tab') )

        closeButton = QPushButton(config.app.translate('main_window', 'Close', 'about frita') )
        buttonBox = QDialogButtonBox(Qt.Horizontal)
        buttonBox.addButton(closeButton, QDialogButtonBox.RejectRole)

        layout = QGridLayout()
        layout.setMargin(0)
        layout.addWidget(tab_widget, 0, 0)
        layout.addWidget(buttonBox, 1, 0)
        layout.setColumnMinimumWidth(0, 500)
        layout.setSizeConstraint(QLayout.SetFixedSize)

        closeButton.pressed.connect(dial.close)

        dial.setLayout(layout)
        dial.exec_()

    def quit(self):     # add a confirm alert here
        """quits FrITA"""
        config.app.closeAllWindows()
        config.app.quit()

## file filters and segmentation
    def setup_model(self):
        """Makes source and target the same length and resets model with new data.
        It is assumed that there are no blank lines in source or target"""

        source = []
        target = []
        both = itertools.zip_longest(config.SOURCE, config.TARGET, fillvalue='')

        for s, t in both:
            source.append(s)
            target.append(t)

        config.SOURCE = source
        config.TARGET = target

##        print("""setup_model:
##        len(config.SOURCE)={0}
##        len(config.TARGET)={1}""".format(len(config.SOURCE), len(config.TARGET)) )

#       get the model/view started!
        self.view.MODEL.reset()
        self.update_statusbar()


    def file_filter(self):
        """ sets SOURCE and TARGET """

        def remove_empty_items(segmented_text):
            segmented_text = [ i for i in segmented_text if len(i)>0 ]
            segmented_text = [ i for i in segmented_text if i.isspace() == False ]
            return segmented_text

        filenames = [(config.PROJECT_PROPERTIES['sfilename'], config.PROJECT_PROPERTIES['slang']),
                    (config.PROJECT_PROPERTIES['tfilename'], config.PROJECT_PROPERTIES['tlang']) ]

        for name, lang in filenames:
            ext = os.path.splitext(name)[1]
            text = None

            file_open_error = config.app.translate('main_window',
            '{0} cannot be opened. The encoding or the file type is not supported.'.format(name),
            'file import error')

            err_title = config.app.translate('main_window',
            'File error', 'file import error')

            if ext == '.docx':
                document = docx.opendocx(name)
                paratextlist = docx.getdocumenttext(document)
                text = [p+'\n' for p in paratextlist]

            elif ext == '.odt':
                text = importOdt.get_writer_doc(name)

            elif re.match('(\.x?(htm)l?)|(\.php)', ext):    # treats php like html
                # possible KW options for html parser: get_meta=True, get_img_meta=False
                text = parse_html.to_text_list(name)

            elif ext == '.txt':
                file_obj = open(name, mode='rb')
                as_bytes = file_obj.read()
                text = self.decode_text_file(as_bytes)

                if text:
                    text = text.splitlines()
                else:
                    self.error_message(file_open_error, err_title)
                    text = None

            elif len(ext) == 0:     # try to open files without an extension as plain text
                istext = self.is_plain_text(name)

                if istext is True:
                    as_bytes = open(name, mode='rb').read()
                    text = self.decode_text_file(as_bytes)
                    text = text.splitlines()

                if istext is False or text is None:
                    self.error_message(file_open_error, err_title)


            elif ext == '.tmx':     # not implemented YET
                self.error_message(file_open_error, err_title)
                text = None

            else:
                self.error_message(file_open_error, err_title)
                text = None


            if text:
                segmented_text = self.segment_text(text, lang)

                if segmented_text:
                    segmented_text = remove_empty_items(segmented_text)

                    if lang == config.PROJECT_PROPERTIES['slang']:
                        config.SOURCE = segmented_text
                    if lang == config.PROJECT_PROPERTIES['tlang']:
                        config.TARGET = segmented_text

##                    print("""debug file_filter: filename={0} :
##                    len(segmented_text)={1} :
##                    lang={2}""".format(name, len(segmented_text), lang) )

        self.setup_model()

    def segment_text(self, text, lang):
        parse = segment.parse_rules(config.RULESDB, lang)

        if parse.error is True:
            err = config.app.translate('parse_rules',
            """There are no language specific rules for {0} in the segmentation rules database.\n
            Using default rules only.""".format(lang),
            'no rules for language in rules database')

            title = config.app.translate('parse_rules', 'Warning')

            err_msg = QMessageBox()
            err_msg.setText(err)
            err_msg.setWindowTitle(title)
            err_msg.exec_()

        break_rules = parse.break_rules
        skip_rules = parse.skip_rules
        seg = segment.segment(break_rules, skip_rules, text)

        return seg.segmented_text

    def is_plain_text(self, name):
        """ If there are more than 10 null bytes then the file is probably not plain text.
       If there are more non-printable characters than printable ones, the file is probably not plain text. """

        with open(name, mode='rb') as afile:
            fn = afile.read(512)
            npchars = [chr(c) for c in fn if c < 31 ]
            textchars = [chr(c) for c in fn if c > 32]

            if  npchars.count('\x00') > 10:
                return False

            if textchars.count('0') > 10:
                return False

            if len(npchars) > len(textchars):
                return False

            else:
                return True


    def decode_text_file(self, as_bytes):
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
                decoded_data = as_bytes.decode(enc, errors='strict')
                return decoded_data

            except:
                continue



## main
def main():
    config.app = QApplication(sys.argv)
    # get install dir, make sure this ALWAYS works
    config.INSTALL_PATH = sys.path[0]
    config.FONT = config.app.font()
    config.app.setAttribute(Qt.AA_NativeWindows, on=True)
    config.app.quitOnLastWindowClosed()
# load translator here, before creating widgets
    MAIN_WINDOW = main_window()
    MAIN_WINDOW.show()

    sys.exit(config.app.exec_())

if __name__ == '__main__':
    #cProfile.run('main()' )
    main()
