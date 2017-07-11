#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from datetime import datetime

from PyQt4.QtGui import (QVBoxLayout, QTableWidgetItem)
from PyQt4.QtCore import Qt

import peewee
from configuration import Config
from Common.ui.common import FWidget, FPeriodHolder, FPageTitle
from Common.ui.table import FTableWidget
from models import Reports, Product
from Common.ui.util import formatted_number, is_int


class By_productViewWidget(FWidget, FPeriodHolder):

    def __init__(self, product, parent=0, *args, **kwargs):

        super(By_productViewWidget, self).__init__(
            parent=parent, *args, **kwargs)
        FPeriodHolder.__init__(self, *args, **kwargs)

        self.parentWidget().setWindowTitle(Config.NAME_ORGA + u"      Par product")

        product = Product.select().where(Product.name.contains(product)).get()

        self.title = FPageTitle(
            u"Rapports du product: {name}".format(name=product.name))
        self.table = By_productTableWidget(product, parent=self,
                                           main_date=self.main_date)

        vbox = QVBoxLayout()
        vbox.addWidget(self.title)
        vbox.addWidget(self.periods_bar)
        vbox.addWidget(self.table)

        self.setLayout(vbox)

    def refresh(self):
        self.table.refresh()

    def change_period(self, main_date):
        self.table.refresh_period(main_date)


class By_productTableWidget(FTableWidget):

    def __init__(self, product, parent, main_date, *args, **kwargs):

        self.parent = parent
        self.product = product
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = [u"Magain", u"Entrée", u"sortie", u"Restante"]
        self.prod = product
        self.set_data_for(main_date)
        self.stretch_columns = [0]
        self.align_map = {0: 'l', 1: 'r', 2: 'r', 3: 'r'}
        self.ecart = -5
        self.display_vheaders = False
        self.refresh()

    def refresh_period(self, main_date):
        self._reset()
        self.set_data_for(main_date)
        self.refresh()

    def set_data_for(self, main_date):

        try:
            on, end = main_date.current.current[
                0], main_date.current.current[1]
        except:
            on, end = main_date.current[0], main_date.current[1]

        on = datetime(on.year, on.month, on.day, 0, 0, 0)
        end = datetime(end.year, end.month, end.day, 23, 59, 59)
        reports = []
        period_report = Reports.select().filter(product=self.product,
                                                date__gte=on, date__lte=end)

        for rept in period_report.group_by("store").order_by(Reports.date.desc()):
            dict = {}
            reports_stores = period_report.filter(store=rept.store)
            sum_qty_in = reports_stores.filter(
                type_=Reports.E).aggregate(peewee.Sum('qty_use'))
            sum_qty_out = reports_stores.filter(
                type_=Reports.S).aggregate(peewee.Sum('qty_use'))

            dict["store"] = rept.store.name
            dict["sum_qty_in"] = sum_qty_in if sum_qty_in else 0
            dict["sum_qty_out"] = sum_qty_out if sum_qty_out else 0
            dict["sum_nbr_part_in"] = rept.product.number_parts_box * \
                dict["sum_qty_in"]
            dict["sum_nbr_part_out"] = rept.product.number_parts_box * \
                dict["sum_qty_out"]
            try:
                dict["remaining"] = reports_stores.order_by(
                    ('.date', 'desc')).get().remaining
                reports.append(dict)
            except:
                raise
                # pass
        self.data = [(rep.get('store'), rep.get('sum_qty_in'), rep.get('sum_qty_out'),
                      rep.get('remaining'))
                     for rep in reports]

    def extend_rows(self):

        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 1)
        # self.setSpan(nb_rows, 0, 1, 1)
        mtt_ttc = QTableWidgetItem(u"TOTAUX: ")
        mtt_ttc.setTextAlignment(Qt.AlignRight)
        self.setItem(nb_rows, 0, mtt_ttc)

        ttl_remainig = 0
        tall_in = 0
        tall_out = 0

        for row_num in xrange(0, self.data.__len__()):
            all_in = is_int(unicode(self.item(row_num, 1).text()))
            tall_in += all_in
            all_out = is_int(unicode(self.item(row_num, 2).text()))
            tall_out += all_out
            remaining = is_int(unicode(self.item(row_num, 3).text()))
            ttl_remainig += remaining

        # Montant TTC
        tall_in = QTableWidgetItem(formatted_number(tall_in))
        tall_in.setTextAlignment(Qt.AlignRight)
        self.setItem(row_num + 1, 1, tall_in)
        tall_out = QTableWidgetItem(formatted_number(tall_out))
        tall_out.setTextAlignment(Qt.AlignRight)
        self.setItem(row_num + 1, 2, tall_out)

        ttl_remainig = QTableWidgetItem(formatted_number(ttl_remainig))
        ttl_remainig.setTextAlignment(Qt.AlignRight)
        self.setItem(row_num + 1, 3, ttl_remainig)

    def click_item(self, row, column, *args):
        store_column = 0
        if column == store_column:
            from by_store import By_storeViewWidget
            self.parent.change_main_context(By_storeViewWidget,
                                            store=self.data[row][store_column])
        else:
            return
