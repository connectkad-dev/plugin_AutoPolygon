# -*- coding: utf-8 -*-

# List comprehensions in canvasMoveEvent functions are 
# adapted from Benjamin Bohard`s part of rectovaldiams plugin.

from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
import math
#from rectangle import Rectangle
#import calc

list_position = ["Center","Bottom Left","Bottom Right","Top Left","Top Right"]
# Tool class
class RectDigitTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas
        
        #self.rb=None
        self.xc = None
        self.yc = None
        
        self.position_pnt = "Center"
        
        #Initialisation de la largeur par défaut
        self.width = 1
        
        #Initialisation de la longueur par défaut
        self.heigth = 1
                
        #our own fancy cursor
        self.cursor = QCursor(QPixmap(["16 16 3 1",
                                       "      c None",
                                       ".     c #FF0000",
                                       "+     c #17a51a",
                                       "                ",
                                       "       +.+      ",
                                       "      ++.++     ",
                                       "     +.....+    ",
                                       "    +.  .  .+   ",
                                       "   +.   .   .+  ",
                                       "  +.    .    .+ ",
                                       " ++.    .    .++",
                                       " ... ...+... ...",
                                       " ++.    .    .++",
                                       "  +.    .    .+ ",
                                       "   +.   .   .+  ",
                                       "   ++.  .  .+   ",
                                       "    ++.....+    ",
                                       "      ++.++     ",
                                       "       +.+      "]))
                                       
        self.rb = None                                       
    
    def SetPositionPoint(self,position = "Center"):
        
        if position.upper() in str(list_position).upper():
            self.position_pnt = position
            return
        else:
            return u'La position : "' + position + '" est inconnu. La liste est des positions de point possibles sont : ' + str(list_position)
                    
    def canvasPressEvent(self,event):
    
        #Récupération de la couche en cours
        layer = self.canvas.currentLayer()
        color = QColor(255,0,0,125)
        self.rb = QgsRubberBand(self.canvas, True)
        self.rb.setColor(color)
        self.rb.setWidth(1)
       
        # Récupération du point en cours selon les coordonnées
        point = self.toLayerCoordinates(layer,event.pos())  
        pointMap = self.toMapCoordinates(layer, point)
        self.xc = pointMap.x()
        self.yc = pointMap.y()
        
        currpoint = self.toMapCoordinates(event.pos())
        
        self.currx = currpoint.x()
        self.curry = currpoint.y()
        
        #Calcul des Offset
        xOffset = abs( self.currx - self.xc)
        yOffset = abs( self.curry - self.yc)
                
        #Mise à 0 de la géométrie
        self.rb.reset(True)
        
        #Calcul des 4 points 
        
        #Si la position  du point est Bottom Left (bas gauche)
        if self.position_pnt == "Bottom Left":
            
            self.pt1 = QgsPoint(xOffset, yOffset)
            self.pt2 = QgsPoint(xOffset, yOffset+self.width)
            self.pt3 = QgsPoint(xOffset+self.heigth, yOffset+self.width)
            self.pt4 = QgsPoint(xOffset+self.heigth, yOffset)
                        
            self.pt_oppose = self.pt4
                                 
        #Si la position  du point est Bottom Right (bas droit)
        elif self.position_pnt == "Bottom Right":
            
            self.pt1 = QgsPoint(xOffset-self.heigth, yOffset)
            self.pt2 = QgsPoint(xOffset, yOffset)
            self.pt3 = QgsPoint(xOffset, yOffset+self.width)
            self.pt4 = QgsPoint(xOffset-self.heigth, yOffset+self.width)
            
            self.pt_oppose = self.pt1
            
        #Si la position  du point est Top Left (haut gauche)
        elif self.position_pnt == "Top Left":
            
            self.pt1 = QgsPoint(xOffset, yOffset-self.width)
            self.pt2 = QgsPoint(xOffset, yOffset)
            self.pt3 = QgsPoint(xOffset+self.heigth, yOffset)
            self.pt4 = QgsPoint(xOffset+self.heigth, yOffset-self.width)
            
            self.pt_oppose = self.pt3
            
        #Si la position  du point est Top Right (haut droit)
        elif self.position_pnt == "Top Right":
            
            self.pt1 = QgsPoint(xOffset-self.heigth, yOffset-self.width)
            self.pt2 = QgsPoint(xOffset, yOffset-self.width)
            self.pt3 = QgsPoint(xOffset, yOffset)
            self.pt4 = QgsPoint(xOffset-self.heigth, yOffset)
            
            self.pt_oppose = self.pt4
            
        else:
            #Sinon crée les points selon le centroide du rectange
            
            #On regarde si la taille est 1 et l'offset 0 (????)
            if self.heigth == 1 and xOffset == 0:
                xOffset = 0.5

            #On regarde si la largueur est 1 et l'offset 0 (????)
            if self.width == 1 and yOffset == 0:
                yOffset = 0.5
                     
            self.pt1 = QgsPoint(-xOffset-(self.heigth/2), -yOffset-(self.width/2))
            self.pt2 = QgsPoint(-xOffset-(self.heigth/2), yOffset+(self.width/2))
            self.pt3 = QgsPoint(xOffset+(self.heigth/2), yOffset+(self.width/2))
            self.pt4 = QgsPoint(xOffset+(self.heigth/2), -yOffset-(self.width/2))
                      
            self.pt_oppose = None
        
        
        # set cursor to these coords
        if self.pt_oppose <> None:
            global_point = self.canvas.mapToGlobal(self.toCanvasCoordinates( QgsPoint(self.pt_oppose.x()+self.xc, self.pt_oppose.y()+self.yc)))
            cursor = QCursor()
            cursor.setPos(global_point.x(), global_point.y())
                
        #Création du polygon selon les points
        points = [self.pt1, self.pt2, self.pt3, self.pt4]
        polygon = [QgsPoint(i[0]+self.xc,i[1]+self.yc) for i in points]
        
        #Création du polygone
        self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)  
        
        #Affichage du polygone
        self.canvas.refresh()
    
    def canvasMoveEvent(self,event):

        if not self.rb:return

        #Recalcul du rectangle
        currpoint = self.toMapCoordinates(event.pos())
        
        pt1 = self.pt1
        pt2 = self.pt2
        pt3 = self.pt3
        pt4 = self.pt4
        
        if self.currx > currpoint.x():
            pt1 = QgsPoint(pt1.x()*-1, pt1.y())
            pt2 = QgsPoint(pt2.x()*-1, pt2.y())
            
        if self.curry > currpoint.y():
            pt3 = QgsPoint(pt3.x(), pt3.y()*-1)
            pt4 = QgsPoint(pt4.x(), pt4.y()*-1)
        
         #Création du polygon selon les points
        points = [self.pt1, self.pt2, self.pt3, self.pt4]
        polygon = [QgsPoint(i[0]+self.xc,i[1]+self.yc) for i in points]
        
        #Création du polygone
        self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)
        
        #Récupération du centre du rectangle
        pto=self.rb.asGeometry().boundingBox().center()
        
        #Calcul du degres
       
        
        #self.rb.setToGeometry(geom, None)
        
    #Au relachement du clic
    def canvasReleaseEvent(self,event):
    
        #On enlève le rectangle de digitalisation
        if self.rb <> None:
        
            #Si on a bien un polygon, on valide la création
            if self.rb.numberOfVertices() > 2:
                geom = self.rb.asGeometry()
                self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)
                
            self.rb.reset(True)
            self.rb=None
            
            #Affichage du polygone
            self.canvas.refresh()
                    
    def showSettingsWarning(self):
        pass
    
    def activate(self):
        self.canvas.setCursor(self.cursor)
        
    def deactivate(self):
        pass

    def isZoomTool(self):
        return False
  
    def isTransient(self):
        return False
    
    def isEditTool(self):
        return True
                
    def SetWidth(self, width):
        self.width = width
        
    def SetHeigth(self, heigth):
        self.heigth = heigth
        
 #   def Rotate(self):
        #// cx, cy - center of square coordinates
        #// x, y - coordinates of a corner point of the square
        #// theta is the angle of rotation

        #// translate point to origin
        #float tempX = x - cx;
        #float tempY = y - cy;

        #// now apply rotation
        #float rotatedX = tempX*cos(theta) - tempY*sin(theta);
        #float rotatedY = tempX*sin(theta) + tempY*cos(theta);

        #// translate back
        #x = rotatedX + cx;
        #y = rotatedY + cy;

        #Apply this to all 4 corners and you are done!
        
        
        
        
        #def rotatePoint(self, angle, point, origin):
        #    sinT = sin(radians(angle))
        #    cosT = cos(radians(angle))
        #    return (origin[0] + (cosT * (point[0] - origin[0]) - sinT * (point[1] - origin[1])),
        #                  origin[1] + (sinT * (point[0] - origin[0]) + cosT * (point[1] - origin[1])))

        #def rotateRect(self, degrees):
        #    center = (self.collideRect.centerx, self.collideRect.centery)
        #    self.collideRect.topleft = self.rotatePoint(degrees, self.collideRect.topleft, center)
        #    self.collideRect.topright = self.rotatePoint(degrees, self.collideRect.topright, center)
        #    self.collideRect.bottomleft = self.rotatePoint(degrees, self.collideRect.bottomleft, center)
        #    self.collideRect.bottomright = self.rotatePoint(degrees, self.collideRect.bottomright, center)
       
    #def calcAngleExistant(p1, p2):
    #    """
    #    Return the angle of the line represents by two points : p1 and p2

    #    :param p1: The first point
    #    :param p2: The second point
    #    :type p1: QgsPoint
    #    :type p2: QgsPoint
    #    :return: Return the angle (degre)
    #    :rtype: float
    #    """

    #    a = calcPente(p1, p2) # The slope of the segment p1-p2
    #    length_p1p2 = QgsDistanceArea().measureLine(p1, p2) # Hypothenuse
    #    length_adjacent = fabs(p2.y() - p1.y()) # Adjacent
    #    if length_p1p2 == 0: # Normally you can't have a length of 0 but avoid division by zero
    #        angle_CAB = 0
    #    else:
    #        angle_CAB = acos(length_adjacent/length_p1p2) #

        # Correction of angle_CAB
    #    if a<0:
    #        angle_CAB = angle_CAB - pi/2
    #    elif a>0:
    #        angle_CAB = pi/2 - angle_CAB

    #    return angle_CAB
        
    
    #def calcPente(p1, p2):
    #    """
    #    Return the slope of the line represents by two points : p1 and p2

    #    :param p1: The first point
    #    :param p2: The second point
    #    :type p1: QgsPoint
    #    :type p2: QgsPoint
    #    :return: Return the slope (degre)
    #    :rtype: float
    #    """

    #    num = p1.x() - p2.x()
    #    denum = p1.y() - p2.y()

        # Avoid division by zero
    #    if num == 0:
            # Return a negative value if denum > 0
    #        if denum > 0:
    #            return -90
    #        else:
            # else return a positive value
    #            return 90
        # Same as above with denum
    #    elif denum == 0:
    #        if num > 0:
    #            return -90
    #        else:
    #            return 90
    #    else:
    #        return denum/num
