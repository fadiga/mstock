#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import datetime
from PyQt4.QtGui import (QVBoxLayout, QIcon, QTableWidgetItem)

from Common.tabpane import tabbox
from Common.ui.common import FWidget, FPageTitle, FBoxTitle
from Common.ui.table import FTableWidget
from Common.ui.util import (show_date, formatted_number, date_on_or_end)

from models import Reports
from configuration import Config
from data_helper import (lastes_upper_of)


class DashbordViewWidget(FWidget):

    """ Shows the home page  """

    def __init__(self, parent=0, *args, **kwargs):
        super(DashbordViewWidget, self).__init__(
            parent=parent, *args, **kwargs)

        self.parentWidget().set_window_title("TABLEAU DE BORD")

        self.parent = parent
        vbox = QVBoxLayout()
        table_alert = QVBoxLayout()
        table_mouvement = QVBoxLayout()

        # self.search_field = LineEdit()
        # self.search_field.setToolTip("Rechercher un produit")
        # self.search_field.setMaximumSize(
        #     500, self.search_field.maximumSize().height())
        # self.search_field.textChanged.connect(self.finder)

        self.title = FPageTitle("TABLEAU DE BORD")

        self.title_alert = FBoxTitle(u"Les alertes ")
        self.table_alert = AlertTableWidget(parent=self)
        # table_alert.addWidget(self.title_alert)
        table_alert.addWidget(self.table_alert)

        self.table_mouvement = GReportTableWidget(parent=self)
        self.title_mouvement = FBoxTitle(
            show_date(self.table_mouvement.today, time=False))
        # table_invoice.addWidget(self.title_invoice)
        # table_mouvement.addWidget(self.title_mouvement)
        table_mouvement.addWidget(self.table_mouvement)
        tab_widget = tabbox((table_mouvement, u"Mouvements d'aujourd'hui"),
                            (table_alert, u"Alerte"))

        vbox.addWidget(self.title)
        vbox.addWidget(tab_widget)
        self.setLayout(vbox)


class GReportTableWidget(FTableWidget):

    """ """

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [u" ", u"Magasin", u"Produit", u"Quantité utilisé",
                         u"Restante", u"Date"]

        self.today = datetime.now()
        self.stretch_columns = [1, 2, 5]
        self.align_map = {3: "r", 4: "r"}
        self.sorter = True
        self.display_vheaders = False
        # self.display_fixed = True
        self.refresh_()

    def refresh_(self):
        """ """
        # je cache la 6 eme colonne
        self._reset()
        self.set_data_for()
        self.refresh()
        # self.hideColumn(6)
        self.setColumnWidth(0, 30)
        pw = self.parent.parent.page_width() / 5
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)
        self.setColumnWidth(3, pw)

    def set_data_for(self):
        self.data = [(rap.type_, rap.store.name, rap.product,
                      formatted_number(rap.qty_use),
                      formatted_number(rap.remaining),
                      show_date(rap.date))
                     for rap in Reports.select().where(
            Reports.date < date_on_or_end(self.today, on=False),
            Reports.date > date_on_or_end(self.today)
        ).order_by(Reports.id.desc())]

    def _item_for_data(self, row, column, data, context=None):
        if column == 0 and self.data[row][0] == Reports.E:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(
                img_media=Config.img_media, img="in.png")), u"")
        if column == 0 and self.data[row][0] == Reports.S:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(
                img_media=Config.img_media, img="out.png")), u"")

        return super(GReportTableWidget, self)._item_for_data(row, column,
                                                              data, context)

    def click_item(self, row, column, *args):
        pass


class AlertTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = [u"Magasin", "Produits", u"Quantité restante",
                         u"Date de la dernière opération"]

        self.stretch_columns = [0, 1, 2, 3]
        self.align_map = {0: 'l', 1: 'l', 2: 'r', 3: 'l'}
        self.display_vheaders = False
        self.live_refresh = True
        # self.sorter = True
        self.refresh_()

    def refresh_(self):
        """ """
        self._reset()
        self.set_data_for()
        self.refresh()
        pw = self.width() / 5
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)

    def set_data_for(self):
        reports = lastes_upper_of(10)
        self.data = [(rep.store.name, rep.product.name, rep.remaining,
                      show_date(rep.date)) for rep in reports]
