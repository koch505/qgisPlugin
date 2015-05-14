import urllib
from qgis.core import *
from geoserver.layer import Layer
from opengeo.postgis.table import Table
from opengeo.geoserver.pki import PKICatalog
from PyQt4 import QtCore

def layerUri(layer):
    resource = layer.resource
    catalog = layer.catalog
    def addAuth(_params):
        if hasattr(catalog, 'authid') and catalog.authid is not None:
            hasauthcfg = False
            try:
                configpki = QgsAuthConfigPkiPaths()
                if not hasattr(configpki, "issuerAsPem"):
                    # issuerAsPem() removed at same time as authcfg introduced
                    #   in core PKI implementation
                    hasauthcfg = True
            except:
                pass
            if hasauthcfg and QGis.QGIS_VERSION_INT >= 20801:
                _params['authcfg'] = catalog.authid
            else:
                _params['authid'] = catalog.authid
        else:
            _params['password'] = catalog.password
            _params['username'] = catalog.username
    if resource.resource_type == 'featureType':
        params = {
            'service': 'WFS',
            'version': '1.0.0',
            'request': 'GetFeature',
            'typename': resource.workspace.name + ":" + layer.name,
            'srsname': resource.projection,
        }
        addAuth(params)
        uri = layer.catalog.gs_base_url + 'wfs?' + urllib.unquote(urllib.urlencode(params))
    elif resource.resource_type == 'coverage':
        params = {
            'identifier': resource.workspace.name + ":" + resource.name,
            'format': 'GeoTIFF',
            'url': layer.catalog.gs_base_url + 'wcs',
            'cache': 'PreferNetwork'
        }
        addAuth(params)
        uri = urllib.unquote(urllib.urlencode(params))
    else:
        params = {
            'layers': resource.workspace.name + ":" + resource.name,
            'format': 'image/png',
            'url': layer.catalog.gs_base_url + 'wms',
            'styles': '',
            'crs': resource.projection
        }
        addAuth(params)
        uri = urllib.unquote(urllib.urlencode(params))

    return uri

def layerMimeUri(element):
    if isinstance(element, Layer):
        layer = element
        uri = layerUri(layer)
        resource = layer.resource
        if resource.resource_type == 'featureType':
            layertype = 'vector'
            provider = 'WFS'
        elif resource.resource_type == 'coverage':
            layertype = 'raster'
            provider = 'wcs'
        else:
            layertype = 'raster'
            provider = 'wms'
        escapedName = resource.title.replace( ":", "\\:" );
        escapedUri = uri.replace( ":", "\\:" );
        mimeUri = ':'.join([layertype, provider, escapedName, escapedUri])
        return mimeUri

def tableUri(table):
        geodb = table.conn.geodb
        uri = QgsDataSourceURI()
        passwd = geodb.passwd if not isinstance(geodb.passwd, QtCore.QPyNullVariant) else ""
        uri.setConnection(geodb.host, str(geodb.port), geodb.dbname, geodb.user, passwd)
        uri.setDataSource(table.schema, table.name, table.geomfield)
        return uri.uri()

def tableMimeUri(table):
    if isinstance(table, Table):
        uri = tableUri(table)
        return ':'.join(["vector", "postgres", table.name, uri])
