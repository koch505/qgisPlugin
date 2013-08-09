from PyQt4 import QtGui, QtCore

class PublishProjectDialog(QtGui.QDialog):
    
    def __init__(self, catalogs, parent = None):
        super(PublishProjectDialog, self).__init__(parent)
        self.catalogs = catalogs            
        self.catalog = None
        self.workspace = None
        self.text = None
        self.initGui()
        
        
    def initGui(self):                         
        layout = QtGui.QVBoxLayout()                                
        buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Close)        
        self.setWindowTitle('Publish layer')
                 
        
        verticalLayout = QtGui.QVBoxLayout()
        
        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.setSpacing(30)
        horizontalLayout.setMargin(0)        
        catalogLabel = QtGui.QLabel('Catalog')
        self.catalogBox = QtGui.QComboBox()        
        self.catalogBox.addItems(self.catalogs.keys())
        self.catalogBox.currentIndexChanged.connect(self.catalogHasChanged)
        horizontalLayout.addWidget(catalogLabel)
        horizontalLayout.addWidget(self.catalogBox)
        verticalLayout.addLayout(horizontalLayout)
        
        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.setSpacing(30)
        horizontalLayout.setMargin(0)        
        workspaceLabel = QtGui.QLabel('Workspace')
        self.workspaceBox = QtGui.QComboBox()     
        self.workspaces = self.catalogs[self.catalogs.keys()[0]].get_workspaces()
        workspaceNames = [w.name for w in self.workspaces]
        self.workspaceBox.addItems(workspaceNames)
        horizontalLayout.addWidget(workspaceLabel)
        horizontalLayout.addWidget(self.workspaceBox)
        verticalLayout.addLayout(horizontalLayout)
        
        self.destGroupBox = QtGui.QGroupBox()
        self.destGroupBox.setLayout(verticalLayout)
        
        verticalLayout = QtGui.QVBoxLayout()
        
        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.setSpacing(30)
        horizontalLayout.setMargin(0)        
        groupLabel = QtGui.QLabel('Global group name')
        self.groupNameBox = QtGui.QLineEdit()        
        self.groupNameBox.setPlaceholderText("[leave empty if no global group should be created]")
        horizontalLayout.addWidget(groupLabel)
        horizontalLayout.addWidget(self.groupNameBox)
        verticalLayout.addLayout(horizontalLayout)
        
        self.groupGroupBox = QtGui.QGroupBox()
        self.groupGroupBox.setLayout(verticalLayout)
        
        layout.addWidget(self.destGroupBox)
        layout.addWidget(self.groupGroupBox)                      
        layout.addWidget(buttonBox)
        self.setLayout(layout)

        self.connect(buttonBox, QtCore.SIGNAL("accepted()"), self.okPressed)
        self.connect(buttonBox, QtCore.SIGNAL("rejected()"), self.cancelPressed)
        
        self.resize(400,200) 
        
    def catalogHasChanged(self):
        catalog = self.catalogs[self.catalogBox.currentText()]
        self.workspaces = catalog.get_workspaces()
        workspaceNames = [w.name for w in self.workspaces]
        self.workspaceBox.clear()
        self.workspaceBox.addItems(workspaceNames)              
    
    def okPressed(self):                
        self.catalog = self.catalogs[self.catalogBox.currentText()]
        self.workspace = self.workspaces[self.workspaceBox.currentIndex()]
        self.groupName = self.groupNameBox.text()
        if self.groupName.strip() == "":
            self.groupName = None
        self.close()

    def cancelPressed(self):
        self.catalog = None        
        self.workspace = None
        self.text = None
        self.close()          
        
