##[Example scripts]=group
##input=vector
##output=output vector

from qgis.core import *
from processing.tools.vector import VectorWriter

vectorLayer = processing.getObject(input)

provider = vectorLayer.dataProvider()

writer = VectorWriter(output, None, provider.fields(),
                      provider.geometryType(), vectorLayer.crs())

features = processing.features(vectorLayer)

writer.addFeature(features.iter.next())

del writer
