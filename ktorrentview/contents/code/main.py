# -*- coding: utf-8 -*-

from os.path import expanduser, exists, join
import codecs

from PyQt4.QtCore import Qt, QModelIndex, QObject, QRectF, QString, QVariant, \
                        pyqtSlot, SIGNAL
from PyQt4.QtGui import QColor, QComboBox, QFileDialog, QGraphicsGridLayout, \
                        QHeaderView, QIcon, QItemDelegate, QMessageBox,  \
                        QPixmap, QTreeView
from PyKDE4.kdecore import i18n

from PyKDE4.plasma import Plasma
from PyKDE4 import plasmascript
import dbus

class KTorrentView(plasmascript.Applet):
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
        
        self.setLayout(self.layout)
        self.resize(500,200)
        
    

def CreateApplet(parent):
    return KTorrentView(parent)
