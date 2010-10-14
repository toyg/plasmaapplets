# -*- coding: utf-8 -*-
# /
# tc_models.py - part of TaskPlasma
# Copyright (c) 2010 Giacomo Lacava - g.lacava@gmail.com
#
# Licensed under the European Union Public License, Version 1.1.
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at http://ec.europa.eu/idabc/eupl5
# Unless required by applicable law or agreed to in writing, software distributed 
# under the Licence is distributed on an "AS IS" basis, WITHOUT WARRANTIES OR 
# CONDITIONS OF ANY KIND, either express or implied.
# See the Licence for the specific language governing permissions and limitations 
# under the Licence.
# /


import xml.etree.ElementTree as etree 

from PyQt4.QtCore import Qt, QModelIndex, QVariant, QAbstractListModel, \
                        QAbstractItemModel, QFile, QIODevice
from PyQt4.QtGui import QStringListModel, QFont, QBrush, QColor
from PyQt4.QtXml import QDomDocument, QDomNode

class DomItem(object):
    def __init__(self, node, row, parent=None):
        self.domNode = node
        # Record the item's location within its parent.
        self.rowNumber = row
        self.parentItem = parent
        self.childItems = {}

    def node(self):
        return self.domNode

    def parent(self):
        return self.parentItem

    def child(self, i):
        if i in self.childItems:
            return self.childItems[i]

        if i >= 0 and i < self.domNode.childNodes().count():
            childNode = self.domNode.childNodes().item(i)
            if childNode.nodeName() in ["task","tasks"]:
                childItem = DomItem(childNode, i, self)
                self.childItems[i] = childItem
                return childItem

        return None

    def row(self):
        return self.rowNumber
        
class TaskListModel(QAbstractItemModel):
    def __init__(self, filePath, parent=None):
        super(TaskListModel, self).__init__(parent)
        
        f = QFile(filePath)
        if f.open(QIODevice.ReadOnly):
            document = QDomDocument()
            if document.setContent(f):
                self.xmlPath = filePath
            f.close()
        
            self.domDocument = document
    
            # using documentElement we bypass the root node
            self.rootItem = DomItem(self.domDocument.documentElement(), 0)

    def columnCount(self, parent):
        return 2

    def data(self, index, role):
        if not index.isValid():
            return None

        item = index.internalPointer()
        node = item.node()
        attributes = []
        attributeMap = node.attributes()
        
        if role == Qt.DisplayRole:
            if index.column() == 0:
                return attributeMap.namedItem("subject").nodeValue()
            elif index.column() == 1:
                return attributeMap.namedItem(
                                    "percentageComplete").nodeValue().toInt()[0]
            return None
            
        elif role == Qt.CheckStateRole:
            if index.column() == 0:
                if attributeMap.namedItem(
                                    "percentageComplete").nodeValue() == "100": 
                    return Qt.Checked
                else:
                    return Qt.Unchecked
                
        elif role == Qt.FontRole:
            if index.column() == 0:
                font = QFont()
                if attributeMap.namedItem(
                                    "percentageComplete").nodeValue() == "100":
                    font.setStrikeOut(True)
                else:
                    font.setStrikeOut(False)
                return font
            
        elif role == Qt.ForegroundRole:
            if index.column() == 0:            
                if attributeMap.namedItem(
                                    "percentageComplete").nodeValue() == "100":
                    brush = QBrush()
                    brush.setColor(QColor("grey"))
                    return brush
                
        return None
        
        
    def setData(self, index, value, role):
        if not index.isValid():
            return False
        item = index.internalPointer().node()
        if role == Qt.CheckStateRole:
            # a checkbox was modified
            progress, success = value.toInt()
            item.toElement().setAttribute("percentageComplete",str(progress*50))
            # check children
            numChildren = item.childNodes().count()
            if numChildren > 0 and progress == Qt.Checked:
                for i in xrange(0,numChildren):
                    self.setData(index.child(i,0),value,role)
                self.dataChanged.emit(index,index.child(numChildren-1,0))
            if progress == Qt.Unchecked:
                self.setData(index.parent(),value,role)
                self.dataChanged.emit(index.parent(),index)
            return True
            
        elif role == Qt.EditRole:
            if index.column() == 0:
                # task desc
                item.toElement().setAttribute("subject",
                                                    unicode(value.toString()))
                self.dataChanged.emit(index,index)
                return True
                
            elif index.column() == 1:
                # task progress
                item.toElement().setAttribute("percentageComplete",
                                                        str(value.toString())) 
                self.dataChanged.emit(index,index)
                
                progress, success = value.toInt()
                if progress == 100:                
                    # if task is now completed, update children
                    # FIXME: this doesn't work and I don't understand why :(
                    numChildren = item.childNodes().count()
                    if numChildren > 0:
                        for i in xrange(0,numChildren):
                            self.setData(index.child(i,1),value,role)
                        self.dataChanged.emit(index,index.child(numChildren-1,1))
                        return True
                        
                elif progress < 100:
                    # if task is now NOT complete and parent is, update parent.
                    # this works
                    if self.data(index.parent(),Qt.CheckStateRole) == Qt.Checked:
                        parentIndex = self.index(index.parent().row(),index.column(),index.parent().parent())
                        self.setData(parentIndex,value,role)
                        self.dataChanged.emit(index.parent(),index)
                    return True
                return True
        # for everything else, do the generic thing
        return QAbstractItemModel.setData(self,index,value,role)


    def flags(self, index):
        if not index.isValid():
            return Qt.NoItemFlags
            
        if index.column() == 0:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable \
                                    | Qt.ItemIsUserCheckable
        elif index.column() == 1:
            return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable 

    def headerData(self, section, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            if section == 0:
                return "Tasks"
            elif section == 1:
                return "%"

        return None

    def index(self, row, column, parent):
        if not self.hasIndex(row, column, parent):
            return QModelIndex()

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()

        childItem = parentItem.child(row)
        
        if childItem:
            return self.createIndex(row, column, childItem)
        else:
            return QModelIndex()

    def parent(self, child):
        if not child.isValid():
            return QModelIndex()

        childItem = child.internalPointer()
        parentItem = childItem.parent()

        if not parentItem or parentItem == self.rootItem:
            return QModelIndex()

        return self.createIndex(parentItem.row(), 0, parentItem)

    def rowCount(self, parent):
        if parent.column() > 0:
            return 0

        if not parent.isValid():
            parentItem = self.rootItem
        else:
            parentItem = parent.internalPointer()
            
        numChildNodes = 0
        children = parentItem.node().childNodes()
        for i in xrange(0,children.count()):
            if children.at(i).nodeName() in ["task","tasks"]:
                numChildNodes += 1
        return numChildNodes




