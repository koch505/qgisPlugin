from qgis.core import *
from opengeo import config
import opengeo.config

ALL_TYPES = -1

class WrongLayerNameException(BaseException) :
    pass

def resolve_layer(name):
    layers = get_all_layers()    
    for layer in layers:
        if layer.name() == name:
            return layer
    raise WrongLayerNameException()       

def get_raster_layers():    
    layers = config.iface.legendInterface().layers()
    raster = list()

    for layer in layers:
        if layer.type() == layer.RasterLayer:
            if layer.providerType() == 'gdal':#only gdal file-based layers
                raster.append(layer)
    return raster


def get_vector_layers(shapetype=-1):
    layers = config.iface.legendInterface().layers()
    vector = list()
    for layer in layers:
        if layer.type() == layer.VectorLayer:
            if shapetype == ALL_TYPES or layer.geometryType() == shapetype:
                uri = unicode(layer.source())
                if not uri.lower().endswith("csv") and not uri.lower().endswith("dbf"):
                    vector.append(layer)
    return vector

def get_all_layers():
    layers = []
    layers += get_raster_layers();
    layers += get_vector_layers();
    return layers


def get_groups():
    groups = {}    
    rels = opengeo.config.iface.legendInterface().groupLayerRelationship()
    for rel in rels:
        groupName = rel[0] 
        if groupName != '':
            groupLayers = rel[1]            
            groups[groupName] = [QgsMapLayerRegistry.instance().mapLayer(layerid) for layerid in groupLayers]
    return groups


