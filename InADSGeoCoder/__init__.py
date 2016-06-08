# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InADSGeoCoder
                                 A QGIS plugin
 Geocoder plugin for Estonian InADS geocoding service
                             -------------------
        begin                : 2016-06-07
        copyright            : (C) 2016 by sookoll
        email                : mihkel.oviir@gmail.com
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load InADSGeoCoder class from file InADSGeoCoder.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .inads_geocoder import InADSGeoCoder
    return InADSGeoCoder(iface)
