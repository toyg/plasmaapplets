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
