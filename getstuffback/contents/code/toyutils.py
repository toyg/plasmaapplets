# -*- coding: utf-8 -*-
# /
# toyutils.py - part of getstuffback
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

from PyQt4.QtCore import QString, QStringList

class dotdict(dict):
    """ enable access to dictionary keys using dot-notation
    e.g. obj.key rather than obj['key']"""
    
    def __getattr__(self, attr):
        return self.get(attr, None)
    __setattr__= dict.__setitem__
    __delattr__= dict.__delitem__
    
    # following  two needed for pickling
    def __getstate__(self): return self.__dict__
    def __setstate__(self, d): self.__dict__.update(d)
    
def attr_to_header(attrName):
    """ take a string of form word1_word2 etc and return a string suitable for
    display ("Word1 Word2")"""
    
    return " ".join(map(str.capitalize,attrName.split("_")))

def list_to_stringlist(origList):
    sList = QStringList()
    for s in origList: sList.append(QString(s))
    return sList
