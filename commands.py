#FrITA - Free Interactive Text Aligner
#The easy to use bilingual text aligner for creating tmx translation memories

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

## Undoable commands

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import sys
import config

class edit_text(QUndoCommand):    # this could use config.cur_text...
    def __init__(self, delegate, editor, model, index, odata, value, description):
        super(edit_text, self).__init__(description)
        self.delegate = delegate
        self.model = model
        self.editor = editor
        self.value = value
        self.index = index
        # index here is a persistent model index
        self.model = self.index.model()
        self.original_data = odata
        self.row = self.index.row()
        self.col = self.index.column()

    def redo(self):
        self.model.beginResetModel()

        if self.col == 0:
            config.SOURCE[self.row] = self.value
        if self.col == 1:
            config.TARGET[self.row] = self.value

        self.model.reset()
        self.model.endResetModel()


    def undo(self):
        self.model.beginResetModel()

        if self.col == 0:
            config.SOURCE[self.row] = self.original_data
        if self.col == 1:
            config.TARGET[self.row] = self.original_data

        self.model.reset()
        self.model.endResetModel()
##

class insert_blank_cell(QUndoCommand):
    def __init__(self, table, row, col, description):
        super(insert_blank_cell, self).__init__(description)
        self.table = table
        self.row = row
        self.col = col

    def redo(self):
        self.table.MODEL.beginResetModel()

        if self.col == 0:
            config.SOURCE.insert(self.row, '...')

        if self.col == 1:
            config.TARGET.insert(self.row, '...')

        self.table.MODEL.reset()
        self.table.MODEL.endResetModel()


    def undo(self):
        self.table.MODEL.beginResetModel()

        if self.col == 0:
            del config.SOURCE[self.row]

        if self.col == 1:
            del config.TARGET[self.row]

        self.table.MODEL.reset()
        self.table.MODEL.endResetModel()

##

class remove_cell(QUndoCommand):
    def __init__(self, table, row, col, description):
        super(remove_cell, self).__init__(description)
        self.table = table
        self.row = row
        self.col = col

        if self.col == 0:
            self.deleted_text = config.SOURCE[self.row]
        if self.col == 1:
            self.deleted_text = config.TARGET[self.row]

    def redo(self):
        self.table.MODEL.beginResetModel()

        if self.col == 0:
            del config.SOURCE[self.row]

        if self.col == 1:
            del config.TARGET[self.row]

        self.table.MODEL.reset()
        self.table.MODEL.endResetModel()

    def undo(self):
        self.table.MODEL.beginResetModel()

        if self.col == 0:
            config.SOURCE.insert(self.row, self.deleted_text)

        if self.col == 1:
            config.TARGET.insert(self.row, self.deleted_text)

        self.table.MODEL.reset()
        self.table.MODEL.endResetModel()
##

class insert_blank_row(QUndoCommand):
    def __init__(self, table, row, description):
        super(insert_blank_row, self).__init__(description)
        self.table = table
        self.row = row

    def redo(self):
        self.table.MODEL.insertRow(self.row)

    def undo(self):
        self.table.MODEL.removeRow(self.row)
##

class remove_entire_row(QUndoCommand):
    def __init__(self, table, row, description):
        super(remove_entire_row, self).__init__(description)
        self.table = table
        self.row = row

        self.sitem = config.SOURCE[self.row]
        self.titem = config.TARGET[self.row]

    def redo(self):
        # items deleted from SOURCE and TARGET in MODEL
        self.table.MODEL.removeRow(self.row)

    def undo(self):
        self.table.MODEL.beginResetModel()
        # source
        config.SOURCE.insert(self.row, self.sitem)
        # target
        config.TARGET.insert(self.row, self.titem)

        self.table.MODEL.reset()
        self.table.MODEL.endResetModel()

##

class merge_with_next(QUndoCommand):
    def __init__(self, table, row, col, description):
        super(merge_with_next, self).__init__(description)
        
        self.row = row
        self.col = col
        self.table = table

        if self.col == 0:
            self.first_part = config.SOURCE[row]
            self.second_part = config.SOURCE[row+1]

        if self.col == 1:
            self.first_part = config.TARGET[row]
            self.second_part = config.TARGET[row+1]

        self.merged = self.first_part.strip()+' '+self.second_part.strip()

    def redo(self):
        self.table.MODEL.beginResetModel()
        if self.col == 0:
            del config.SOURCE[self.row+1]
            config.SOURCE[self.row] = self.merged
            if config.TARGET[-1].isspace() or len(config.TARGET[-1]) < 1:
                config.TARGET.pop()

        if self.col == 1:
            del config.TARGET[self.row+1]
            config.TARGET[self.row] = self.merged
            if config.SOURCE[-1].isspace() or len(config.SOURCE[-1]) < 1:
                config.SOURCE.pop()


        self.table.MODEL.endResetModel()
    
    def undo(self):
        self.table.MODEL.beginResetModel()
        if self.col == 0:
            config.SOURCE[self.row]=self.first_part           
            config.SOURCE.insert(self.row+1, self.second_part)
            
        if self.col == 1:
            config.TARGET[self.row]=self.first_part           
            config.TARGET.insert(self.row+1, self.second_part)

        self.table.MODEL.endResetModel()

##

class merge_with_previous(QUndoCommand):
    def __init__(self, table, row, col, description):
        super(merge_with_previous, self).__init__(description)

        self.row = row
        self.col = col
        self.table = table

        if self.col == 0:
            self.first_part = config.SOURCE[row-1]
            try:
                self.second_part = config.SOURCE[row]
            except:
                self.second_part = ''

        if self.col == 1:
            self.first_part = config.TARGET[row-1]
            try:
                self.second_part = config.TARGET[row]
            except:
                self.second_part = ''

        self.merged = self.first_part.strip()+' '+self.second_part.strip()

    def redo(self):
        self.table.MODEL.beginResetModel()
        if self.col == 0 and len(self.second_part) > 0:
            del config.SOURCE[self.row]
            config.SOURCE[self.row-1] = self.merged
            if config.TARGET[-1].isspace() or len(config.TARGET[-1]) < 1:
                config.TARGET.pop()
        
        if self.col == 1 and len(self.second_part) > 0:
            del config.TARGET[self.row]
            config.TARGET[self.row-1] = self.merged
            if config.SOURCE[-1].isspace() or len(config.SOURCE[-1]) < 1:
                config.SOURCE.pop()

        self.table.MODEL.endResetModel()

    def undo(self):
        self.table.MODEL.beginResetModel()
        if self.col == 0:
            config.SOURCE[self.row-1]=self.first_part
            config.SOURCE.insert(self.row, self.second_part)
            if self.row > len(config.SOURCE):
                config.SOURCE.append(self.second_part)

        if self.col == 1:
            config.TARGET[self.row-1]=self.first_part
            config.TARGET.insert(self.row, self.second_part)
            if self.row > len(config.TARGET):
                config.TARGET.append(self.second_part)

        self.table.MODEL.endResetModel()



##

class merge_selected(QUndoCommand):
    def __init__(self, table, selections, description):
        super(merge_selected, self).__init__(description)

        self.selections = selections
        self.table = table
        self.model = self.table.MODEL
        self.ssegs = [i.data()+' ' for i in self.selections if i.column() == 0]
        self.tsegs = [i.data()+' ' for i in self.selections if i.column() == 1]
        self.top = self.selections[0].row()
#        e = self.selections[-1:]
#        self.end = e[0].row()
        self.end = self.selections[-1:][0].row()

    def redo(self):
        sdata = ''.join(self.ssegs)
        tdata = ''.join(self.tsegs)

        if len(self.ssegs) > 0: # SOURCE
            self.model.beginResetModel()
            config.SOURCE[self.top] = sdata
            
            # avoids empty rows at the end
            end = len(config.TARGET)-1
            for i in range(len(config.SOURCE[self.top+1:self.end+1] ) ):
                last = ''.join(config.TARGET[end] )
                if last.isspace() or len(last) == 0:
                    del config.TARGET[end]
                end -= 1
            
            del config.SOURCE[self.top+1:self.end+1]

            self.model.endResetModel()
            cur = self.selections[0]
            self.table.setCurrentIndex(cur)

        if len(self.tsegs) > 0: # TARGET
            self.model.beginResetModel()
            config.TARGET[self.top] = tdata
            
            end = len(config.SOURCE)-1
            for i in range(len(config.TARGET[self.top+1:self.end+1] ) ):
                last = ''.join(config.SOURCE[end] )
                if last.isspace() or len(last) == 0:
                    del config.SOURCE[end]
                end -= 1
            
            del config.TARGET[self.top+1:self.end+1]
            
            self.model.endResetModel()
            cur = self.selections[0]
            self.table.setCurrentIndex(cur)

    def undo(self):
        if len(self.ssegs) > 0: # SOURCE
            self.model.beginResetModel()
            ind = self.top
            del config.SOURCE[self.top:self.end]

            for i in self.ssegs:
                if ind <= self.end:
                    config.SOURCE.insert(ind, i)
                    ind += 1

            self.model.endResetModel()
            cur = self.selections[0]
            self.table.setCurrentIndex(cur)

        if len(self.tsegs) > 0: # TARGET
            self.model.beginResetModel()
            ind = self.top
            del config.TARGET[self.top:self.end-1]
            
            for i in self.tsegs:
                if ind <= self.end:
                    config.TARGET.insert(ind, i)
                    ind += 1
           
            self.model.endResetModel()
            cur = self.selections[0]
            self.table.setCurrentIndex(cur)
##

class splitSegment(QUndoCommand):
    def __init__(self, table, row, col, cur_pos, description):
        super(splitSegment, self).__init__(description)
        self.table = table
        self.row = row
        self.col = col
        self.cur_pos = cur_pos

        if self.col == 0:
            self.segment = config.SOURCE[self.row]
        if self.col ==1:
            self.segment = config.TARGET[self.row]

        self.first_part = self.segment[:self.cur_pos].rstrip()
        self.second_part = self.segment[self.cur_pos:].lstrip()

    def redo(self):
        self.table.MODEL.beginResetModel()

        if self.col == 0:
            config.SOURCE[self.row] = self.first_part
            config.SOURCE.insert(self.row+1, self.second_part)

        if self.col == 1:
            config.TARGET[self.row] = self.first_part
            config.TARGET.insert(self.row+1, self.second_part)

        self.table.MODEL.endResetModel()

    def undo(self):
        self.table.MODEL.beginResetModel()

        if self.col == 0:
            config.SOURCE[self.row] = self.segment
            del config.SOURCE[self.row+1]

        if self.col == 1:
            config.TARGET[self.row] = self.segment
            del config.TARGET[self.row+1]

        self.table.MODEL.endResetModel()

##
