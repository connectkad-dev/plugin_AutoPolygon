# -*- coding: utf-8 -*-
"""
/***************************************************************************
 AutoPolygon
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
from PyQt4.QtCore import *
from PyQt4.QtGui import *
# Initialize Qt resources from file resources.py
import resources_rc

# Import the code for the dialog
from Auto_Polygon_dialog import AutoPolygonDialog
from options_dialog import OptionsDialog
import os.path
import ConfigParser

# Import qgis api
from qgis.core import *
from qgis.gui import *

import sys
sys.path.append('/include')

# Import des outils de digitalisation de rectangle
from include.rect_digit_tools import RectDigitTool

class AutoPolygon:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        self.canvas = self.iface.mapCanvas()
        
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'Auto_Polygon_{}.qm'.format(locale))
            
        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        #Configuration 
        self.config = ConfigParser.RawConfigParser()
                
        # Create the dialog (after translation) and keep reference
        self.dlg = AutoPolygonDialog()
        
        self.dlg_options = OptionsDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'Automatic Polygon')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'AutoPolygon')
        self.toolbar.setObjectName(u'AutoPolygon')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('Auto_Polygon', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        # Add actions
        
        #Automatic creation of a polygon with a point
        icon_path = ':/plugins/AutoPolygon/icons/rectangle_point.png'
        self.rectdigitpoint = self.add_action(
            icon_path,
            text=self.tr(u'Automatic creation of a polygon with a point'),
            callback=self.rectcreate_point,
             add_to_menu=True,
             add_to_toolbar=False,
            parent=self.iface.mainWindow())
            
        #Automatic creation of a polygon with a line
        icon_path = ':/plugins/AutoPolygon/icons/rectangle_line.png'
        self.rectdigitline = self.add_action(
            icon_path,
            text=self.tr(u'Automatic creation of a polygon with a line'),
            callback=self.rectcreate_line,
             add_to_menu=True,
             add_to_toolbar=False,
            parent=self.iface.mainWindow())
                
        # Get the tool to digitize a rectangle
        self.rectdigittool = RectDigitTool( self.canvas )
                
        #Configuring the rectangle tool
        self.RectMaj()
        
        #Polygon creation tools
        self.rectdigittools = QToolButton(self.toolbar)
        self.rectdigittools.setPopupMode(QToolButton.MenuButtonPopup)
        
        self.rectdigittools.addActions( [ self.rectdigitpoint, self.rectdigitline ] )
        self.rectdigittools.setDefaultAction(self.rectdigitpoint)        
        self.toolbar.addWidget(self.rectdigittools)  

        #Creating the option button
        icon_path = ':/plugins/AutoPolygon/icons/option.png'
        self.options_conf = self.add_action(
            icon_path,
            text=self.tr(u'Options'),
            callback=self.options,
             add_to_menu=True,
             add_to_toolbar=True,
            parent=self.iface.mainWindow())        
                           
        #Connect to the event change layer
        QObject.connect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer*)"), self.toggle)
        
        # At the end of the feature creation, call the function createFeature
        QObject.connect(self.rectdigittool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        
        # By default, put the enabled button to False
        self.rectdigitpoint.setEnabled(False)
        self.rectdigitline.setEnabled(False)
        
        #If a layer is already selected, you are asked to perform toggle if the user requests editing
        self.toggle()

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Automatic Polygon'),
                action)
            self.iface.removeToolBarIcon(action)
        
        #Disconnecting events
        QObject.disconnect(self.rectdigittool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
        QObject.disconnect(self.iface, SIGNAL("currentLayerChanged(QgsMapLayer*)"), self.toggle)
    

    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            pass
         
    #Function changing a layer
    def toggle(self):
        mc = self.canvas
        layer = mc.currentLayer()
        #Decide whether the plugin button/menu is enabled or disabled
        if layer <> None:
            
            if layer.type() == QgsMapLayer.VectorLayer:
                #If the layer is editable and the geometry is a type polygon
                if (layer.isEditable() and layer.geometryType() == 2):
                                                                       
                    #It makes clickable button
                    self.rectdigitpoint.setEnabled(True)
                    self.rectdigitline.setEnabled(True)

                    #Connect to the event editing stopped
                    QObject.connect(layer,SIGNAL("editingStopped()"),self.toggle)

                    #Disconnect to the event editing started
                    QObject.disconnect(layer,SIGNAL("editingStarted()"),self.toggle) 
                
                else:                                
                    #It makes unclickable button
                    self.rectdigitpoint.setEnabled(False)
                    self.rectdigitline.setEnabled(False)
                    
                    if layer.geometryType() == 2:
                        #Connect to the event editing started
                        QObject.connect(layer,SIGNAL("editingStarted()"),self.toggle)
                    else:
                        #Disconnect to the event editing started
                        QObject.disconnect(layer,SIGNAL("editingStarted()"),self.toggle) 
                    
                    #Disconnect to the event editing stopped
                    QObject.disconnect(layer,SIGNAL("editingStopped()"),self.toggle)
            else:
                #Disconnect to the event editing started
                QObject.disconnect(layer,SIGNAL("editingStarted()"),self.toggle) 
                
                
    def rectcreate_point(self):
        self.canvas.setMapTool(self.rectdigittool)
        self.rectdigittools.setDefaultAction(self.rectdigitpoint)    
        
        result = self.rectdigittool.SetPositionTypeSaisie("Point")
        
        if result is not None :
            self.iface.messageBar().pushMessage(
                        self.tr(u'Warning'),
                        self.tr(result),
                        level=QgsMessageBar.WARNING,
                        duration=3
                    )
                
    def rectcreate_line(self):
        self.canvas.setMapTool(self.rectdigittool)
        self.rectdigittools.setDefaultAction(self.rectdigitline)
        
        result = self.rectdigittool.SetPositionTypeSaisie("Line")
        
        if result is not None :
            self.iface.messageBar().pushMessage(
                        self.tr(u'Warning'),
                        self.tr(result),
                        level=QgsMessageBar.WARNING,
                        duration=3
                    )        

    #Function when create feature
    def createFeature(self, geom):
        settings = QSettings()
        mc = self.canvas
        
        #Get the current layer
        layer = mc.currentLayer()
        if layer <> None:
            renderer = mc.mapRenderer()
            
            #Get the layer SRID
            layerCRSSrsid = layer.crs().srsid()
            projectCRSSrsid = renderer.destinationCrs().srsid()
            
            provider = layer.dataProvider()   
            f = QgsFeature()
                        
            #On the Fly reprojection.
            if layerCRSSrsid != projectCRSSrsid:
                geom.transform(QgsCoordinateTransform(projectCRSSrsid, layerCRSSrsid))
                                        
            f.setGeometry(geom)
            
            # add attribute fields to feature
            fields = layer.pendingFields()

            # vector api change update
            f.initAttributes(fields.count())
            for i in range(fields.count()):
                f.setAttribute(i,provider.defaultValue(i))

            layer.beginEditCommand("Create a feature")       
            layer.addFeature(f)
            layer.endEditCommand()
            
        else:
            QObject.disconnect(self.rectdigittool, SIGNAL("rbFinished(PyQt_PyObject)"), self.createFeature)
         
    # Showing the option dialog box         
    def options(self):
    
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg_options.show()
        # Run the dialog event loop
        result = self.dlg_options.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            
            #Configuring the rectangle tool
            self.RectMaj()
            
            pass
     
    def RectMaj(self):
        #Configuring the rectangle tool
        try: self.config.read( self.plugin_dir+'/AutoPolygon.cfg' )
        except: return
        try: 
            width=self.config.getfloat('RECTANGLE','width')
            height=self.config.getfloat('RECTANGLE','height')
            position=self.config.get('RECTANGLE','position')
        except: 
            #If there were errors, the default values are put
            width=2
            height=1
            position= self.tr(u'Bottom Left').encode('utf-8').strip()
            
        self.rectdigittool.SetWidth (width)
        self.rectdigittool.SetHeight (height)
        result = self.rectdigittool.SetPositionPoint(position)
        
        #If the position doesn't existSi la position n'existe pas
        if result is not None :
            self.iface.messageBar().pushMessage(
                        self.tr(u'Warning'),
                        self.tr(result),
                        level=QgsMessageBar.WARNING,
                        duration=3
                    )
        