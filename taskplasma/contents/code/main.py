# -*- coding: utf-8 -*-

# /
# main.py - part of TaskPlasma
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

# TODO: remember last-opened file
# FIXME: changing progress value to 100% should cascade the value to children
# FIXME: completed tasks should collapse
# FIXME: changing progress values is still a bit fiddly and sometimes fails
# FIXME: resizing the treeview, the first column should expand rather than last


from os.path import expanduser, exists, join
import codecs

from PyQt4.QtCore import Qt, QModelIndex, QObject, QRectF, QString, QVariant, \
                        pyqtSlot, SIGNAL
from PyQt4.QtGui import QColor, QComboBox, QFileDialog, QGraphicsGridLayout, \
                        QHeaderView, QIcon, QItemDelegate, QMessageBox,  \
                        QPixmap, QTreeView, QToolButton
from PyKDE4.kdecore import i18n
from PyKDE4.kdeui import KStandardGuiItem
from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript

from tc_models import TaskListModel

class TaskCoachApplet(plasmascript.Applet):
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
        
        # using the predefined KGuiItem objects save us a lot of work
        self.btnOpen = Plasma.PushButton(self.applet)
        self.btnOpen.nativeWidget().setGuiItem(KStandardGuiItem.Open)
        
        self.btnReset = Plasma.PushButton(self.applet)
        self.btnReset.nativeWidget().setGuiItem(KStandardGuiItem.Reset)
        
        self.btnSave = Plasma.PushButton(self.applet)
        self.btnSave.nativeWidget().setGuiItem(KStandardGuiItem.Save)

        self.btnSaveAs = Plasma.PushButton(self.applet)
        self.btnSaveAs.nativeWidget().setGuiItem(KStandardGuiItem.SaveAs)


        self.layout.addItem(self.btnOpen,0,0)
        self.layout.addItem(self.btnReset,0,1)
        self.layout.addItem(self.btnSave,2,1)
        self.layout.addItem(self.btnSaveAs,2,0)
        
        self.model = None
        self.filePath = None
  
        self.treeView = Plasma.TreeView(self.applet)
        self.treeView.setVisible(False)
        
        header = self.treeView.nativeWidget().header()
        header.setDefaultAlignment(Qt.AlignCenter)
        
        fontColor = self.theme.theme().color(Plasma.Theme.TextColor)
        
        header.setStyleSheet("""
            QHeaderView {
                color: %s; 
                font: bold italic;
            };
            """ % fontColor.name() )
        self.treeView.setStyleSheet("""
            QTreeView { background-color: transparent; color: %s;}; 
            """ % fontColor.name() )
        
                                                                                 
        self.treeView.setModel(self.model)
        self.layout.addItem(self.treeView,1,0,1,2)

        self.setLayout(self.layout)
        self.resize(350,500)
        
        self.btnOpen.clicked.connect(self.openFile)
        self.btnReset.clicked.connect(self.resetFile)
        self.btnSave.clicked.connect(self.saveFile)
        self.btnSaveAs.clicked.connect(self.saveFileAs)
        
        # FIXME: doesn't work
        QObject.connect(self.treeView.nativeWidget(),
            SIGNAL("dataChanged(QModelIndex,QModelIndex)"),
            self.onDataChanged)
        
        self.treeView.nativeWidget().setItemDelegate(
                                            ProgressDelegate(
                                                self.treeView.nativeWidget()))
        self.treeView.nativeWidget().header().setResizeMode(
                                                        QHeaderView.Interactive)
        self.treeView.nativeWidget().setEditTriggers(QTreeView.AllEditTriggers)	
        
    def _open(self,filePath):
        if not filePath.isEmpty():
            self.model = TaskListModel(str(filePath))
            self.treeView.setModel(self.model)
            self.treeView.nativeWidget().expandAll()
            self.treeView.nativeWidget().header().resizeSection(0,
                                    self.treeView.nativeWidget().width() * 0.8)
            self.treeView.nativeWidget().header().resizeSection(1,
                                    self.treeView.nativeWidget().width() * 0.1)
            self.filePath = filePath
            self.treeView.setVisible(True)
        
        
    @pyqtSlot()
    def openFile(self,*args):
        fPath = QFileDialog.getOpenFileName(None,
            "Select TaskCoach file",
            expanduser("~"),
            "TaskCoach files (*.tsk);;All Files(*.*)")
        self._open(fPath)
        
    @pyqtSlot()        
    def resetFile(self,*args):
        if self.filePath is not None:
            self.model = TaskListModel(str(self.filePath))
            self.treeView.setModel(self.model)
            self.treeView.nativeWidget().expandAll()
            
    @pyqtSlot()        
    def saveFileAs(self,*args):
        savePath = QFileDialog.getSaveFileName ( None,
                "Save As",
                self.filePath,
                "TaskCoach files (*.tsk);;All Files(*.*)")
        if savePath.isEmpty(): return # user cancelled action
        tmpPath = QString(self.filePath)
        self.filePath = savePath
        done = self.saveFile()
        # if anything went wrong, go back to original
        if not done: self.filePath = tmpPath

    @pyqtSlot()
    def saveFile(self,*args):
        try:
            f = codecs.open(str(self.filePath),"w","utf-8")
            f.write(self.model.domDocument.toString())
            f.close()
            return True
        except Exception, e:
            QMessageBox.critical(None, "Failure while saving", e.msg)
            return False
        except Error, e:
            QMessageBox.critical(None, "Failure while saving", e.msg)
            return False

    
    # FIXME: doesn't work
    @pyqtSlot("QModelIndex","QModelIndex")
    def onDataChanged(self,topLeftIndex,bottomRightIndex):
        if self.model.data(topLeftIndex,Qt.CheckStateRole) == Qt.Checked:
            self.treeView.collapse(topLeftIndex)


class ProgressDelegate(QItemDelegate):
    """Custom delegate class to override a few things """
    def __init__(self,parent=None):
        super(ProgressDelegate,self).__init__(parent)
        
        
    def _getColorForProgress(self,progress):
        """calculate which color to use to represent a given progress"""
        red = QColor(Qt.red)
        hue, sat, val, alpha = red.getHsv()
        # progress : 100 = x : 120
        color = QColor.fromHsv(hue + int(progress * 6 / 5), sat, val)
        return color
            
        
    def paint(self, painter, option, index):
        """custom painter for progress state """
        if index.column() == 1:
            # get value
            progress = index.model().data(index,Qt.DisplayRole)
            
            # calculate where to put the painted rect
            fullRect = option.rect
            center = fullRect.center()
            newRect = QRectF()
            newRect.setTop(     center.y() - 5  )
            newRect.setBottom(  center.y() + 5  )
            newRect.setLeft(    center.x() - 10 )
            newRect.setRight(   center.x() + 10 )
            
            color = self._getColorForProgress(progress)
            # paint
            painter.save()
            painter.fillRect(newRect, color)
            painter.translate(option.rect.x(), option.rect.y()+5)
            painter.restore()
        else:
            QItemDelegate.paint(self,painter,option,index)
            
    def createEditor(self,parent,option,index):
        """create widgets to edit values"""
        if index.column() == 1:
            cbox = QComboBox(parent)
            cbox.setMaxVisibleItems(10)            
            self.updateEditorGeometry(cbox, option,index )
            for pos,value in enumerate([0,20,30,40,50,60,70,80,90,100]):
                icon = QPixmap(20,10)
                icon.fill(self._getColorForProgress(value))
                cbox.insertItem(pos, QIcon(icon),"",value)
            cbox.showPopup()
            return cbox
        else:
            return QItemDelegate.createEditor(self,parent,option,index)
    
    
    
    def setEditorData(self,editor,index):
        """Set initial data for the editor"""
        if index.column() == 0:
            current = index.model().data(index,Qt.DisplayRole)
            editor.setText(current)
        elif index.column() == 1:
            current = index.model().data(index,Qt.DisplayRole)
            editor.setCurrentIndex(editor.findData(current))
        else:
            QItemDelegate.setEditorData(self,editor,index)
    
    def setModelData(self,editor,model,index):
        """Save value changes"""
        if index.column() == 1:
            value, ok = editor.itemData(editor.currentIndex()).toInt()
            model.setData(index,QVariant(value),Qt.EditRole)
        else:
            QItemDelegate.setModelData(self,editor,model,index)
            
    

def CreateApplet(parent):
    return TaskCoachApplet(parent)
