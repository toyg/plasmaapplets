# -*- coding: utf-8 -*-
# /
# gsbui.py - part of getstuffback
# Copyright (c) 2010 Giacomo Lacava - g.lacava@gmail.com
#
# Licensed under the European Union Public License, Version 1.1.
# You may not use this work except in compliance with the Licence.
# You may obtain a copy of the Licence at http://ec.europa.eu/idabc/eupl5
# Unless required by applicable law or agreed to in writing,software distributed 
# under the Licence is distributed on an "AS IS" basis, WITHOUT WARRANTIES OR 
# CONDITIONS OF ANY KIND, either express or implied.
# See the Licence for specific language governing permissions and limitations 
# under the Licence.
# /

from datetime import datetime
from PyQt4.QtCore import Qt, QVariant, QDateTime, QString
from PyQt4.QtGui import QDialog, QMessageBox, QColor, QDateTimeEdit, \
                        QStyledItemDelegate, QWidget
from PyQt4 import uic
from PyKDE4.kdecore import ki18n
from PyKDE4.kdeui import KColorButton, KDatePicker
from toyutils import list_to_stringlist

class AddDlg(QDialog):
    
    def __init__(self, applet):
        super(QDialog,self).__init__()
        path = applet.package().path() + "ui/loan_add.ui"
        addDlg, baseClass = uic.loadUiType(path)
        self.realDlg = addDlg()
        self.realDlg.setupUi(self)
        
        # convenience access to widget we care about
        for obj in ['lineItemDescription','linePerson', 'dteDate',
                                            'dteExpectedDate', 'comboItemType']:
            self.__dict__[obj] = self.realDlg.__dict__[obj]
        
        # init combobox
        self.comboItemType.insertItems(0,
                                list_to_stringlist(applet.db.get_loan_types()))
        self.comboItemType.clearEditText()
        
        # init dates
        today = datetime.today()
        self.dteDate.setDateTime(today)
        self.dteExpectedDate.setDateTime(today)
        
        # signals                   
        self.realDlg.buttonBox.accepted.connect(self.add)
        self.show()
                
    def add(self,button=None):
        if self.realDlg.lineItemDescription.toPlainText().isEmpty():
            QMessageBox.critical(self, ki18n("Missing description").toString(), 
                ki18n("""Please enter a short description for the item, 
                e.g. 'X-Files boxset'""").toString())
            return False
        elif self.realDlg.linePerson.text().isEmpty():
            QMessageBox.critical(self, ki18n("Missing person name").toString(), 
                ki18n("""Please enter the name of the person. How can you get your
                stuff back if you don't know who has it? ;-) """).toString())
            return False
        
        date = self.realDlg.dteDate.dateTime().toPyDateTime()
        dateExpected = self.realDlg.dteExpectedDate.dateTime().toPyDateTime()
        if dateExpected < date:
            QMessageBox.critical(self, ki18n("Wrong expected date").toString(), 
                ki18n("""You expect to get stuff back before the loan even happens.
                Please check your "Expected on" date.""").toString())
            return False
        
        self.accept()

class LoanDelegate(QStyledItemDelegate):
    """Custom delegate class to override a few things """
    def __init__(self,applet,parent=None):
        super(LoanDelegate,self).__init__(parent)
        self.applet = applet
        self.options = applet.config().group("general")
               
    def paint(self, painter, option, index):
        self.initStyleOption( option, index) # required 
        overdueColour = QColor(
                            self.options.readEntry("overdue_colour","#ff6666"))
        grace_period = int(self.options.readEntry("grace","5").toString())
        if index.isValid():
            
            # -- begin overriding color depending on date
            model = index.model()
            colDate = model.position_for_header('date')
            colExpDate = model.position_for_header('expected_date')
            
            model = index.model()
            column = index.column()
            today = datetime.today()
            
            dateExpIndex = model.index(index.row(),colExpDate)
            dateQv = model.data(dateExpIndex,Qt.DisplayRole)
                
            if dateQv.toString() == "":
                dateIndex = model.index(index.row(),colDate)
                dateQv = model.data(dateIndex,Qt.DisplayRole)                    

            if type(dateQv) == type(QVariant()):
                date = dateQv.toDateTime().toPyDateTime()
            elif type(dateQv) == type(QDateTime()):
                date = dateQv.toPyDateTime()
                        
            if (today - date).days > grace_period:
                
                
                painter.save()
                painter.fillRect(option.rect, overdueColour)
                painter.translate(option.rect.x(), option.rect.y())
                painter.restore()
            # -- end overriding color depending on date
            
            
        QStyledItemDelegate.paint(self,painter,option,index)
            
            
    def createEditor(self,parent,option,index):
        """create widgets to edit values"""
        if index.isValid():
            model = index.model()
            column = index.column()
            if (column == model.position_for_header('date')) or \
               (column == model.position_for_header('expected_date')) :
                    data = model.data(index,Qt.DisplayRole)
                    if data.toString() == "":
                        data = datetime.today()
                    editor = QDateTimeEdit(data)
                    editor.setCalendarPopup(True)
                    self.updateEditorGeometry(editor, option,index )
                    # by default it's a bit too small
                    editor.setFixedWidth(option.rect.width() + 50)
                    # FIXME: resulting position is still wrong
                    return editor
                    
        return QStyledItemDelegate.createEditor(self,parent,option,index)
    


class ConfigDlg(QWidget):
    def __init__(self,parent, applet):
        super(ConfigDlg,self).__init__(parent)
        path = applet.package().path() + "configui/config.ui"
        confDlg, baseClass = uic.loadUiType(path)
        self.realDlg = confDlg()
        self.realDlg.setupUi(self)
        
        self.options = applet.config().group("general")
        overdueColour = QColor(
                            self.options.readEntry("overdue_colour","#ff6666"))
        grace_period = int(self.options.readEntry("grace","5").toString())

        self.btnColour = KColorButton(overdueColour, self)
        self.realDlg.formLayout.addRow(ki18n("Overdue Colour").toString(),self.btnColour)
        
        self.spinGrace = self.realDlg.spinGrace
        self.spinGrace.setValue(grace_period)

