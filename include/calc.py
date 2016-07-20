# -*- coding: utf-8 -*-
from qgis.core import *
from math import *

 # Rotates a geometry.
# (c) Stefan Ziegler
def rotate(geom,  point,  angle):
    coords = []
    ring = []
    for i in geom.asPolygon():
        for k in i: 
            p1 = QgsPoint(k.x() - point.x(),  k.y() - point.y())
            p2 = rotatePoint(p1,  angle)
            p3 = QgsPoint(point.x() + p2.x(),  point.y() + p2.y())
            ring.append(p3)
        coords.append(ring)
        ring = []
    return QgsGeometry().fromPolygon(coords)
            
# Rotates a single point (centre 0/0).
# (c) Stefan Ziegler
def rotatePoint(point,  angle):
    x = cos(angle)*point.x() - sin(angle)*point.y()
    y = sin(angle)*point.x() + cos(angle)*point.y()
    return QgsPoint(x,  y)
    
def PolarToCartesian(polarcoords):
    '''A tuple, or list, of polar values(distance, theta in radians) are
    converted to cartesian coords'''
    r = polarcoords[0]
    theta = polarcoords[1]
    x = r * cos(theta)
    y = r * sin(theta)
    return [x, y]
    
def AddAndSubtractRadians(theta):
    return (theta + 1.57079632679, theta - 1.57079632679)
    
def CartesianToPolar(xy1, xy2):
    '''Given coordinate pairs as two lists or tuples, return the polar
    coordinates with theta in radians. Values are in true radians along the
    unit-circle, for example, 3.14 and not -0 like a regular python
    return.'''
    try:
        x1, y1, x2, y2 = float(xy1[0]), float(xy1[1]), float(xy2[0]), float(xy2[1])
        xdistance, ydistance = x2 - x1, y2 - y1
        distance = pow(((pow((x2 - x1),2)) + (pow((y2 - y1),2))),.5)
        if xdistance == 0:
            if y2 > y1:
                theta = pi/2
            else:
                theta = (3*pi)/2
        elif ydistance == 0:
            if x2 > x1:
                theta = 0
            else:
                theta = pi
        else:
            theta = atan(ydistance/xdistance)
            if xdistance > 0 and ydistance < 0:
                theta = 2*pi + theta
            if xdistance < 0 and ydistance > 0:
                theta = pi + theta
            if xdistance < 0 and ydistance < 0:
                theta = pi + theta
        return [distance, theta]
    except:
        QMessageBox.information(None, "DEBUG:", "Error in CartesianToPolar()" )