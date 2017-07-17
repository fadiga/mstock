#!usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad


from PyQt4.QtGui import QVBoxLayout

from configuration import Config
from models import (Store, Product, Reports)

from Common.ui.common import (FWidget, FLabel)
from Common.ui.util import formatted_number, show_date
from Common.ui.table import FTableWidget


class ReportForStoreWidget(FWidget):

    def __init__(self, store="", parent=0, *args, **kwargs):
        super(ReportForStoreWidget, self).__init__(
            parent=parent, *args, **kwargs)
        title = u"<h1> Situation du : <i>{}</i></h1>".format(store)
        self.parentWidget().setWindowTitle(Config.NAME_ORGA + title)
        self.parent = parent
        self.store = store

        self.table_resultat = ReportTableWidget(parent=self)

        self.prod_label = FLabel(title)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.prod_label)
        vbox.addWidget(self.table_resultat)
        self.setLayout(vbox)


class ReportTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):

        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = ["Produit",
                         "Restante(carton)", "Restante (pièce)", "Date"]

        self.parent = parent
        self.store = parent.store

        self.sorter = True
        self.stretch_columns = [0, 1, 2, 3]
        self.align_map = {0: 'l', 1: 'r', 2: 'r'}
        # self.ecart = -5
        self.display_vheaders = False
        self.refresh_()

    def refresh_(self):
        """ """
        self._reset()
        self.set_data_for()
        self.refresh()

        pw = self.width() / 5 - 20
        self.setColumnWidth(0, pw * 2)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)

    def set_data_for(self):

        reports = []
        print(self.store)
        try:
            store = Store.get(name=self.store)
        except Exception as e:
            print(e)
            return

        for prod in Product.select().order_by(Product.name):
            try:
                repts = Reports.select().where(
                    Reports.store == store, Reports.product == prod
                ).order_by(-Reports.date)[0]
                remaining = repts.remaining
                last_op = repts.date
            except Exception as e:
                continue
            dict_store = {}
            dict_store["prod"] = prod.name
            dict_store["last_remaining_box"] = formatted_number(remaining)
            dict_store["last_remaining_p"] = formatted_number(
                remaining * prod.number_parts_box)
            dict_store["last_op"] = last_op
            reports.append(dict_store)

        self.data = [(rep.get('prod'), rep.get('last_remaining_box'),
                      rep.get('last_remaining_p'), show_date(
                          rep.get('last_op'))) for rep in reports]
        self.refresh()
