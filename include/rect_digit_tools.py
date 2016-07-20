# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from math import *
from calc import *

list_position = ["Center","Bottom Left","Bottom Right","Top Left","Top Right"]
# Tool class
class RectDigitTool(QgsMapTool):
    def __init__(self, canvas):
        QgsMapTool.__init__(self,canvas)
        self.canvas=canvas
        self.snapper = QgsMapCanvasSnapper(self.canvas)
        
        #self.rb=None
        self.xc = None
        self.yc = None
        
        self.position_pnt = "Center"
        
        #Initialisation de la largeur par défaut
        self.width = 2
        
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
        self.snaprb = None        
    
    def SetPositionPoint(self,position = "Center"):
        
        if position.upper() in str(list_position).upper():
            self.position_pnt = position
            return
        else:
            return u'La position : "' + position + '" est inconnu. La liste est des positions de point possibles sont : ' + str(list_position)
                    
    def canvasPressEvent(self,event):
    
        #Récupération de la couche en cours
        layer = self.canvas.currentLayer()
        
        if layer <> None:
            color = QColor(255,0,0,125)
            self.rb = QgsRubberBand(self.canvas, True)
            self.rb.setColor(color)
            self.rb.setWidth(1)
           
            #Récupération du point pour snapper
            x = event.pos().x()
            y = event.pos().y()
            selPoint = QPoint(x,y)
            (retval,result) = self.snapper.snapToBackgroundLayers(selPoint)
            
            #the point we want to have, is either from snapping result
            if result  <> []:
                snappoint = result[0].snappedVertex               
            #or its some point from out in the wild
            else:
                snappoint =  QgsMapToPixel.toMapCoordinates(self.canvas.getCoordinateTransform (), x, y)
            
            # Récupération du point en cours selon les coordonnées
            point = self.toLayerCoordinates(layer,snappoint)  
            pointMap = self.toMapCoordinates(layer, point)
            self.xc = pointMap.x()
            self.yc = pointMap.y()
                                    
            
            self.currx = snappoint.x()
            self.curry = snappoint.y()
            
            #Calcul des Offset
            xOffset = abs( self.currx - self.xc)
            yOffset = abs( self.curry - self.yc)
                    
            #Mise à 0 de la géométrie
            self.rb.reset(True)
            
            
            #Calcul des 4 points 
            
            #Si la position  du point est Bottom Left (bas gauche)
            if self.position_pnt == "Bottom Left":
                
                self.pt1 = QgsPoint(xOffset, yOffset)
                self.pt2 = QgsPoint(xOffset+self.heigth, yOffset)
                self.pt3 = QgsPoint(xOffset+self.heigth, yOffset+self.width)
                self.pt4 = QgsPoint(xOffset, yOffset+self.width)
                            
                pt_oppose = self.pt2
                                                 
            #Si la position  du point est Bottom Right (bas droit)
            elif self.position_pnt == "Bottom Right":
                
                self.pt1 = QgsPoint(xOffset-self.heigth, yOffset)
                self.pt2 = QgsPoint(xOffset, yOffset)
                self.pt3 = QgsPoint(xOffset, yOffset+self.width)
                self.pt4 = QgsPoint(xOffset-self.heigth, yOffset+self.width)
                
                pt_oppose = self.pt1
                
            #Si la position  du point est Top Left (haut gauche)
            elif self.position_pnt == "Top Left":
                
                self.pt1 = QgsPoint(xOffset, yOffset-self.width)
                self.pt2 = QgsPoint(xOffset+self.heigth, yOffset-self.width)
                self.pt3 = QgsPoint(xOffset+self.heigth, yOffset)
                self.pt4 = QgsPoint(xOffset, yOffset)
                
                pt_oppose = self.pt3
                
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
                          
                pt_oppose = None        
            
            # set cursor to these coords
            if pt_oppose <> None:
                global_point = self.canvas.mapToGlobal(self.toCanvasCoordinates( QgsPoint(pt_oppose.x()+self.xc, pt_oppose.y()+self.yc)))
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

        #Récupération du point pour snapper
        x = event.pos().x()
        y = event.pos().y()
        selPoint = QPoint(x,y)
        (retval,result) = self.snapper.snapToBackgroundLayers(selPoint)
        
        #the point we want to have, is either from snapping result
        if result  <> []:
            snappoint = result[0].snappedVertex               
        #or its some point from out in the wild
        else:
            snappoint =  QgsMapToPixel.toMapCoordinates(self.canvas.getCoordinateTransform (), x, y)
    
        if self.snaprb <> None:
            self.snaprb.reset()
            
        color = QColor(255,0,0,125)
        self.snaprb = QgsRubberBand(self.canvas, True)
        self.snaprb.setColor(color)
        self.snaprb.setWidth(1)
        
        self.snaprb.setToGeometry(QgsGeometry.fromPoint(snappoint), None)  
                
        if not self.rb:return

        #Recalcul du rectangle
        
        # Récupération du point en cours selon les coordonnées
        layer = self.canvas.currentLayer()        
        point = self.toLayerCoordinates(layer,event.pos())  
        pointMap = self.toMapCoordinates(layer, point)
        
        #pto = self.rb.asGeometry().boundingBox().center()
            
        #Si on a demandé un  positionnement en bas
        if self.position_pnt == "Bottom Left" or self.position_pnt == "Bottom Right":
        
            pt3 = self.pt3
            pt4 = self.pt4
            
            if self.position_pnt == "Bottom Left":
                pt1 = self.pt1
                pt2 = QgsPoint(pointMap.x()-self.xc,pointMap.y()-self.yc)
                
                #Création d'une ligne
                line = QgsGeometry.fromPolyline([pt1,pt2])
                
                #On met le point en cours à la distance voulue (self.heigth)
                if line.length() > self.heigth:        
                    pt2 = line.interpolate(self.heigth).asPoint()
                else:
                    pt2.setX(pt2.x() +(pt2.x()-pt1.x())/line.length()*(self.heigth-line.length()))
                    pt2.setY(pt2.y() +(pt2.y()-pt1.y())/line.length()*(self.heigth-line.length()))
            else:
                pt1 = QgsPoint(pointMap.x()-self.xc,pointMap.y()-self.yc)
                pt2 = self.pt2
                
                #Création d'une ligne
                line = QgsGeometry.fromPolyline([pt2,pt1])
                
                #On met le point en cours à la distance voulue (self.heigth)
                if line.length() > self.heigth:        
                    pt1 = line.interpolate(self.heigth).asPoint()
                else:
                    pt1.setX(pt1.x() +(pt1.x()-pt2.x())/line.length()*(self.heigth-line.length()))
                    pt1.setY(pt1.y() +(pt1.y()-pt2.y())/line.length()*(self.heigth-line.length()))
                                
            #Mise en place de la perpendiculaire au point voulu à une distance self.width
            
            #use the start point and end point to get a theta
            polarcoor = CartesianToPolar((pt1.x(),pt1.y()), (pt2.x(),pt2.y()))
            
            #Add and subtract the 90 degrees in radians from the line...      
            ends = AddAndSubtractRadians(polarcoor[1])      
            firstend = PolarToCartesian((float(self.width),float(ends[0]))) 
            
            #Calcul des coordonnées à droite de la ligne
            #secondend = PolarToCartesian((float(self.width),float(ends[1])))  
            
            #Calcul des coordonnées à gauche de la ligne
            pt3.setX(pt2.x() + firstend[0])
            pt3.setY(pt2.y() + firstend[1])        
                         
            pt4.setX(pt1.x() + firstend[0])
            pt4.setY(pt1.y() + firstend[1])
        
        #Si on a demandé un  positionnement en haut
        elif self.position_pnt == "Top Left" or self.position_pnt == "Top Right":   
            pt1 = self.pt1
            pt2 = self.pt2
            
            if self.position_pnt == "Top Left":
                pt3 = QgsPoint(pointMap.x()-self.xc,pointMap.y()-self.yc)
                pt4 = self.pt4
                
                #Création d'une ligne
                line = QgsGeometry.fromPolyline([pt4,pt3])
                
                #On met le point en cours à la distance voulue (self.heigth)
                if line.length() > self.heigth:        
                    pt3 = line.interpolate(self.heigth).asPoint()
                else:
                    pt3.setX(pt3.x() +(pt3.x()-pt4.x())/line.length()*(self.heigth-line.length()))
                    pt3.setY(pt3.y() +(pt3.y()-pt4.y())/line.length()*(self.heigth-line.length()))
               
            else:
                pt4 = QgsPoint(pointMap.x()-self.xc,pointMap.y()-self.yc)
                pt3 = self.pt3
                
                #Création d'une ligne
                line = QgsGeometry.fromPolyline([pt3,pt4])
                
                #On met le point en cours à la distance voulue (self.heigth)
                if line.length() > self.heigth:        
                    pt4 = line.interpolate(self.heigth).asPoint()
                else:
                    pt4.setX(pt4.x() +(pt4.x()-pt3.x())/line.length()*(self.heigth-line.length()))
                    pt4.setY(pt4.y() +(pt4.y()-pt3.y())/line.length()*(self.heigth-line.length()))
               
                     
            #Mise en place de la perpendiculaire au point voulu à une distance self.width
        
            #use the start point and end point to get a theta
            polarcoor = CartesianToPolar((pt4.x(),pt4.y()), (pt3.x(),pt3.y()))
            
            #Add and subtract the 90 degrees in radians from the line...      
            ends = AddAndSubtractRadians(polarcoor[1])  
            
            #Calcul des coordonnées à gauche de la ligne   
            #firstend = PolarToCartesian((float(self.width),float(ends[0]))) 
            
            #Calcul des coordonnées à droite de la ligne
            secondend = PolarToCartesian((float(self.width),float(ends[1]))) 
            
            #Calcul des coordonnées à gauche de la ligne
            pt2.setX(pt3.x() + secondend[0])
            pt2.setY(pt3.y() + secondend[1])        
                         
            pt1.setX(pt4.x() + secondend[0])
            pt1.setY(pt4.y() + secondend[1])
            
        else:
        
            # A REVOIR
            center = self.rb.asGeometry().boundingBox().center()            
            angle = center.azimuth(point)
            #self.rb.reset(True)        
            rotgeom = rotate(self.rb.asGeometry(), center, -(angle*pi/180))  
            self.rb.setToGeometry( rotgeom, layer ) 
        
        if self.position_pnt != "Center":
            #Création du polygon selon les points
            points = [pt1, pt2, pt3, pt4]
            polygon = [QgsPoint(i[0]+self.xc,i[1]+self.yc) for i in points]
            
            #Création du polygone
            self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)
                                          
            self.pt1 = pt1
            self.pt2 = pt2
            self.pt3 = pt3        
            self.pt4 = pt4
                            
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
                    
        if self.snaprb <> None:
            self.snaprb.reset(True) 
            self.snaprb=None
            
        #Affichage du polygone
        self.canvas.refresh()
                    
    def showSettingsWarning(self):
        pass
    
    def activate(self):
        self.canvas.setCursor(self.cursor)  
        if self.rb <> None:
            self.rb.reset() 
        if self.snaprb <> None:
            self.snaprb.reset() 

            
        
    def deactivate(self):
        try:
            if self.rb <> None:
                self.rb.reset()
            if self.snaprb <> None:
                self.snaprb.reset() 
        except AttributeError:
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
        