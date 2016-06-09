# -*- coding: utf-8 -*-
"""
/***************************************************************************
 InADSGeoCoder
                                 A QGIS plugin
 Geocoder plugin for Estonian InADS geocoding service
                              -------------------
        begin                : 2016-06-07
        git sha              : $Format:%H$
        copyright            : (C) 2016 by sookoll
        email                : mihkel.oviir@gmail.com
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
import resources
# Import the code for the dialog
from inads_geocoder_dialog import InADSGeoCoderDialog
import os.path
import urllib
import json
from qgis.core import *


class InADSGeoCoder:
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
        self.canvas = iface.mapCanvas()
        # store layer id
        self.layerid = ''
        # layer attributes
        self.layer_attributes = [
            'aadresstekst',
            'taisaadress',
            'unik',
            'kort_unik',
            'koodaadress',
            'kort_nr',
            'ehakov',
            'liik',
            'ehak',
            'viitepunkt_x',
            'viitepunkt_y',
            'boundingbox',
            'tunnus',
            'adr_id',
            'tehn_id2',
            'old_aadresstekst',
            'kort_ads_oid',
            'kort_orig_tunnus',
            'pikkaadress',
            'kort_adob_id',
            'ehakmk',
            'adob_id',
            'kort_adr_id',
            'onkort',
            'liikVal',
            'ads_oid'
        ]

        self.query_types = ['EHAK','TANAV','EHITISHOONE','KATASTRIYKSUS']

        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'InADSGeoCoder_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = InADSGeoCoderDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&InADS GeoCoder')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'InADSGeoCoder')
        self.toolbar.setObjectName(u'InADSGeoCoder')

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
        return QCoreApplication.translate('InADSGeoCoder', message)


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

        icon_path = ':/plugins/InADSGeoCoder/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'InADS'),
            callback=self.run,
            parent=self.iface.mainWindow())


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&InADS GeoCoder'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""

        self.dlg.setWindowFlags(Qt.WindowStaysOnTopHint)
        # show the dialog
        self.dlg.show()
        # set results input default value
        self.dlg.results.setValue(10)
        # query types
        for t in self.query_types:
            getattr(self.dlg, t).setChecked(1)

        # register search button clicked
        self.dlg.geocode_button.clicked.connect(self.geocode)

        # Run the dialog event loop
        result = self.dlg.exec_()

        # See if OK was pressed
        if result:
            pass


    def geocode(self):
        """ Send query to InADS service """
        # collect params
        query = unicode(self.dlg.address.text()).encode('utf-8')
        results = self.dlg.results.text()
        # query types
        qtypes = []
        for t in self.query_types:
            if getattr(self.dlg, t).isChecked():
                qtypes.append(t)
        print(qtypes)

        # http://inaadress.maaamet.ee/inaadress/gazetteer?address=kesk&results=10&appartment=1&unik=0&features=EHAK%2CTANAV%2CEHITISHOONE%2CKATASTRIYKSUS
        url = 'http://inaadress.maaamet.ee/inaadress/gazetteer?'

        params = {
            'address': query,
            'results': results,
            'appartment': 1,
            'unik': 0,
            'features': ','.join(qtypes)
        }

        params = urllib.urlencode(params)
        url = "?".join((url, params))

        response = urllib.urlopen(url)
        code = response.getcode()

        if code != 200:
            pass
        else:
            data = json.load(response)

            if 'addresses' in data:
                places = data['addresses']
                if len(places) > 0:
                    self.dlg.address.clear()
                    if not QgsMapLayerRegistry.instance().mapLayer(self.layerid):
                        self.createLayer()
                    for place in places:
                        self.process_point(place)

    def createLayer(self):
        # create layer with same CRS as map canvas
        self.layer = QgsVectorLayer("Point", "InADS addresses", "memory")
        self.provider = self.layer.dataProvider()
        self.layer.setCrs(self.canvas.mapRenderer().destinationCrs())

        # add fields
        for attr in self.layer_attributes:
            self.provider.addAttributes([QgsField(attr, QVariant.String)])

        # BUG: need to explicitly call it, should be automatic!
        self.layer.updateFields()

        # Labels on
        label = self.layer.label()
        label.setLabelField(QgsLabel.Text, 0)
        self.layer.enableLabels(True)

        # add layer if not already
        QgsMapLayerRegistry.instance().addMapLayer(self.layer)

        # store layer id
        self.layerid = self.layer.id()

    def process_point(self, place):
        # create point
        point = QgsPoint(float(place['viitepunkt_x']), float(place['viitepunkt_y']))

        # add a feature
        fields=self.layer.pendingFields()
        f = QgsFeature(fields)
        f.setGeometry(QgsGeometry.fromPoint(point))

        # add fields
        for attr in self.layer_attributes:
            f[attr] = place[attr]

        self.provider.addFeatures([ f ])
        self.canvas.refresh()
