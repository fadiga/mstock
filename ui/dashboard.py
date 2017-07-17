#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: ai ts=4 sts=4 et sw=4 nu
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from datetime import datetime
from PyQt4.QtGui import (QVBoxLayout, QIcon, QTableWidgetItem)

from Common.tabpane import tabbox
from Common.ui.common import FWidget, FPageTitle, FBoxTitle, LineEdit
from Common.ui.table import FTableWidget
from Common.ui.util import (show_date, formatted_number, raise_error,
                            date_on_or_end)

from models import Invoice, Reports, Store
from configuration import Config
from data_helper import (lastes_reports, lastes_upper_of, multi_store)

from ui.invoice_show import ShowInvoiceViewWidget


class DashbordViewWidget(FWidget):

    """ Shows the home page  """

    def __init__(self, parent=0, *args, **kwargs):
        super(DashbordViewWidget, self).__init__(
            parent=parent, *args, **kwargs)

        self.parentWidget().setWindowTitle(
            Config.APP_NAME + u"    TABLEAU DE BORD")

        self.parent = parent
        vbox = QVBoxLayout()
        table_invoice = QVBoxLayout()
        table_alert = QVBoxLayout()
        table_mouvement = QVBoxLayout()

        self.search_field = LineEdit()
        self.search_field.setToolTip("Rechercher un produit")
        self.search_field.setMaximumSize(
            500, self.search_field.maximumSize().height())
        self.search_field.textChanged.connect(self.finder)

        self.title = FPageTitle("TABLEAU DE BORD")

        self.title_alert = FBoxTitle(u"Les alertes ")
        self.table_alert = AlertTableWidget(parent=self)
        # table_alert.addWidget(self.title_alert)
        table_alert.addWidget(self.table_alert)

        self.title_invoice = FBoxTitle(u"Les stocks actual")
        self.table_invoice = InvoiceTableWidget(parent=self)
        table_invoice.addWidget(self.search_field)
        table_invoice.addWidget(self.table_invoice)

        self.table_mouvement = GReportTableWidget(parent=self)
        self.title_mouvement = FBoxTitle(
            show_date(self.table_mouvement.today, time=False))
        # table_invoice.addWidget(self.title_invoice)
        # table_mouvement.addWidget(self.title_mouvement)
        table_mouvement.addWidget(self.table_mouvement)
        tab_widget = tabbox((table_alert, u"Alertes sur les produits"),
                            (table_mouvement, u"Les Mouvements"),
                            (table_invoice, u"Les Factures"))

        vbox.addWidget(self.title)
        vbox.addWidget(tab_widget)
        self.setLayout(vbox)

    def finder(self):
        self.table_invoice.refresh_(str(self.search_field.text()))


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
                img_media=Config.img_media,  img="out.png")), u"")

        return super(GReportTableWidget, self)._item_for_data(row, column,
                                                              data, context)

    def click_item(self, row, column, *args):
        pass


class InvoiceTableWidget(FTableWidget):

    def __init__(self, parent):
        FTableWidget.__init__(self, parent=parent)
        self.hheaders = [u"Utilisateur", u"Facture N°", u"Date",
                         u"Doit", u"Consulter"]

        self.parent = parent

        self.sorter = True
        self.stretch_columns = [3, 2]
        # self.display_fixed = True
        self.align_map = {0: 'l', 1: 'r', 2: 'l', 3: 'l'}
        self.refresh_()

    def refresh_(self, value=None):
        """ """
        self._reset()
        self.set_data_for(value)
        self.refresh()

        pw = self.parent.parent.page_width() / 5
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)
        self.setColumnWidth(3, pw)

    def set_data_for(self, value):

        if value:
            try:
                invoices = Invoice.select().where(Invoice.number == int(value))
            except Exception as e:
                Config.logging.error(e)
                invoices = Invoice.select().where(Invoice.location.contains(value) |
                                                  Invoice.client.contains(value))
        else:
            invoices = Invoice.select().order_by(Invoice.number.asc())

        self.data = [(invoice.owner, invoice.number, show_date(invoice.date),
                      invoice.client, "") for invoice in invoices]

    def _item_for_data(self, row, column, data, context=None):
        if column == self.data[0].__len__() - 1:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(
                img_media=Config.img_media, img="go-next.png")), (u"voir"))

        return super(InvoiceTableWidget, self)._item_for_data(row, column,
                                                              data, context)

    def click_item(self, row, column, *args):
        last_column = self.hheaders.__len__() - 1
        if column != last_column:
            return
        try:
            self.parent.change_main_context(
                ShowInvoiceViewWidget,
                table_p=self, invoice=Invoice.get(number=(self.data[row][1])))
        except IndexError:
            pass


class AlertTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = [u"Magasin"] if multi_store else []
        self.hheaders += [u"Produits", u"Quantité restante",
                          u"Date de la dernière operation"]

        self.align_map = {0: 'l', 1: 'l', 2: 'r'} if multi_store else {
            0: 'l', 1: 'r', 2: 'r'}
        self.sorter = True
        self.refresh_()

    def refresh_(self):
        """ """
        self._reset()
        self.set_data_for()
        self.refresh()

    def set_data_for(self):
        reports = lastes_upper_of(10)
        if multi_store:
            self.data = [(rep.store.name, rep.product.name, rep.remaining,
                          show_date(rep.date)) for rep in reports]
        else:
            self.data = [(rep.product.name, rep.remaining, show_date(rep.date))
                         for rep in reports]
