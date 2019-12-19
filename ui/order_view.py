#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

import json

from PyQt4.QtGui import (QVBoxLayout, QGridLayout, QCheckBox)
from PyQt4.QtCore import Qt, QDate, SIGNAL

from configuration import Config
from Common.ui.util import raise_error, date_to_datetime
from Common.ui.common import (FWidget, FPageTitle, FormLabel, BttExportXLSX,
                              IntLineEdit, ButtonSave, FormatDate, DeletedBtt,
                              QLineEdit)
from Common.ui.table import FTableWidget

from models import Product

from tools.export_xls import write_order_xls
from ui.remove_order_save import RemoveOrderwWidget


class OrderViewWidget(FWidget):

    def __init__(self, parent=0, *args, **kwargs):
        super(OrderViewWidget, self).__init__(parent=parent, *args, **kwargs)

        self.parentWidget().setWindowTitle(
            "{} {}".format(Config.APP_NAME, "COMMANDE"))
        self.parent = parent

        self.title = FPageTitle("<h1> Faire une Commande </h1>")

        vbox = QVBoxLayout()
        self.order_table = OrederTableWidget(parent=self)

        self.export_xls_btt = BttExportXLSX("")
        self.connect(self.export_xls_btt, SIGNAL('clicked()'),
                     self.export_xls_order)

        self.com_date = FormatDate(QDate.currentDate())

        self.restor_order_btt = DeletedBtt(u"vider")
        self.connect(self.restor_order_btt, SIGNAL('clicked()'),
                     self.remove_save)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Rechercher un article")
        self.search_field.setMaximumSize(200,
                                         self.search_field.maximumSize().height())
        self.search_field.textChanged.connect(self.finder)

        # Grid
        gridbox = QGridLayout()
        gridbox.addWidget(self.search_field, 0, 0)
        # gridbox.addWidget(FormLabel(u"Date"), 0, 3)
        gridbox.setColumnStretch(2, 2)
        # gridbox.setColumnStretch(1, 2)
        gridbox.addWidget(self.restor_order_btt, 0, 3)
        gridbox.addWidget(self.com_date, 0, 4)
        gridbox.addWidget(self.export_xls_btt, 0, 5)
        vbox.addWidget(self.title)
        vbox.addLayout(gridbox)
        vbox.addWidget(self.order_table)
        self.setLayout(vbox)

    def finder(self, value):
        self.order_table.refresh_(value)

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

        self.hheaders = [u"CHOIX", u"QUANTITE", u"DESCRIPTION"]

        # self.setEditTriggers(QAbstractItemView.EditTriggers(True))
        self.stretch_columns = [2]
        self.align_map = {0: 'r', 1: 'r', 2: 'l'}
        self.display_vheaders = False
        self.live_refresh = False
        self.display_fixed = True

        self.refresh_()

    def refresh_(self, value=None):
        """ """
        self._reset()
        self.set_data_for(value)
        self.refresh()

    def set_data_for(self, prod_find):
        products = Product.select().order_by(Product.name.asc())
        if prod_find:
            products = products.where(Product.name.contains(prod_find))
        rest = self.restor_pew_order()
        self.data = [(2 if prod.name in rest.keys() else 0,
                      rest[prod.name] if prod.name in rest.keys() else "",
                      prod.name) for prod in products]

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
        data = self.getTableItems()
        # fichier.txt est un fichier déjà créé par toi-même
        obj_file = open('tmp_order.txt', 'w')
        # ecriture des données dans fichier.txt
        obj_file.write(json.dumps(data))
        obj_file.close()  # fermeture du fichier quand plus aucune utilité

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
                # liste_item.append(str(self.item(i, 3).text()))
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
