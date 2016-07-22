# -*- coding: utf-8 -*-

from PyQt4 import QtGui
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from qgis.core import *
from qgis.gui import *
from math import *
from calc import *

list_position = ["Center","Bottom Left","Bottom Right","Top Left","Top Right"]
list_type_saisie = ["Point","Line"]

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
        
        self.type_saisie = "Point"
        
        #Sert à savoir quand démarrer une ligne
        self.started = False
        self.lastPoint = None
    
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
        self.rbline = None
        self.clickright = False
    
    #Définit le type de position de création de rectangle
    def SetPositionPoint(self,position = "Center"):
        
        if position.upper() in str(list_position).upper():
            self.position_pnt = position
            return
        else:
            return u'La position : "' + position + '" est inconnu. La liste est des positions de point possibles sont : ' + str(list_position)
            
            
    def SetPositionTypeSaisie(self,type_saisie = "Point"):
        
        if type_saisie.upper() in str(list_type_saisie).upper():
            self.type_saisie = type_saisie
            return
        else:
            return u'Le Type de saisie : "' + type_saisie + '" est inconnu. La liste est des types de saisie possibles sont : ' + str(list_type_saisie)
                    
    def canvasPressEvent(self,event):
            
        #Récupération de la couche en cours
        layer = self.canvas.currentLayer()
        self.clickright = False
        if layer <> None:
                      
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
            
            if self.type_saisie == "Point" :
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
                        
                color = QColor(255,0,0,125)
                self.rb = QgsRubberBand(self.canvas, True)
                self.rb.setColor(color)
                self.rb.setWidth(1)
            
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
                    
                    pt_oppose = self.pt4
                    
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
            elif self.type_saisie == "Line":
            
                if event.button()  <> 2:
                    if self.rb <> None:
                        self.rb.reset()
                                   
                    self.rb = QgsRubberBand (self.canvas, QGis.Line)
                    self.rb.setColor(QColor(255,0,0,125))
                    self.rb.setWidth(4)
                else:
                    self.clickright = True
                    if self.rbline <> None:
                        self.rbline.reset()
                
                if self.rb <> None:
                    #bring the rubberband to the cursor i.e. the clicked point
                    self.rb.movePoint(QgsPoint(snappoint))
                    self.rb.addPoint(QgsPoint(snappoint))
                    
                   
                    if self.rb.numberOfVertices() > 2:
                        ptd = self.rb.getPoint(0,0)               
                        ptf = self.rb.getPoint(0,1)
                        
                        #Récupération de la ligne
                        line = QgsGeometry.fromPolyline([ptd,ptf])
                                    
                        #Mise en place des rectangles
                        for i in range(0, int(floor(line.length()/self.heigth))):                              
                            pt1 = line.interpolate(self.heigth*i).asPoint()
                            pt2 = line.interpolate(self.heigth*(i+1)).asPoint()
                            
                            #use the start point and end point to get a theta
                            polarcoor = CartesianToPolar((pt1.x(),pt1.y()), (pt2.x(),pt2.y()))
                            
                            #Add and subtract the 90 degrees in radians from the line...      
                            ends = AddAndSubtractRadians(polarcoor[1])      
                            firstend = PolarToCartesian((float(self.width),float(ends[0])))
                            
                            #Calcul des coordonnées à gauche de la ligne
                            pt3 = QgsPoint(pt2.x() + firstend[0],pt2.y() + firstend[1])   
                            pt4 = QgsPoint(pt1.x() + firstend[0],pt1.y() + firstend[1])      
                                                             
                            #Création du polygon selon les points
                            points = [pt1, pt2, pt3, pt4]
                            polygon = [QgsPoint(i[0],i[1]) for i in points]                        
                            
                            #Création du polygone
                            
                            #layer = self.canvas.currentLayer()    
                            self.rbline.addGeometry(QgsGeometry.fromPolygon([polygon]), None)  
                    
                
    def canvasMoveEvent(self,event):
        
        if self.rbline <> None:
            self.rbline.reset()
                
        color = QColor(255,0,0,125)
        self.rbline = QgsRubberBand(self.canvas, True)
        self.rbline.setColor(color)
        self.rbline.setWidth(1)
            
        if not self.rb or self.type_saisie == "Line":
        
            if event.pos() <> None:
                #Récupération du point pour snapper
                x = event.pos().x()
                y = event.pos().y()
                selPoint = QPoint(x,y)
                (retval,result) = self.snapper.snapToBackgroundLayers(selPoint)
                
                if self.snaprb <> None:
                    self.snaprb.reset()
                    
                snappoint = None
                #the point we want to have, is either from snapping result
                if result  <> []:
                    snappoint = result[0].snappedVertex
                    
                if snappoint <> None:                    
                    if self.snaprb == None:
                        color = QColor(255,0,0,125)
                        self.snaprb = QgsRubberBand(self.canvas, True)
                        self.snaprb.setColor(color)
                        self.snaprb.setWidth(4)	
                        self.snaprb.setIconSize(4)
                    
                    self.snaprb.setToGeometry(QgsGeometry.fromPoint(snappoint), None) 

            if not self.rb :
                return
            
          
        # Si on a demandé de créer un rectanlge via un point        
        if self.type_saisie == "Point":
        
            if self.snaprb <> None:
                self.snaprb.reset()
            
            # Récupération du point en cours selon les coordonnées
            layer = self.canvas.currentLayer()        
            point = self.toLayerCoordinates(layer,event.pos())  
            pointMap = self.toMapCoordinates(layer, point)
                        
            snappoint = None    
            #Si on a demandé un  positionnement en bas
            if self.position_pnt == "Bottom Left" or self.position_pnt == "Bottom Right":
            
                pt3 = self.pt3
                pt4 = self.pt4
                
                if self.position_pnt == "Bottom Left":
                    #Recalcul du point 2 selon un éventuel snap
                    (pt2,pt1,snappoint) = self.CalculSnapPnt(QgsPoint(pointMap.x()-self.xc,pointMap.y()-self.yc),self.pt1)                                            
                else:
                    #Recalcul du point 1 selon un éventuel snap
                    (pt1,pt2,snappoint) = self.CalculSnapPnt(QgsPoint(pointMap.x()-self.xc,pointMap.y()-self.yc),self.pt2)
                
                #Calcul des perpendiculaire gauche
                (pt4,pt3) = self.CalculPerpendicul(pt1,pt2,"Left")                
            
            #Si on a demandé un  positionnement en haut
            elif self.position_pnt == "Top Left" or self.position_pnt == "Top Right":   
                pt1 = self.pt1
                pt2 = self.pt2
                
                if self.position_pnt == "Top Left":                
                   #Recalcul du point 3 selon un éventuel snap
                   (pt3,pt4,snappoint) = self.CalculSnapPnt(QgsPoint(pointMap.x()-self.xc,pointMap.y()-self.yc),self.pt4)                                           
                else:                
                   #Recalcul du point 3 selon un éventuel snap
                   (pt4,pt3,snappoint) = self.CalculSnapPnt(QgsPoint(pointMap.x()-self.xc,pointMap.y()-self.yc),self.pt3)
                                          
                #Calcul des perpendiculaire droite
                (pt1,pt2) = self.CalculPerpendicul(pt4,pt3,"Right")
                
            else:
            
                # A REVOIR + VOIR SNAP CENTRE
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
                
                if self.snaprb <> None:
                    self.snaprb.reset()
                    
                #Mise en place du snap s'il y en a un
                if snappoint <> None:
                    
                    if self.snaprb == None:
                        color = QColor(255,0,0,125)
                        self.snaprb = QgsRubberBand(self.canvas, True)
                        self.snaprb.setColor(color)
                        self.snaprb.setWidth(4)	
                    
                    self.snaprb.setToGeometry(QgsGeometry.fromPoint(snappoint), None)
                    
        elif self.type_saisie == "Line":
                        
            #Récupération du point pour snapper (si le point de snap n'est pas null)            
            if snappoint <> None:
                point = snappoint
            else:   
                point =  QgsMapToPixel.toMapCoordinates(self.canvas.getCoordinateTransform (), x, y)
                
            position = 0 
            
            #Récupération de la ligne
            ptd = self.rb.getPoint(0,0)
            
            #Si ce n'est pas un click droit
            if not self.clickright:                
                self.rb.movePoint(point)
                ptf = QgsPoint(point)
            elif self.rb.numberOfVertices() > 2:                
                ptf = self.rb.getPoint(0,1)
                
                #Détermination de la position du curseur par rapport à la ligne (=0 sur la ligne, >0 au dessus de la ligne, <0 en dessous de la ligne)
                position = (ptf.x() - ptd.x()) * (point.y() - ptd.y()) - (ptf.y() - ptd.y()) * (point.x() - ptd.x())
                
            if ptd <> None and ptf <> None:
                line = QgsGeometry.fromPolyline([ptd,ptf])
                            
                #Mise en place des rectangles
                for i in range(0, int(floor(line.length()/self.heigth))):                              
                    pt1 = line.interpolate(self.heigth*i).asPoint()
                    pt2 = line.interpolate(self.heigth*(i+1)).asPoint()
                    
                    if position <0:
                        #Calcul des perpendiculaire gauche
                        (pt4,pt3) = self.CalculPerpendicul(pt1,pt2,"Left",True)
                    else:
                        #Calcul des perpendiculaire gauche
                        (pt4,pt3) = self.CalculPerpendicul(pt1,pt2,"Left",False) 
                                                                     
                    #Création du polygon selon les points
                    points = [pt1, pt2, pt3, pt4]
                    polygon = [QgsPoint(i[0],i[1]) for i in points]                        
                    
                    #Création du polygone
                    self.rbline.addGeometry(QgsGeometry.fromPolygon([polygon]), None)
            else:
                self.rb.reset()
                                       
    #Au relachement du clic
    def canvasReleaseEvent(self,event):
    
        if self.type_saisie == "Point":
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
            
        elif self.type_saisie == "Line":
            if event.button()  == 2 and self.rb <> None:
                if self.rb.numberOfVertices() > 2:
                
                    #Récupération du point pour snapper
                    x = event.pos().x()
                    y = event.pos().y()
                    point =  QgsMapToPixel.toMapCoordinates(self.canvas.getCoordinateTransform (), x, y)
                    
                    #Récupération de la ligne
                    line = self.rb.asGeometry().asPolyline()
                    ptd = line[0]
                    ptf = line[1]  
                    line = QgsGeometry.fromPolyline([ptd,ptf])
                    
                    #Détermination de la position du curseur par rapport à la ligne (=0 sur la ligne, >0 au dessus de la ligne, <0 en dessous de la ligne)
                    position = (ptf.x() - ptd.x()) * (point.y() - ptd.y()) - (ptf.y() - ptd.y()) * (point.x() - ptd.x())
                    
                    self.rb.reset()
                    #Mise en place des rectangles
                    for i in range(0, int(floor(line.length()/self.heigth))):                              
                        pt1 = line.interpolate(self.heigth*i).asPoint()
                        pt2 = line.interpolate(self.heigth*(i+1)).asPoint()
                        
                        if position <0:
                            #Calcul des perpendiculaire gauche
                            (pt4,pt3) = self.CalculPerpendicul(pt1,pt2,"Left",True)
                        else:
                            #Calcul des perpendiculaire gauche
                            (pt4,pt3) = self.CalculPerpendicul(pt1,pt2,"Left",False) 
                                                         
                        #Création du polygon selon les points
                        points = [pt1, pt2, pt3, pt4]
                        polygon = [QgsPoint(i[0],i[1]) for i in points]                        
                        
                        #Création du polygone dans la couche
                        self.rb.setToGeometry(QgsGeometry.fromPolygon([polygon]), None)                    
                        geom = self.rb.asGeometry()
                        self.emit(SIGNAL("rbFinished(PyQt_PyObject)"), geom)
                        self.rb.reset(True)
                        
                    self.rb=None
                        
                    #Mise à zéro de l'affichage temporaire
                    if self.rbline <> None:
                        self.rbline.reset()
                    self.rbline=None
                    
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
        if self.rbline <> None:
            self.rbline.reset()            
        
    def deactivate(self):
        try:
            if self.rb <> None:
                self.rb.reset()
            if self.snaprb <> None:
                self.snaprb.reset()                 
            if self.rbline <> None:
                self.rbline.reset()
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
        
    def CalculSnapPnt(self,pt_snap,pt_opp):
    
        layer = self.canvas.currentLayer()
        snappoint = None
                     
        #Récupération du point pour snapper
        selPoint=self.toCanvasCoordinates(QgsPoint(pt_snap.x()+self.xc, pt_snap.y()+self.yc))   
        (retval,result) = self.snapper.snapToBackgroundLayers(QPoint(selPoint.x(),selPoint.y()))

        #S'il y a un snap à faire
        if result  <> []:
        
            #Récupération du snap et on snappe le point
            snappoint = result[0].snappedVertex
            selPoint = self.toMapCoordinates(layer, snappoint)
            selPoint = QgsPoint(selPoint.x()-self.xc, selPoint.y()-self.yc)
            pt_snap = selPoint                    
        
        #Création d'une ligne
        line = QgsGeometry.fromPolyline([pt_opp,pt_snap])
        
        #On met le point en cours à la distance voulue (self.heigth)
        if line.length() > self.heigth:        
            pt_snap = line.interpolate(self.heigth).asPoint()
        else:
            pt_snap.setX(pt_snap.x() +(pt_snap.x()-pt_opp.x())/line.length()*(self.heigth-line.length()))
            pt_snap.setY(pt_snap.y() +(pt_snap.y()-pt_opp.y())/line.length()*(self.heigth-line.length()))
            
        return (pt_snap,pt_opp,snappoint)
    
    def CalculPerpendicul(self,pt_deb,pt_fin,type = "Both",reverse = False):
    
        #use the start point and end point to get a theta
        polarcoor = CartesianToPolar((pt_deb.x(),pt_deb.y()), (pt_fin.x(),pt_fin.y()))
        
        #Add and subtract the 90 degrees in radians from the line...      
        ends = AddAndSubtractRadians(polarcoor[1])       
        
        #Calcul des coordonnées à gauche de la ligne
        firstend = PolarToCartesian((float(self.width),float(ends[0])))  
        
        #Calcul des coordonnées à droite de la ligne
        secondend = PolarToCartesian((float(self.width),float(ends[1])))
        
        #Si on a demandé à inversé le resultat
        if reverse:
            firstend[0]=firstend[0]*-1
            firstend[1]=firstend[1]*-1
            secondend[0]=secondend[0]*-1
            secondend[1]=secondend[1]*-1
                        
        #Calcul des coordonnées à gauche de la ligne
        pt_deb_perp_gauche=QgsPoint(pt_deb.x() + firstend[0],pt_deb.y() + firstend[1])
        pt_fin_perp_gauche=QgsPoint(pt_fin.x() + firstend[0],pt_fin.y() + firstend[1])
        
        #Calcul des coordonnées à droite de la ligne
        pt_deb_perp_droit=QgsPoint(pt_deb.x() + secondend[0],pt_deb.y() + secondend[1])
        pt_fin_perp_droit=QgsPoint(pt_fin.x() + secondend[0],pt_fin.y() + secondend[1])
       
        #Si on a demandé de renvoyer les coordonnées à gauche de la ligne
        if type == "Left":
            return(pt_deb_perp_gauche,pt_fin_perp_gauche)            
        #Si on a demandé de renvoyer les coordonnées à droite de la ligne
        elif type == "Right":
            return(pt_deb_perp_droit,pt_fin_perp_droit)
        else:
            #Si on a demandé de renvoyer les coordonnées à gauche et à droite de la ligne
            return(pt_deb_perp_gauche,pt_fin_perp_gauche,pt_deb_perp_droit,pt_fin_perp_droit)
            