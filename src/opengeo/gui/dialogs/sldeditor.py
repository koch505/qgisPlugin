import sys
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.Qsci import QsciScintilla, QsciLexerXML
from PyQt4 import QtGui, QtCore
import xml.dom.minidom


class SldEditorDialog(QtGui.QDialog):
    
    def __init__(self, style, explorer, parent = None):
        super(SldEditorDialog, self).__init__(parent)
        
        self.style = style  
        self.explorer = explorer          
        self.initGui()        
        
    def initGui(self):   
        self.resize(600, 350)    
        self.setWindowFlags(self.windowFlags() | Qt.WindowSystemMenuHint |
                                                Qt.WindowMinMaxButtonsHint)                  
        self.setWindowTitle('Edit SLD style')
        
        layout = QtGui.QVBoxLayout()                                
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Cancel)         
        sld = xml.dom.minidom.parseString(self.style.sld_body)         
        self.editor = SldEditorWidget(sld.toprettyxml())        
        layout.addWidget(self.editor)       
        layout.addWidget(buttonBox)
        self.setLayout(layout)

        buttonBox.accepted.connect(self.okPressed)
        buttonBox.rejected.connect(self.cancelPressed)
        
    def okPressed(self): 
        self.explorer.run(self.style.update_body, "Update SLD body", [], self.editor.text())        
        self.close()
        
    def cancelPressed(self):
        self.close()

        

class SldEditorWidget(QsciScintilla):
    ARROW_MARKER_NUM = 8

    def __init__(self, text, parent=None):
        super(SldEditorWidget, self).__init__(parent)

        font = QFont()
        font.setFamily('Courier')
        font.setFixedPitch(True)
        font.setPointSize(10)
        self.setFont(font)
        self.setMarginsFont(font)

        fontmetrics = QFontMetrics(font)
        self.setMarginsFont(font)
        self.setMarginWidth(0, fontmetrics.width("00000") + 6)
        self.setMarginLineNumbers(0, True)
        self.setMarginsBackgroundColor(QColor("#cccccc"))

        self.setBraceMatching(QsciScintilla.SloppyBraceMatch)

        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#ffe4e4"))

        lexer = QsciLexerXML()
        lexer.setDefaultFont(font)
        self.setLexer(lexer)
        self.SendScintilla(QsciScintilla.SCI_STYLESETFONT, 1, 'Courier')
        
        self.setText(text)




