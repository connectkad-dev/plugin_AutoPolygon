# -*- coding: utf-8 -*-
"""
/***************************************************************************
 OptionsDialog
                                 A QGIS plugin
 Ce plugin permet de créer des polygones automatiques selon une longueur et largeur prédéfinies
                             -------------------
        begin                : 2016-07-06
        git sha              : $Format:%H$
        copyright            : (C) 2016 by G. Lavocat/Rennes Métropole
        email                : g.lavocat@rennesmetropole.fr
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

import os

from PyQt4 import QtCore, QtGui, uic
from PyQt4.QtCore import *
from PyQt4.QtGui import *

import ConfigParser

FORM_CLASS, _ = uic.loadUiType(os.path.join(
    os.path.dirname(__file__), 'dialog/ui_options.ui'))


class OptionsDialog(QtGui.QDialog, FORM_CLASS):
    def __init__(self, parent=None):
        """Constructor."""
        super(OptionsDialog, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
                
        self.config = ConfigParser.RawConfigParser()
        
        #Configuration de l'outil de rectangle
        try: self.config.read( os.path.join(
            os.path.dirname(__file__), 'AutoPolygon.cfg') )
        except: return
        try: 
            width=self.config.getfloat('RECTANGLE','width')
            height=self.config.getfloat('RECTANGLE','height')
            position=self.config.get('RECTANGLE','position')
        except: 
            #S'il n'y eu des erreurs, on met les valeurs par défaut
            width=2
            height=1
            position="Bottom Left"
            
        self.dsb_width.setValue(width)
        self.dsb_height.setValue(height)
        self.cb_position.setCurrentIndex(self.cb_position.findText(position))
        
        self.accepted.connect(self.accept)
       
    def accept(self):
        
        #Enregistrement de la config
        
        self.config.set('RECTANGLE','width',self.dsb_width.value())
        self.config.set('RECTANGLE','height', self.dsb_height.value())
        self.config.set('RECTANGLE','position', self.cb_position.currentText().encode('utf-8').strip())
        
        with open(os.path.join(os.path.dirname(__file__), 'AutoPolygon.cfg'), 'wb') as configfile:
            self.config.write(configfile)
            
        #Fermeture de la fenêtre avec acceptation
        super(OptionsDialog, self).accept()