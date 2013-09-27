# -*- coding: utf-8 -*-


'''
This module provides methods to export layers so they can be used as valid data 
for uploading to GeoServer.
'''

from qgis.core import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from opengeo.qgis import utils
import os
    
def exportVectorLayer(layer):
    '''accepts a QgsVectorLayer or a string with a filepath'''
    settings = QSettings()
    systemEncoding = settings.value( "/UI/encoding", "System" )
    if isinstance(layer, QgsMapLayer):
        filename = unicode(layer.source())  
        destFilename = unicode(layer.name()) 
    else:
        filename = unicode(layer)        
        destFilename = unicode(os.path.splitext(os.path.basename(filename))[0])
    if (not filename.lower().endswith("shp")): 
        if not isinstance(layer, QgsMapLayer):
            layer = QgsVectorLayer(filename, "layer", "ogr")                                                
            if not layer.isValid() or layer.type() != QgsMapLayer.VectorLayer:
                raise Exception ("Error reading file {} or it is not a valid vector layer file".format(filename))
        output = utils.tempFilenameInTempFolder(destFilename + ".shp")
        provider = layer.dataProvider()
        writer = QgsVectorFileWriter(output, systemEncoding, layer.pendingFields(), provider.geometryType(), layer.crs() )
        for feat in layer.getFeatures():
            writer.addFeature(feat)
        del writer
        return output
    else:
        return filename



def exportRasterLayer(layer): 
    if (not unicode(layer.source()).lower().endswith("tif") ):        
        filename = str(layer.name())
        output = utils.tempFilenameInTempFolder(filename + ".tif")
        writer = QgsRasterFileWriter(output)    
        writer.setOutputFormat("GTiff");
        writer.writeRaster(layer.pipe(), layer.width(), layer.height(), layer.extent(), layer.crs())
        del writer
        return output
    else:
        return unicode(layer.source())






