#!usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad


from PyQt4.QtGui import (QVBoxLayout, QTableWidgetItem, QIcon, QGridLayout)
# from PyQt4.QtCore import QDate, Qt

from configuration import Config
from models import Invoice
from tools.export_pdf2 import pdFview
from Common.ui.util import uopen_file
from Common.ui.common import (FWidget, LineEdit, FPageTitle, MenuBtt)
from Common.ui.util import (show_date)
from Common.ui.table import FTableWidget

from ui.invoice_show import ShowInvoiceViewWidget


class InvoiceViewWidget(FWidget):

    def __init__(self, product="", parent=0, *args, **kwargs):
        super(InvoiceViewWidget, self).__init__(parent=parent, *args, **kwargs)
        self.parentWidget().setWindowTitle(
            "{} {}".format(Config.APP_NAME, "FACTURES"))
        self.parent = parent

        vbox = QVBoxLayout(self)

        self.search_field = LineEdit()
        self.search_field.setPlaceholderText("Rechercher un produit")
        self.search_field.setMaximumSize(
            300, 400)
        self.search_field.textChanged.connect(self.finder)

        editbox = QGridLayout()
        table_invoice = QVBoxLayout()

        self.title_invoice = FPageTitle(u"Les Factures")
        self.table_invoice = InvoiceTableWidget(parent=self)

        self.add_invoice = MenuBtt(u"+ &Facture")
        self.add_invoice.clicked.connect(self.goto_add_invoice)
        self.add_invoice.setMaximumSize(
            200, self.add_invoice.maximumSize().height())
        editbox.addWidget(self.add_invoice, 0, 0)
        editbox.addWidget(self.search_field, 0, 4)
        editbox.setColumnStretch(1, 1)

        table_invoice.addLayout(editbox)
        table_invoice.addWidget(self.table_invoice)
        vbox.addWidget(self.title_invoice)
        vbox.addLayout(table_invoice)
        self.setLayout(vbox)

    def goto_add_invoice(self):
        """ """
        from ui.invoice_add_view import InvoiceAddViewWidgetDialog

        self.open_dialog(InvoiceAddViewWidgetDialog, modal=True, table_p=self.table_invoice)

    def finder(self):
        search_term = self.search_field.text()
        self.table_invoice.refresh_(search_term)


class InvoiceTableWidget(FTableWidget):

    def __init__(self, parent):
        FTableWidget.__init__(self, parent=parent)
        self.hheaders = [u"Utilisateur", u"Facture N°", u"Date",
                         u"Doit", u"Consulter", "Imprimer"]

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
                invoices = Invoice.select().where(
                    Invoice.location.contains(value) |
                    Invoice.client.contains(value))
        else:
            invoices = Invoice.select().order_by(Invoice.number.asc())

        self.data = [(invoice.owner, invoice.number, show_date(invoice.date),
                      invoice.client, "", "") for invoice in invoices]

    def _item_for_data(self, row, column, data, context=None):
        if column == 4:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(
                img_media=Config.img_cmedia, img="find.png")), (u"voir"))
        if column == 5:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(
                img_media=Config.img_cmedia, img="pdf.png")), (""))

        return super(InvoiceTableWidget, self)._item_for_data(row, column,
                                                              data, context)

    def click_item(self, row, column, *args):
        # last_column = self.hheaders.__len__() - 1
        self.invoice = Invoice.get(number=(self.data[row][1]))
        if column == 4:
            self.parent.change_main_context(
                ShowInvoiceViewWidget,
                table_p=self, invoice=self.invoice)
        if column == 5:
            pdf = pdFview("invoice", self.invoice)
            uopen_file(pdf)
