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
import itertools
import collections
import commands
from commands import *
import config

class delegateEditor(QTextEdit):             # editor for delegate
    def __init__(self, widget=None):
        super(delegateEditor, self).__init__(widget)

        self.setAcceptRichText(True)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        #styles
        stylesheet = "* { background-color: yellow; border: 1px solid black; }"
        self.setStyleSheet(stylesheet)
        # highlight split/TextCharFormats
        self.seg_bg = QTextCharFormat()
        nice_light_blue = QColor().fromRgb(59, 168, 242, 100)
        self.seg_bg.setBackground(nice_light_blue)

        self.def_bg = QTextCharFormat()
        self.def_bg.setBackground(Qt.yellow)

        # document, margins & size
        document = self.document()
        document.setMaximumBlockCount(1)
        document.setDocumentMargin(0.0)

        #actions
        self.textChanged.connect(self.c_text)
        self.cursorPositionChanged.connect(self.getCursor)
        self.c_pos = 0

    def c_text(self):
        config.cur_text = self.toPlainText()
        config.text_changed = True

    def getCursor(self):        # connected to split and highlight split!
        self.c = self.textCursor()
        self.c_pos = self.c.position()
        parent = self.parent()
        view = parent.parent()
        view.cur_pos = self.c_pos
        self.highlight_split()

    def highlight_split(self):
        self.c.movePosition( 4, 0, 1  )
        self.c.movePosition( 17, 1, self.c_pos  )
        self.c.setCharFormat(self.seg_bg)    # sets different bg color
        self.c.movePosition(17, 0, 1)
        self.c.movePosition(15, 1, 1)
        self.c.setCharFormat(self.def_bg)    # restores default yellow bg color

    def keyPressEvent(self, event): #captures return key
        if event.key() == 16777220:            ##Qt.Key_Return
            event.ignore()
            self.close()
        elif event.key() == 16777221:           ##Qt.Key_Enter:
            event.ignore()
            self.close()
        else:
            QTextEdit.keyPressEvent(self, event)

##

class editorDelegate(QStyledItemDelegate):      # main item delegate
    def __init__(self, parent):
        super(editorDelegate, self).__init__()

    def createEditor(self, parent, option, index):
        if index.isValid():
            text = index.model().data(index, Qt.EditRole)
            editor = delegateEditor(parent)
            return editor

    def setEditorData(self, editor, index):     ## original data sent to editor widget
        if index.isValid():
            text = index.model().data(index, Qt.EditRole)
            editor.setText(text)
            self.sizeHintChanged.emit(index)


    def setModelData(self, editor, model, index):   ## value is data sent to MODEL after being edited
        if index.isValid():
            value = editor.toPlainText()    #this is the edited text
            # use persistent model index
            pindex = QPersistentModelIndex(index)
            if pindex.isValid():
                if pindex.column() == 0 and pindex.row() < len(config.SOURCE):
                    odata = config.SOURCE[pindex.row()]

                    if config.text_changed:
                        command = commands.edit_text(self, editor, model, pindex, odata, value, \
                                                     config.app.translate('editorDelegate', 'edit text', 'command') )
                        config.undostack.push(command)

                if pindex.column() == 1 and pindex.row() < len(config.TARGET):
                    odata = config.TARGET[pindex.row()]

                    if config.text_changed:
                        command = commands.edit_text(self, editor, model, pindex, odata, value, \
                                                     config.app.translate('editorDelegate', 'edit text', 'command') )
                        config.undostack.push(command)

                self.commitData.emit(editor)
                model.setData(index, value, Qt.EditRole)
                self.closeEditor.emit(editor, 3)

##

class view_model(QAbstractTableModel):      # main model
    numberPopulated = pyqtSignal(int)
    def __init__(self, parent):
        super(view_model, self).__init__(parent)

        self.seg_count = 0
        self.cur_row = None
        self.cur_delegate = editorDelegate(self)
        self.bad_rows = []

        self.dataChanged.connect(self.mismatch)
        # parent is main_view
        self.dataChanged.connect(parent.resizeRowsToContents)
        self.modelReset.connect(parent.resizeRowsToContents)

    def mismatch(self):
        self.bad_rows = []

        if len(config.SOURCE) == len(config.TARGET):
            r = 0
            zp = zip(config.SOURCE, config.TARGET)
            for s, t in zp:
                slen = len(s)
                tlen = len(t)
##                print("""main_view.mismatch:
##                slen={0}
##                tlen={1}""".format(slen, tlen) )
                if slen > 0 and tlen > 0:
                    dif = slen / tlen
                    if dif < 0.8 or dif > 1.3:
                        self.bad_rows.append(r)
                r += 1

    def data(self, index, role):
        #source
        if index.column() == 0:
            if role == Qt.DisplayRole:
                row = index.row()
                try:
                    segment = config.SOURCE[row]
                    return segment
                except IndexError:
##                    print("""main_view.data - source:
##                            exception: {0}
##                            source rowcount error at {1}""".format(sys.exc_info(), row) )
                    return None

            if role == Qt.EditRole:
                return index.data()
        #target
        if index.column() == 1:
            if role == Qt.DisplayRole:
                row = index.row()
                try:
                    segment = config.TARGET[row]
                    return segment
                except IndexError:
##                    print("""main_view.data - target:
##                            exception: {0}
##                            source rowcount error at {1}""".format(sys.exc_info(), row))
                    return None

            if role == Qt.EditRole:
                return index.data()

        if index.row() == self.cur_row:
            if role == Qt.BackgroundRole:
                hbg = QBrush(Qt.yellow)
                return hbg

            if role == Qt.BackgroundRole:
                if index.row() % 2 == 0:
                    return qApp.palette().base()
                elif index.row() %2 != 0:
                    return qApp.palette().alternateBase()

        if role == Qt.TextAlignmentRole:
            alignment = Qt.Alignment(Qt.AlignTop)
            return alignment

        #highlight mismatch
        if index.isValid():
            red = QBrush(Qt.red)
            if index.row() in self.bad_rows and role == Qt.ForegroundRole:
                return red
            elif role == Qt.ForegroundRole:
                return qApp.palette().foreground()

        return None

    def canFetchMore(self, index):
        return self.seg_count < max(config.real_row_count)

    def fetchMore(self, index):
        remainder = max(config.real_row_count) - self.seg_count
        segs_to_fetch = max(0, remainder)
        last = self.seg_count+segs_to_fetch

        if last < max(config.real_row_count):
            self.beginInsertRows(QModelIndex(), self.seg_count, last)
            self.seg_count += segs_to_fetch
            self.endInsertRows()
            self.numberPopulated.emit(segs_to_fetch)

    def setData(self, index, value, role):
        if role == Qt.EditRole:     ## edit segment text
            if index.isValid() and index.column() == 0:
                row = index.row()
                try:
                    config.SOURCE[row] = value
                    self.dataChanged.emit(index, index)
                    return True
                except IndexError:
                    config.SOURCE.append('')
                    self.dataChanged.emit(index, index)
                    return True


        if role == Qt.EditRole:     ## edit segment text
            if index.isValid() and index.column() == 1:
                row = index.row()
                try:
                    config.TARGET[row] = value
                    self.dataChanged.emit(index, index)
                    return True
                except IndexError:
                    config.TARGET.append('')
                    self.dataChanged.emit(index, index)
                    return True

        return None

    def insertRow(self, row, parent=QModelIndex() ):
        self.beginResetModel()
        
        before = config.SOURCE[:row]
        after = config.SOURCE[row:]
        before.append('...')
        config.SOURCE = before+after

        before = config.TARGET[:row]
        after = config.TARGET[row:]
        before.append('...')
        config.TARGET = before+after

        self.endResetModel()
        return True

    def removeRow (self, row, parent=QModelIndex() ):
        self.beginResetModel()
        del config.SOURCE[row]
        del config.TARGET[row]
        self.reset()
        self.endResetModel()

    def index(self, row, column, parent=QModelIndex() ):
        return self.createIndex(row, column, object)

    def flags(self, index):
        if index.isValid():
            return Qt.ItemIsEditable|Qt.ItemIsSelectable|Qt.ItemIsEnabled

    def rowCount(self, parent=QModelIndex() ):
        if parent.isValid() == True:
            return 0

        def prune(shorten_me):
            last_ind = len(shorten_me)-1
            while last_ind > 0:
                last = shorten_me[last_ind]
                if last.isspace() or len(last ) == 0:
                    shorten_me.pop()
                else:
                    break
                last_ind -= 1

        if len(config.TARGET) != len(config.SOURCE):
            prune(config.SOURCE)
            prune(config.TARGET)
            slen = len(config.SOURCE)
            tlen = len(config.TARGET)
            dif = abs(slen-tlen)
        
            if slen > tlen:
                spaces = ['' for i in range(dif)]
                config.TARGET.extend(spaces)
        
            if slen < tlen:
                spaces = ['' for i in range(dif)]
                config.SOURCE.extend(spaces)

            self.mismatch()
            return len(config.SOURCE)

        else:
            if config.SOURCE[-1].isspace() or len(config.SOURCE[-1]) < 1:
                prune(config.SOURCE)
              
            if config.TARGET[-1].isspace() or len(config.TARGET[-1]) < 1:
                prune(config.TARGET)
            
            self.mismatch()
            return len(config.SOURCE)


    def columnCount(self, parent):
        return 2

    def headerData (self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return config.app.translate('view', 'Source', 'column header')
            if section == 1:
                return config.app.translate('view', 'Target', 'column header')

        if orientation == Qt.Vertical and role == Qt.DisplayRole:
            return section+1


##

class view(QTableView):     #most commands referenced here
    def __init__(self, parent):
        super(view, self).__init__(parent)

        self.MODEL = view_model(self)
        self.setModel(self.MODEL)

        # view properties
        self.setSortingEnabled(False)
        self.setItemDelegate(editorDelegate(self) )
        self.setMouseTracking(True)
            # visual characteristics
        self.setWordWrap(True)
        self.setAlternatingRowColors(True)

        h_header = self.horizontalHeader()
        h_header.setResizeMode(1)

        self.v_header = self.verticalHeader()
        self.v_header.setMovable(True)
        self.v_header.setResizeMode(0)

        # actions/events
        self.cur_pos = 0
        self.current_row = None
        self.current_col = None

## highlighting/styles

    def currentChanged(self, current, previous):
        self.current_row = current.row()
        self.current_col = current.column()
        self.highlightCurrentRow(current, previous)
        self.edit(current)
        self.MODEL.mismatch()
        config.text_changed = False

    def highlightCurrentRow(self, current, previous):
        self.MODEL.cur_row = current.row()

## actions in (undoable) commands
## also edit text, see commands & main delegate
    def merge_down(self):
        command = commands.merge_with_next(self, self.current_row, self.current_col, \
                                           config.app.translate('view', 'Merge with next segment', 'command') )

        try:
            config.undostack.push(command)
        except:
            pass


    def merge_up(self):
        command = commands.merge_with_previous(self, self.current_row, self.current_col, \
                                           config.app.translate('view', 'Merge with previous segment', 'command') )

        try:
            config.undostack.push(command)
        except:
            pass

    def merge_selected(self):
        selections = self.selectedIndexes()
        command = commands.merge_selected(self, selections, config.app.translate('view', 'Merge selected', 'command') )
        config.undostack.push(command)

    def add_row(self):
        command = insert_blank_row(self, self.current_row, config.app.translate('view', 'Insert a blank row', 'command') )
        config.undostack.push(command)

    def add_cell(self):
        command = insert_blank_cell(self, self.current_row, self.current_col, \
                                    config.app.translate('view', 'Insert empty segment', 'command') )
        config.undostack.push(command)

    def remove_cell(self):
        command = remove_cell(self, self.current_row, self.current_col, config.app.translate('view', 'Delete segment', 'command') )
        config.undostack.push(command)

    def del_row(self):
        command = remove_entire_row(self, self.current_row, config.app.translate('view', 'Remove entire row', 'command') )
        config.undostack.push(command)

    def split_segment(self):
        command = splitSegment(self, self.current_row, self.current_col, self.cur_pos, \
                               config.app.translate('view', 'Split segment', 'command') )
        config.undostack.push(command)

    def next_mismatch(self):
        next = 0
        self.MODEL.reset()
        for row in self.MODEL.bad_rows:
            if row > self.current_row:
                next = row
                break

        next_ind = self.MODEL.index(next, 0, QModelIndex())
        self.scrollTo(next_ind, QAbstractItemView.EnsureVisible)
        self.setCurrentIndex(next_ind)


    def goto_seg(self):
        if len(config.SOURCE) > 0 and len(config.TARGET) > 0:
            row = 0
            dia = QDialog()

            label = QLabel(config.app.translate('view', 'Go to row', 'dialog label, row number') )
            enter_no = QLineEdit()
            label.setBuddy(enter_no)

            scroll_to_row = lambda:self.scroll_to_row(enter_no.text() )
            close_dia = lambda: dia.reject()

            # use a standard button
            butt_box = QDialogButtonBox(QDialogButtonBox.Cancel)
            close_butt = butt_box.button(QDialogButtonBox.Cancel)
#            close_butt = QPushButton(config.app.translate('view', 'Close', 'close dialog button'))
            close_butt.clicked.connect(close_dia)


            layout = QGridLayout()
            layout.addWidget(label, 0, 0)
            layout.addWidget(enter_no, 0, 1)
            layout.addWidget(close_butt, 1, 1)
            dia.setLayout(layout)

            dia.finished.connect(scroll_to_row)
            dia.exec_()

    def scroll_to_row(self, row):
        end = max(len(config.SOURCE), len(config.TARGET) )
        # end is visual row

        if len(row) > 0:
            row = int(row)
        else:
            row = 1

        if row > 0:    # row needs to be real row i.e. starts with 0 but can't be -1
            row = row-1

        if row <= end:
            self.setSelectionBehavior(1)
            selected_row = self.selectRow(row)
            ind = self.selectedIndexes()[0]
            self.setCurrentIndex(ind  )
            self.scrollTo(ind)
            self.setSelectionBehavior(0)
        else:
            err_msg = config.app.translate('view', 'You must select a row less than '+str(end), 'goto row error message')
            title = config.app.translate('view', 'Error', 'goto row error dialog title')
            err_box = QMessageBox(2, title, err_msg, buttons=QMessageBox.Close )
            err_box.exec_()



