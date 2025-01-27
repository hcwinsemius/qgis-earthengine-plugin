# -*- coding: utf-8 -*-
"""
Main plugin file.
"""
from __future__ import absolute_import

import webbrowser
from builtins import object
import os.path

from qgis.PyQt.QtCore import QSettings, QTranslator, qVersion, QCoreApplication
from qgis.PyQt.QtWidgets import QAction
from qgis.PyQt.QtGui import QIcon
from qgis.core import QgsProject

import ee

import ee_plugin.ee_auth
ee_plugin.ee_auth.init()

# Initialize Qt resources from file resources.py
from ee_plugin.icons import resources


class GoogleEarthEnginePlugin(object):
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
            'GoogleEarthEnginePlugin_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        self.menu_name_plugin = self.tr("Google Earth Engine Plugin")

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
        return QCoreApplication.translate('GoogleEarthEngine', message)

    def initGui(self):
        ### Main dockwidget menu
        # Create action that will start plugin configuration
        icon_path = ':/plugins/ee_plugin/icons/earth_engine.svg'
        self.dockable_action = QAction(QIcon(icon_path), "User Guide", self.iface.mainWindow())
        # connect the action to the run method
        self.dockable_action.triggered.connect(self.run)
        # Add menu item
        self.iface.addPluginToMenu(self.menu_name_plugin, self.dockable_action)

    # --------------------------------------------------------------------------

    def run(self):
        # open user guide in external web browser
        webbrowser.open_new("https://github.com/gee-community/qgis-earthengine-plugin")

    def unload(self):
        # Remove the plugin menu item and icon
        self.iface.removePluginMenu(self.menu_name_plugin, self.dockable_action)

    # --------------------------------------------------------------------------

    def updateLayers(self):
        layers = QgsProject.instance().mapLayers().values()    
        
        for l in filter(lambda layer: layer.customProperty('ee-layer'), layers):
            ee_script = l.customProperty('ee-script')
            image = ee.deserializer.fromJSON(ee_script)
            ee_plugin.utils.update_ee_image_layer(image, l)
