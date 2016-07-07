# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AutoPolygon
                                 A QGIS plugin
 Ce plugin permet de créer des polygones automatiques selon une longueur et largeur prédéfinies
                             -------------------
        begin                : 2016-07-06
        copyright            : (C) 2016 by G. Lavocat/Rennes Métropole
        email                : g.lavocat@rennesmetropole.fr
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
    """Load AutoPolygon class from file AutoPolygon.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .Auto_Polygon import AutoPolygon
    return AutoPolygon(iface)
