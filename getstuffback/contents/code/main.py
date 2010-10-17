# -*- coding: utf-8 -*-
# /
# main.py - part of getstuffback
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
from os.path import abspath
from PyQt4 import uic
from PyQt4.QtCore import Qt, QString, QStringList, QModelIndex
from PyQt4.QtGui import QGraphicsGridLayout, QHeaderView, QDialog, QMessageBox
                                                
from PyKDE4.kdeui import KStandardGuiItem
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript

from gsbmodels import GSBDbModel, Loan
from gsbui import AddDlg, LoanDelegate
from toyutils import list_to_stringlist

class GSBApplet(plasmascript.Applet):
    def __init__(self,parent,args=None):
        plasmascript.Applet.__init__(self,parent)
        
        
    def init(self):
        self.setHasConfigurationInterface(False)
        self.setAspectRatioMode(Plasma.IgnoreAspectRatio)
        
        self.settings = self.config()

        self.theme = Plasma.Svg(self)
        self.theme.setImagePath("widgets/background")
        self.setBackgroundHints(Plasma.Applet.DefaultBackground)

        self.layout = QGraphicsGridLayout(self.applet)
        self.layout.setColumnSpacing(0,5.0)
        
        self.lblTitle = Plasma.Label(self.applet)
        self.lblTitle.setText("Stuff to get back")
        self.lblTitle.setAlignment(Qt.AlignHCenter)
        self.lblTitle.setStyleSheet("""QLabel { text-align:center; font-style: italic; font-weight: bold;}""")
        self.layout.addItem(self.lblTitle,0,0,1,3)
        
        self.btnAdd = Plasma.PushButton(self.applet)
        self.btnAdd.nativeWidget().setGuiItem(KStandardGuiItem.Add)
        self.layout.addItem(self.btnAdd,1,0)
            
        self.btnRemove = Plasma.PushButton(self.applet)
        self.btnRemove.nativeWidget().setGuiItem(KStandardGuiItem.Remove)
        self.layout.addItem(self.btnRemove,1,2)

        self.db = GSBDbModel()
        
        self.view = Plasma.TreeView(self.applet)
        self.view.setModel(self.db)
        self.view.nativeWidget().setColumnHidden(self.db.IDCOL,True)
        self.view.nativeWidget().setRootIsDecorated(False)
        self.view.nativeWidget().setExpandsOnDoubleClick(False)
        self.view.nativeWidget().setItemsExpandable(False)
        self.view.setStyleSheet("""
            QTreeView {
                background-color: transparent;
                }
                QTreeView::item { padding-top:10px; padding-bottom: 10px; }
            """)
        self.view.nativeWidget().header().resizeSections(
                                                QHeaderView.ResizeToContents)
        self.view.nativeWidget().setItemDelegate(
                                            LoanDelegate(
                                                    self.view.nativeWidget()))

        
        self.layout.addItem(self.view,2,0,1,3)

        self.setLayout(self.layout)
        #self.resize(350,500)
        
        self.btnAdd.clicked.connect(self.add_loan)
        self.btnRemove.clicked.connect(self.remove_loan)
        
    def add_loan(self,*args):
        addDlg = AddDlg(self)
        result = addDlg.exec_()
        if result == False: return False
        ln = Loan()
        ln.item_description = unicode(addDlg.lineItemDescription.toPlainText())
        ln.person = unicode(addDlg.linePerson.text())
        ln.date = addDlg.dteDate.dateTime().toPyDateTime()
        ln.expected_date = addDlg.dteExpectedDate.dateTime().toPyDateTime()
        ln.item_type = unicode(addDlg.comboItemType.currentText())
        self.db.add_loan(ln)
        self.db.dataChanged.emit(QModelIndex(),QModelIndex())
        self.db.reset()
        
    def remove_loan(self,*args):
        deleteList = self.view.nativeWidget().selectionModel().selectedIndexes()
        rows = set()
        for index in deleteList:
            row = index.row()
            if row not in rows:
                rows.add(row)
                self.db.removeRow(row)


def CreateApplet(parent):
    return GSBApplet(parent)
