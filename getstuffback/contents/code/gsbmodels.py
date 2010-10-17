# -*- coding: utf-8 -*-
# /
# gsbmodels.py - part of getstuffback
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

from datetime import datetime
from os.path import exists
import xml.etree.ElementTree as etree
import pickle, uuid, codecs

from toyutils import dotdict, attr_to_header

from PyQt4.QtCore import Qt, QDateTime, QModelIndex, QVariant, QString, \
                        QAbstractTableModel,QAbstractItemModel, QFile, QIODevice

from PyKDE4.kdecore import KStandardDirs


class Loan(dotdict):

    def __init__(self):
        self.ID = None
        self.date = None
        self.item_description = None
        self.item_type = None
        self.person = None
        self.expected_date = None


    def get_time_from_loan(self, aDate = datetime.today() ):
        """return a timedelta between original loan date and a given date""" 
        if self.date is None:
            raise Exception("Loan entered without a date!")
            
        # if loan date is in the future, return None
        if aDate < self.date:
            return None
            
        return aDate - self.date
            
class GSBDatabase(object):
    loans = []
    
    def __init__(self):
        self.dbFile = KStandardDirs.locateLocal("data","getstuffback/db.pickle")
        if exists(self.dbFile):
            tree = etree.parse(self.dbFile)
            for loan in tree.getroot():
                l = Loan()
                for attrNode in loan:
                    if (attrNode.tag in ['date','expected_date']) and (
                                                    attrNode.text is not None):
                        try:
                            dateObj = datetime.strptime(attrNode.text,"%Y-%m-%dT%H:%M:%f")
                            l[attrNode.tag] = dateObj
                        except ValueError:
                            pass # ignore invalid data
                    else:
                        l[attrNode.tag] = attrNode.text
                self.loans.append(l)
                
            # flush memory
            del(tree)
            
    def add_loan(self,loan):
        if loan.ID is None:
            newID = uuid.uuid4().hex
            # a bit inefficient, but should guarantee unique ID
            while newID in [l.ID for l in self.loans]:
                newID = uuid.uuid4().hex
            loan.ID = newID
            
        self.loans.append(loan)
        return loan.ID

    def get_loan(self,loan_ID):
        obj = [loan for loan in self.loans if loan.ID == loan_ID]        
        if len(obj) < 1: 
            return None
        elif len(obj) > 1:
            raise Exception("Duplicate item with ID %s" % loan_ID)
            
        return obj[0]

    def del_loan(self,loan_ID):
        for index,l in enumerate(self.loans):
            if l.ID == loan_ID:
                del(self.loans[index])
                return True
        return False
    
    def get_loan_types(self):
        # there's probably a more efficient way
        types = ['CD','DVD','Book','Tool','Game']
        for loan in self.loans:
            if (loan.item_type not in types) and (loan.item_type is not None):
                types.append(loan.item_type)
        types.sort()
        return types
        
        
    
    def save(self,*args):
        """ save the contents to a file. 
        The XML format is not valid XML (uppercase ID, no declaration etc etc)
        but we don't care for now """
        root = etree.Element("loans")
        tree = etree.ElementTree(root) 
        for loan in self.loans:
            loanNode = etree.SubElement(root,"loan")
            for attr in loan.keys():
                if loan[attr] is not None: # we exclude any empty node
                    attrNode = etree.SubElement(loanNode,attr)
                    if attr in ['date','expected_date']:
                        attrNode.text = loan[attr].isoformat()
                    else:
                        attrNode.text = loan[attr]
        tree.write(self.dbFile)
        # let's flush memory
        del(tree)
        del(root)


class GSBDbModel(QAbstractTableModel,GSBDatabase):
    sections = ['ID','item_description','item_type','person','date','expected_date']
    
    def __init__(self,parent=None):
        super(QAbstractTableModel, self).__init__(parent)
        GSBDatabase.__init__(self)
        self.IDCOL = self.position_for_header('ID')
        self.dataChanged.connect(self.save)
        
    def position_for_header(self,headerName):
        """utility function to determine the index of a named column """
        for index,value in enumerate(self.sections):
            if value == headerName: 
                return index

    #--- begin read-only methods
    def rowCount(self,parent=QModelIndex()):
        return len(self.loans)
        
    def columnCount(self,parent=QModelIndex()):
        return len(self.sections)
    
    def headerData(self,section,orientation,role = Qt.DisplayRole):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return attr_to_header(self.sections[section])
            elif orientation == Qt.Vertical:
                return ""

    def data(self,index,role = Qt.DisplayRole):
        if not index.isValid(): 
            return QVariant()
            
        if role == Qt.DisplayRole:
            # get attribute name for this column
            key = self.sections[index.column()]
            # get the object
            obj = self.loans[index.row()]
            # return attribute value
            result = obj.get(key)
            
            if result is not None:
                if type(result) == datetime:
                    return QDateTime(result)
                return result
            else:
                return QVariant("")
    
    # ----- begin write methods
    
    def setData(self, index, value, role):
        if not index.isValid(): return False
        
        # get attribute name for this column
        attribute = self.sections[index.column()]
        # get the object
        loan = self.loans[index.row()]
        
        # save the change
        if role == Qt.EditRole:
            # remember, value is a QVariant!!
            
            # ok, these lookups should probably be done once, in __init__
            if index.column() in [ 
                self.position_for_header('item_description'),
                self.position_for_header('item_type'),
                self.position_for_header('person') ]:
                    value = unicode(value.toString())
            elif index.column() in [ 
                self.position_for_header('date'),
                self.position_for_header('expected_date') ]:
                    value = value.toDateTime().toPyDateTime()
            elif index.column() == self.IDCOL:
                value = str(value.toString())
                    
            loan[attribute] = value
            self.save() # this might have to go elsewhere
            self.dataChanged.emit(index,index)
            return True
            
        # for everything else, do the generic thing
        return QAbstractTableModel.setData(self,index,value,role)
        
    def flags(self, index):
        # refuse to edit ID and invalid indexes
        if (not index.isValid()) or (index.column() == self.IDCOL):
            return Qt.NoItemFlags
        
        # generic
        return Qt.ItemIsEnabled | Qt.ItemIsSelectable | Qt.ItemIsEditable
        
    def removeRow(self,row,parent=QModelIndex()):
        if row >= self.rowCount() or row < 0: return False
        self.loans.pop(row)
        self.save()
        self.reset()
        return True
        
            
    
    
