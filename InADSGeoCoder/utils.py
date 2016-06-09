# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InADSGeoCoder
                                 A QGIS plugin
 Geocoder plugin for Estonian InADS geocoding service
                              -------------------
        begin                : 2016-06-07
        git sha              : $Format:%H$
        copyright            : (C) 2016 by sookoll
        email                : mihkel.oviir@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

from qgis.core import *
from qgis.gui import *

class ClickTool(QgsMapTool):
    def __init__(self,iface, callback):
        QgsMapTool.__init__(self,iface.mapCanvas())
        self.iface      = iface
        self.callback   = callback
        self.canvas     = iface.mapCanvas()
        return None


    def canvasReleaseEvent(self,e):
        point = self.canvas.getCoordinateTransform().toMapPoint(e.pos().x(),e.pos().y())
        self.callback(point)
        return None


def pointTo3301(point, crs):
    """
    crs is the renderer crs
    """
    t=QgsCoordinateReferenceSystem()
    t.createFromSrid(3301)
    f=crs
    transformer = QgsCoordinateTransform(f,t)
    pt = transformer.transform(point)
    return pt

def pointFrom3301(point, crs):
    f=QgsCoordinateReferenceSystem()
    f.createFromSrid(3301)
    t=crs
    transformer = QgsCoordinateTransform(f,t)
    pt = transformer.transform(point)
    return pt