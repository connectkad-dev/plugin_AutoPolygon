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
        
        #Initialisation de la largeur
        self.width = 4
        
        #Initialisation de la longueur
        self.heigth = 10
        
        
        #self.mCtrl = None
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
                                       
    
    def SetPositionPoint(self,position = "Center"):
        
        if position.upper() in str(list_position).upper():
            self.position_pnt = position
            return
        else:
            return u'La position : "' + position + '" est inconnu. La liste est des positions de point possibles sont : ' + str(list_position)
           
            
                     
    def canvasPressEvent(self,event):
    
        #Récupération de la couche en cours
        layer = self.canvas.currentLayer()
        #color = QColor(255,0,0)
        self.rb = QgsRubberBand(self.canvas, True)
        #self.rb.setColor(color)
        #self.rb.setWidth(1)
       
        # Récupération du point en cours selon les coordonnées
        point = self.toLayerCoordinates(layer,event.pos())  
        pointMap = self.toMapCoordinates(layer, point)
        self.xc = pointMap.x()
        self.yc = pointMap.y()
        
        currpoint = self.toMapCoordinates(event.pos())
        
        currx = currpoint.x()
        curry = currpoint.y()
        
        #Calcul des Offset
        xOffset = abs( currx - self.xc)
        yOffset = abs( curry - self.yc)
        
        
        #Mise à 0 de la géométrie
        self.rb.reset(True)
        
        #Calcul des 4 points 
        
        #Si la position  du point est Bottom Left (bas gauche)
        if self.position_pnt == "Bottom Left":
            
            pt1 = QgsPoint(xOffset, yOffset)
            pt2 = QgsPoint(xOffset, yOffset+self.width)
            pt3 = QgsPoint(xOffset+self.heigth, yOffset+self.width)
            pt4 = QgsPoint(xOffset+self.heigth, yOffset)
            
        #Si la position  du point est Bottom Right (bas droit)
        elif self.position_pnt == "Bottom Right":
            
            pt1 = QgsPoint(xOffset-self.heigth, yOffset)
            pt2 = QgsPoint(xOffset, yOffset)
            pt3 = QgsPoint(xOffset, yOffset+self.width)
            pt4 = QgsPoint(xOffset-self.heigth, yOffset+self.width)
            
        #Si la position  du point est Top Left (haut gauche)
        elif self.position_pnt == "Top Left":
            
            pt1 = QgsPoint(xOffset, yOffset-self.width)
            pt2 = QgsPoint(xOffset, yOffset)
            pt3 = QgsPoint(xOffset+self.heigth, yOffset)
            pt4 = QgsPoint(xOffset+self.heigth, yOffset-self.width)
            
        #Si la position  du point est Top Right (haut droit)
        elif self.position_pnt == "Top Right":
            
            pt1 = QgsPoint(xOffset-self.heigth, yOffset-self.width)
            pt2 = QgsPoint(xOffset, yOffset-self.width)
            pt3 = QgsPoint(xOffset, yOffset)
            pt4 = QgsPoint(xOffset-self.heigth, yOffset)
            
        else:
            #Sinon crée les points selon le centroide du rectange
            pt1 = QgsPoint(-xOffset-(self.heigth/2), -yOffset-(self.width/2))
            pt2 = QgsPoint(-xOffset-(self.heigth/2), yOffset+(self.width/2))
            pt3 = QgsPoint(xOffset+(self.heigth/2), yOffset+(self.width/2))
            pt4 = QgsPoint(xOffset+(self.heigth/2), -yOffset-(self.width/2))
        
        #Création du polygon selon les points
        points = [pt1, pt2, pt3, pt4]
        polygon = [QgsPoint(i[0]+self.xc,i[1]+self.yc) for i in points]
        
        #Création du polygone
        self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)
         
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
       

        