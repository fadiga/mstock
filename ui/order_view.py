#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

import json

from PyQt4.QtGui import (QVBoxLayout, QGridLayout, QCheckBox)
from PyQt4.QtCore import Qt, QDate, SIGNAL

from configuration import Config
from Common.ui.util import raise_success, raise_error, date_to_datetime
from Common.ui.common import (FWidget, FPageTitle, FormLabel, BttExportXLS,
                              IntLineEdit, Button_save, FormatDate, Deleted_btt)
from Common.ui.table import FTableWidget

from models import Product

from tools.export_xls import write_order_xls
from ui.remove_order_save import RemoveOrderwWidget


class OrderViewWidget(FWidget):

    def __init__(self, parent=0, *args, **kwargs):
        super(OrderViewWidget, self).__init__(parent=parent, *args, **kwargs)

        self.parentWidget().setWindowTitle(Config.NAME_ORGA + u"    COMMANDE")
        self.parent = parent

        self.title = FPageTitle(u"Faire une Commande")

        vbox = QVBoxLayout()
        self.order_table = OrederTableWidget(parent=self)

        self.export_xls_btt = BttExportXLS(u"Exporter")
        self.connect(self.export_xls_btt, SIGNAL('clicked()'),
                     self.export_xls_order)

        self.com_date = FormatDate(QDate.currentDate())

        self.restor_order_btt = Deleted_btt(u"vider")
        self.connect(self.restor_order_btt, SIGNAL('clicked()'),
                     self.remove_save)

        # Grid
        gridbox = QGridLayout()
        gridbox.addWidget(FormLabel(u"Date"), 0, 0)
        gridbox.addWidget(self.com_date, 0, 1)
        gridbox.setColumnStretch(1, 5)
        gridbox.addWidget(self.restor_order_btt, 2, 2)
        # gridbox.addWidget(self.save_order_btt, 2, 3)
        gridbox.addWidget(self.export_xls_btt, 2, 4)
        vbox.addWidget(self.title)
        vbox.addLayout(gridbox)
        vbox.addWidget(self.order_table)
        self.setLayout(vbox)

    def refresh(self):
        self.order_table.refresh()

    def remove_save(self):
        self.open_dialog(RemoveOrderwWidget, modal=True)

    def export_xls_order(self):
        L = self.order_table.getTableItems()
        com_date = date_to_datetime(self.com_date.text())
        write_order_xls("order.xls", [com_date, L])


class OrederTableWidget(FTableWidget):
    """ """

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [u"CHOIX", u"QUANTITE", u"DESCRIPTION", u"ITEM NO"]

        # self.setEditTriggers(QAbstractItemView.EditTriggers(True))
        self.stretch_columns = [2]
        self.align_map = {0: 'r', 1: 'r', 2: 'l'}
        self.display_vheaders = False
        self.live_refresh = False
        self.refresh_()

    def refresh_(self):
        """ """
        self._reset()
        self.set_data_for()
        self.refresh()

    def set_data_for(self, *args):
        rest = self.restor_pew_order()
        self.data = [(2 if prod.name in rest.keys() else 0,
                     rest[prod.name] if prod.name in rest.keys() else "",
                     prod.name, prod.code) for prod in Product.all()]


    def _item_for_data(self, row, column, data, context=None):
        if column == 0:
            # create check box as our editor.
            editor = QCheckBox()
            # editor.itemClicked.connect(self.save_order)
            if data == 2:
                editor.setCheckState(2)
            self.connect(editor, SIGNAL('stateChanged(int)'), self.save_order)
            return editor
        if column == 1:
            line_edit = IntLineEdit(u"%s" % data)
            line_edit.textChanged.connect(self.save_order)
            return line_edit
        return super(OrederTableWidget, self)._item_for_data(row, column,
                                                             data, context)

    def save_order(self):
        data =  self.getTableItems()
        obj_file = open('tmp_order.txt', 'w') #fichier.txt est un fichier déjà créé par toi-même
        obj_file.write(json.dumps(data)) #ecriture des données dans fichier.txt
        obj_file.close()# fermeture du fichier quand plus aucune utilité

    def getTableItems(self):
        n = self.rowCount()
        commad_list = []
        for i in range(n):
            liste_item = []
            item = self.cellWidget(i, 0)
            if not item:
                pass
            elif item.checkState() == Qt.Checked:
                liste_item.append(self.is_int(self.cellWidget(i, 1).text()))
                liste_item.append(str(self.item(i, 2).text()))
                liste_item.append(str(self.item(i, 3).text()))
                commad_list.append(liste_item)
        return commad_list

    def restor_pew_order(self):

        dict = {}
        try:
            file = open('tmp_order.txt', "r")
            my_data = file.readline()
            for elt in json.loads(my_data):
                dict[elt[1]] = elt[0]
        except:
            pass
        return dict

    def is_int(self, value):

        try:
            return int(value.replace(' ', ''))
        except:
            return 1
