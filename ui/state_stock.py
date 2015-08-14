#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad
from Common import peewee
from datetime import datetime
from PyQt4 import QtGui, QtCore

from configuration import Config
from Common.ui.common import FWidget, FPeriodHolder, FPageTitle
from models import Reports, Store, Product
from Common.ui.table import FTableWidget
from Common.ui.util import formatted_number, is_int


class StateStockViewWidget(FWidget, FPeriodHolder):

    def __init__(self, parent=0, *args, **kwargs):

        super(StateStockViewWidget, self).__init__(
            parent=parent, *args, **kwargs)
        FPeriodHolder.__init__(self, *args, **kwargs)

        self.title = u"     Les Activités"
        self.parentWidget().setWindowTitle(Config.NAME_ORGA + self.title)
        self.parent = parent

        self.table = ReportTableWidget(parent=self, main_date=self.main_date)

        vbox = QtGui.QVBoxLayout()
        vbox.addWidget(FPageTitle(self.title))
        vbox.addWidget(self.periods_bar)
        vbox.addWidget(self.table)
        self.setLayout(vbox)

    def refresh(self):
        self.table.refresh()

    def change_period(self, main_date):
        self.table.refresh_period(main_date)


class ReportTableWidget(FTableWidget):

    def __init__(self, parent, main_date, *args, **kwargs):

        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = ["Magasin", u"Désignation", u"Entrée", u"Sortie"]

        self.parent = parent

        self.sorter = True
        self.stretch_columns = []
        self.align_map = {0: 'l', 1: 'l', 2: 'r', 3: 'r', 4: 'r'}
        # self.ecart = -5
        self.display_vheaders = False
        self.set_data_for(main_date)
        self.refresh()

    def refresh_period(self, main_date):
        """ """
        self._reset()
        self.set_data_for(main_date)
        self.refresh()

    def set_data_for(self, main_date):

        try:
            on, end = main_date.current.current
        except:
            on, end = main_date.current
        on = datetime(on.year, on.month, on.day, 0, 0, 0)
        end = datetime(end.year, end.month, end.day, 23, 59, 59)
        reports = []
        this_periode_rpt = Reports.select().where(Reports.date >= on,
                                                  Reports.date <= end)
        for store in Store.select().order_by(Store.name):
            if ([(i) for i in this_periode_rpt.where(Reports.store << [store, ])] == []):
                continue
            cpt = 0
            for prod in Product.select().order_by(Product.name):
                if ([(i) for i in this_periode_rpt.where(Reports.store == store,
                                                         Reports.product << [prod, ])] == []):
                    continue
                dict_store = {}
                repts = this_periode_rpt.where(
                    Reports.store == store, Reports.product == prod)
                dict_store["store"] = store.name if cpt < 1 else ""
                dict_store["product"] = prod.name
                dict_store["sum_qty_in"] = repts.select(
                    peewee.fn.SUM(Reports.qty_use)).where(Reports.type_ == Reports.E).scalar()
                dict_store["sum_qty_out"] = repts.select(
                    peewee.fn.SUM(Reports.qty_use)).where(Reports.type_ == Reports.S).scalar()
                cpt += 1
                reports.append(dict_store)

        self.data = [(rep.get('store'), rep.get('product'), rep.get('sum_qty_in'),
                      rep.get('sum_qty_out')) for rep in reports]

    def click_item(self, row, column, *args):
        product_column = 0
        if column == product_column:
            from ui.by_product import By_productViewWidget
            self.parent.change_main_context(By_productViewWidget,
                                            product=self.data[row][product_column])
        else:
            return

    def extend_rows(self):
        pass
