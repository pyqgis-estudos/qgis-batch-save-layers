# -*- coding: utf-8 -*-
"""
/***************************************************************************
 BatchSaveLayers
                                 A QGIS plugin
 Save open vector layers to one directory as shapefile
                              -------------------
        begin                : 2016-02-19
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Robert Spiers
        email                : rjspiers1@gmail.com
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
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from PyQt4.QtGui import QAction, QIcon, QFileDialog
from qgis.core import QgsVectorFileWriter
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from batch_save_layers_dialog import BatchSaveLayersDialog
import os.path
import os


class BatchSaveLayers:
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
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'BatchSaveLayers_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = BatchSaveLayersDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&Batch Save Layers')
        # TODO: We are going to let the user set this up in a future iteration
        # self.toolbar = self.iface.addToolBar(u'BatchSaveLayers')
        # self.toolbar.setObjectName(u'BatchSaveLayers')
        
        self.dlg.lineEdit.clear()
        self.dlg.toolButton.clicked.connect(self.select_output_directory)       
        

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
        return QCoreApplication.translate('BatchSaveLayers', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=False,
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

        icon_path = ':/plugins/BatchSaveLayers/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Batch Save Layers'),
            callback=self.run,
            parent=self.iface.mainWindow())

        # add to plugin toolbar
        self.action1 = QAction(
            QIcon(":/plugins/BatchSaveLayers/icon.png"),
            u"Batch Save Layers", self.iface.mainWindow())
        self.iface.addToolBarIcon(self.action1)
        self.action1.triggered.connect(self.run)

    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&Batch Save Layers'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        # del self.toolbar

        # remove from plugin toolbar
        self.iface.removeToolBarIcon(self.action1)

    # Select output file 
    def select_output_directory(self):
        output_dir = QFileDialog.getExistingDirectory(self.dlg, "Select output directory ","")
        self.dlg.lineEdit.setText(output_dir)


    def run(self):
        """Run method that performs all the real work"""

        # Select the layers open in the legendInterface and add them to an array
        layers = self.iface.legendInterface().layers()
        layer_list = []
        # Append only Vector (type == 0) to the layer_list
        for layer in layers:
                if layer.type() == 0:
                    layer_list.append(layer.name())
                else:
                    pass
        # Add layer_list array to listWidget
        self.dlg.listWidget.clear()
        self.dlg.listWidget.addItems(layer_list)
        # qt-designer: could use a selection mode for the layers

        # show the dialog
        self.dlg.show()
        # Run the dialog event loop
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            # pass
            output_dir = self.dlg.lineEdit.text()

            if not os.path.exists(output_dir):
                self.iface.messageBar().pushMessage("No such directory", "Choose an existing directory to save the layers in.", 1, 5)
            if os.path.exists(output_dir):
                self.save_layers()

    def save_layers(self):
        # if checkbox is checked, run the appropriate save function
        if self.dlg.checkBox_shp.isChecked():
            self.save_esri_shapefile()
        else:
            pass
        if self.dlg.checkBox_tab.isChecked():
            self.save_mapinfo_file()
        else:
            pass
        if self.dlg.checkBox_geojson.isChecked():
            self.save_geojson()
        else:
            pass
        if self.dlg.checkBox_kml.isChecked():
            self.save_kml()
        else:
            pass
        if self.dlg.checkBox_pgdump.isChecked():
            self.save_pgdump()
        else:
            pass
        if self.dlg.checkBox_csv.isChecked():
            self.save_csv()
        else:
            pass

    # save CSV
    def save_csv(self):
        layers = self.iface.legendInterface().layers()
        output_dir = self.dlg.lineEdit.text() + "/CSV/"
        # create directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for f in layers:
                if f.type() == 0:
                    writer = QgsVectorFileWriter.writeAsVectorFormat( f, output_dir + f.name() + ".csv", "utf-8", f.crs(), "CSV", layerOptions='GEOMETRY=AS_WKT')
                    if writer == QgsVectorFileWriter.NoError:
                        self.iface.messageBar().pushMessage("Layer Saved", f.name() + ".csv saved to " + output_dir, 0, 2)
                    else:
                        self.iface.messageBar().pushMessage("Error saving layer:", f.name() + ".csv to " + output_dir, 1, 2)
                else:
                    pass

    # save PGDump
    def save_pgdump(self):
        layers = self.iface.legendInterface().layers()
        output_dir = self.dlg.lineEdit.text() + "/PGDump/"
        # create directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for f in layers:
                if f.type() == 0:
                    writer = QgsVectorFileWriter.writeAsVectorFormat( f, output_dir + f.name() + ".sql", "utf-8", f.crs(), "PGDump")
                    if writer == QgsVectorFileWriter.NoError:
                        self.iface.messageBar().pushMessage("Layer Saved", f.name() + ".sql saved to " + output_dir, 0, 2)
                    else:
                        self.iface.messageBar().pushMessage("Error saving layer:", f.name() + ".sql to " + output_dir, 1, 2)
                else:
                    pass

    # save shp
    def save_esri_shapefile(self):
        layers = self.iface.legendInterface().layers()
        output_dir = self.dlg.lineEdit.text() + "/ESRI Shapefile/"
        # create directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for f in layers:
                if f.type() == 0:
                    writer = QgsVectorFileWriter.writeAsVectorFormat( f, output_dir + f.name() + ".shp", "utf-8", f.crs(), "ESRI Shapefile")
                    if writer == QgsVectorFileWriter.NoError:
                        self.iface.messageBar().pushMessage("Layer Saved", f.name() + ".shp saved to " + output_dir, 0, 2)
                    else:
                        self.iface.messageBar().pushMessage("Error saving layer:", f.name() + ".shp to " + output_dir, 1, 2)
                else:
                    pass

    # save MapInfo File
    def save_mapinfo_file(self):
        layers = self.iface.legendInterface().layers()
        output_dir = self.dlg.lineEdit.text() + "/Mapinfo File/"
        # create directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for f in layers:
                if f.type() == 0:
                    writer = QgsVectorFileWriter.writeAsVectorFormat( f, output_dir + f.name() + ".TAB", "utf-8", f.crs(), "MapInfo File")
                    if writer == QgsVectorFileWriter.NoError:
                        self.iface.messageBar().pushMessage("Layer Saved", f.name() + ".TAB saved to " + output_dir, 0, 2)
                    else:
                        self.iface.messageBar().pushMessage("Error saving layer:", f.name() + ".TAB to " + output_dir, 1, 2)
                else:
                    pass

    # save GeoJSON
    def save_geojson(self):
        layers = self.iface.legendInterface().layers()
        output_dir = self.dlg.lineEdit.text() + "/GeoJSON/"
        # create directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for f in layers:
                if f.type() == 0:
                    writer = QgsVectorFileWriter.writeAsVectorFormat( f, output_dir + f.name() + ".geojson", "utf-8", f.crs(), "GeoJSON")
                    if writer == QgsVectorFileWriter.NoError:
                        self.iface.messageBar().pushMessage("Layer Saved", f.name() + ".geojson saved to " + output_dir, 0, 2)
                    else:
                        self.iface.messageBar().pushMessage("Error saving layer:", f.name() + ".geojson to " + output_dir, 1, 2)
                else:
                    pass

    # save KML
    def save_kml(self):
        layers = self.iface.legendInterface().layers()
        output_dir = self.dlg.lineEdit.text() + "/KML/"
        # create directory if it doesn't exist
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        for f in layers:
                if f.type() == 0:
                    writer = QgsVectorFileWriter.writeAsVectorFormat( f, output_dir + f.name() + ".kml", "utf-8", None, "KML")
                    if writer == QgsVectorFileWriter.NoError:
                        self.iface.messageBar().pushMessage("Layer Saved", f.name() + ".kml saved to " + output_dir, 0, 2)
                    else:
                        self.iface.messageBar().pushMessage("Error saving layer:", f.name() + ".kml to " + output_dir, 1, 2)
                else:
                    pass
