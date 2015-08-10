from PyQt4 import QtGui, QtCore
import os
from qgis.gui import *
from qgis.core import *
import tempfile
from opengeo.geoserver import pem
from opengeo.geoserver.pki import PKICatalog
from PyQt4.QtCore import QSettings

class DefineCatalogDialog(QtGui.QDialog):

    def __init__(self, explorer, parent = None, catalog = None, name = None, geonode = None):
        super(DefineCatalogDialog, self).__init__(parent)
        self.explorer = explorer
        self.ok = False
        self.catalog = catalog
        self.name = name
        self.geonode = geonode
        self.initGui()


    def initGui(self):

        if self.name is not None:
            if self.catalog is None:
                settings = QSettings()
                settings.beginGroup("/OpenGeo/GeoServer")
                settings.beginGroup(self.name)
                url = unicode(settings.value("url"))
                username = settings.value("username")
                geonodeUrl = settings.value("geonode")
            elif not isinstance(self.catalog, PKICatalog):
                username = self.catalog.username
                url = self.catalog.service_url
                geonodeUrl = self.geonode.url

        else:
            settings = QSettings()
            username = ""
            geonodeUrl = geonodeUrl = settings.value('/OpenGeo/LastGeoNodeUrl', 'http://localhost:8000/')
            url = settings.value('/OpenGeo/LastCatalogUrl', 'http://localhost:8080/geoserver')

        if url.endswith("/rest"):
            url = url[:-5]

        self.setWindowTitle('Catalog definition')

        verticalLayout = QtGui.QVBoxLayout()

        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.setSpacing(30)
        horizontalLayout.setMargin(0)
        nameLabel = QtGui.QLabel('Catalog name')
        nameLabel.setMinimumWidth(150)
        self.nameBox = QtGui.QLineEdit()
        settings = QtCore.QSettings()
        name = self.name or settings.value('/OpenGeo/LastCatalogName', 'Default GeoServer catalog')
        self.nameBox.setText(name)

        self.nameBox.setMinimumWidth(250)
        horizontalLayout.addWidget(nameLabel)
        horizontalLayout.addWidget(self.nameBox)
        verticalLayout.addLayout(horizontalLayout)

        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.setSpacing(30)
        horizontalLayout.setMargin(0)
        urlLabel = QtGui.QLabel('URL')
        urlLabel.setMinimumWidth(150)
        self.urlBox = QtGui.QLineEdit()
        self.urlBox.setText(url)
        self.urlBox.setMinimumWidth(250)
        horizontalLayout.addWidget(urlLabel)
        horizontalLayout.addWidget(self.urlBox)
        verticalLayout.addLayout(horizontalLayout)

        self.groupBox = QtGui.QGroupBox()
        self.groupBox.setTitle("GeoServer Connection parameters")
        self.groupBox.setLayout(verticalLayout)

        layout = QtGui.QVBoxLayout()
        layout.addWidget(self.groupBox)
        self.spacer = QtGui.QSpacerItem(20,20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        layout.addItem(self.spacer)

        self.tabWidget = QtGui.QTabWidget()

        tabBasicAuth = QtGui.QWidget()
        tabBasicAuthLayout = QtGui.QVBoxLayout(tabBasicAuth)

        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.setSpacing(30)
        horizontalLayout.setMargin(0)
        usernameLabel = QtGui.QLabel('User name')
        usernameLabel.setMinimumWidth(150)
        self.usernameBox = QtGui.QLineEdit()
        self.usernameBox.setText('admin')
        self.usernameBox.setMinimumWidth(250)
        self.usernameBox.setText(username)
        horizontalLayout.addWidget(usernameLabel)
        horizontalLayout.addWidget(self.usernameBox)
        tabBasicAuthLayout.addLayout(horizontalLayout)

        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.setSpacing(30)
        horizontalLayout.setMargin(0)
        passwordLabel = QtGui.QLabel('Password')
        passwordLabel.setMinimumWidth(150)
        self.passwordBox = QtGui.QLineEdit()
        self.passwordBox.setEchoMode(QtGui.QLineEdit.Password)
        self.passwordBox.setMinimumWidth(250)
        horizontalLayout.addWidget(passwordLabel)
        horizontalLayout.addWidget(self.passwordBox)
        tabBasicAuthLayout.addLayout(horizontalLayout)

        self.tabWidget.addTab(tabBasicAuth, "Basic")

        try:
            self.certWidget = QgsAuthConfigSelect()
            self.tabWidget.addTab(self.certWidget, "Configurations")
        except NameError:
            #for QGIS without PKI support
            pass

        verticalLayout3 = QtGui.QVBoxLayout()
        verticalLayout3.addWidget(self.tabWidget)

        self.authBox = QtGui.QGroupBox()
        self.authBox.setTitle("Authentication")
        self.authBox.setLayout(verticalLayout3)

        verticalLayout.addWidget(self.authBox)

        if self.catalog is not None:
            if isinstance(self.catalog, PKICatalog):
                self.tabWidget.setCurrentIndex(1)
                #TODO
            else:
                self.tabWidget.setCurrentIndex(0)
                self.passwordBox.setText(self.catalog.password)
                self.usernameBox.setText(self.catalog.username)

        verticalLayout2 = QtGui.QVBoxLayout()
        horizontalLayout = QtGui.QHBoxLayout()
        horizontalLayout.setSpacing(30)
        horizontalLayout.setMargin(0)
        urlLabel = QtGui.QLabel('URL')
        urlLabel.setMinimumWidth(150)
        self.urlGeonodeBox = QtGui.QLineEdit()
        if isinstance(geonodeUrl, QtCore.QPyNullVariant):
            geonodeUrl = ""
        self.urlGeonodeBox.setText(geonodeUrl)
        self.urlGeonodeBox.setMinimumWidth(250)
        horizontalLayout.addWidget(urlLabel)
        horizontalLayout.addWidget(self.urlGeonodeBox)
        verticalLayout2.addLayout(horizontalLayout)

        self.geonodeBox = QtGui.QGroupBox()
        self.geonodeBox.setTitle("GeoNode Connection parameters (Optional)")
        self.geonodeBox.setLayout(verticalLayout2)

        layout.addWidget(self.geonodeBox)
        self.spacer = QtGui.QSpacerItem(20,20, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
        layout.addItem(self.spacer)

        self.buttonBox = QtGui.QDialogButtonBox(QtGui.QDialogButtonBox.Ok | QtGui.QDialogButtonBox.Close)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

        self.buttonBox.accepted.connect(self.okPressed)
        self.buttonBox.rejected.connect(self.cancelPressed)

        self.resize(400,200)


    def okPressed(self):
        self.url = unicode(self.urlBox.text().strip('/')     + '/rest')
        if not self.url.startswith('http'):
            self.url = 'http://%s' % self.url
        if self.tabWidget.currentIndex() == 0:
            self.username = unicode(self.usernameBox.text())
            self.password = unicode(self.passwordBox.text())
            self.certfile = None
            self.keyfile = None
            self.cafile = None
            self.authid = None
        else:
            self.username = None
            self.password = None
            self.authid = self.certWidget.configId()
            authtype = QgsAuthManager.instance().configProviderType(self.authid);
            if authtype == QgsAuthType.None or authtype == QgsAuthType.Unknown:
                QtGui.QMessageBox.warning(self, "Authentication needed",
                                  "Please specify a valid authentication for connecting to the catalog")
                return
            if authtype == QgsAuthType.Basic:
                configbasic = QgsAuthConfigBasic()
                QgsAuthManager.instance().loadAuthenticationConfig(self.authid, configbasic, True)
                self.password = configbasic.password()
                self.username = configbasic.username()
            elif authtype in pem.nonBasicAuthTypes():
                self.certfile, self.keyfile, self.cafile = pem.getPemPkiPaths(self.authid, authtype)
            else:
                QtGui.QMessageBox.warning(self, "Unsupported authentication",
                                  "The selected authentication type is not supported")
                return

        self.name = unicode(self.nameBox.text())
        name = self.name
        i = 2
        while name in self.explorer.catalogs().keys():
            name = self.name + "_" + str(i)
            i += 1
        self.name = name
        self.geonodeUrl = unicode(self.urlGeonodeBox.text())
        settings = QtCore.QSettings()
        settings.setValue('/OpenGeo/LastCatalogName', self.nameBox.text())
        settings.setValue('/OpenGeo/LastCatalogUrl', self.urlBox.text())
        settings.setValue('/OpenGeo/LastGeoNodeUrl', self.urlGeonodeBox.text())
        saveCatalogs = bool(settings.value("/OpenGeo/Settings/GeoServer/SaveCatalogs", True, bool))
        if saveCatalogs:
            settings.beginGroup("/OpenGeo/GeoServer/" + self.name)
            settings.setValue("url", self.url);
            if self.authid is not None:
                settings.setValue("authid", self.authid)
            else:
                settings.setValue("username", self.username)
            settings.setValue("geonode", self.geonodeUrl)
            settings.endGroup()
        self.ok = True
        self.close()

    def cancelPressed(self):
        self.ok = False
        self.close()
