#!usr/bin/env python
# -*- encoding: utf-8 -*-
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtGui import (QVBoxLayout, QTableWidgetItem,
                         QIcon, QGridLayout, QMessageBox, QPushButton)
from PyQt4.QtCore import Qt

from configuration import Config
from models import Reports
from tools.export_pdf import pdFview
from tools.export_xls import write_invoice_xls
from Common.ui.util import formatted_number, is_int, uopen_file
from Common.ui.common import (
    FWidget, FPageTitle, FLabel, Deleted_btt)
from Common.ui.table import FTableWidget


class ShowInvoiceViewWidget(FWidget):

    def __init__(self, table_p, invoice, parent=0, *args, **kwargs):
        super(ShowInvoiceViewWidget, self).__init__(
            parent=parent, *args, **kwargs)

        self.invoice = invoice

        self.parentWidget().setWindowTitle(Config.NAME_ORGA +
                                           u" CONSULTATION DE FACTURE")

        self.table_p = table_p
        self.parent = parent

        vbox = QVBoxLayout()
        vbox.addWidget(FPageTitle(u"Facture"))

        tablebox = QVBoxLayout()
        self.table_show = ShowInvoiceTableWidget(parent=self)
        tablebox.addWidget(self.table_show)

        formbox = QVBoxLayout()
        editbox = QGridLayout()
        xls_bicon = QIcon.fromTheme(
            '', QIcon(u"{}xls.png".format(Config.img_cmedia)))
        pdFicon = QIcon.fromTheme(
            '', QIcon(u"{}pdf.png".format(Config.img_cmedia)))
        self.button_pdf = QPushButton(pdFicon, u"")
        self.button_pdf.setFixedWidth(30)
        self.button_pdf.setFixedHeight(30)
        self.button_xls = QPushButton(xls_bicon, u"")
        self.button_xls.setFixedWidth(30)
        self.button_xls.setFixedHeight(30)
        self.button_pdf.released.connect(self.printer_pdf)
        self.button_xls.released.connect(self.printer_xls)

        editbox.addWidget(FLabel(u"Facture N°: %s"
                                 % self.invoice.number), 0, 0)
        editbox.addWidget(FLabel(u"%s le %s" % (
            self.invoice.location, self.invoice.date.strftime(u'%x'))), 1, 4)
        editbox.addWidget(FLabel(u"Doit: %s " % self.invoice.client), 1, 0)
        editbox.addWidget(self.button_pdf, 1, 5)
        editbox.addWidget(self.button_xls, 1, 6)

        formbox.addLayout(editbox)
        vbox.addLayout(formbox)
        vbox.addLayout(tablebox)
        self.setLayout(vbox)

    def printer_xls(self):
        write_invoice_xls("invoice.xls", self.invoice)

    def printer_pdf(self):
        pdFreport = pdFview("invoice", self.invoice)
        uopen_file(pdFreport)

    def annulation(self):
        reply = QMessageBox.question(
            self, 'Confirmation', u"<h2 style='color:red;'>Voulez vous "
            "vraiment annuler cette facture?</h2>",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            from ui.dashboard import DashbordViewWidget
            rep = Reports()
            rep.store = 1
            for item in Reports.filter(invoice=self.invoice):
                item.delete_instance()
            self.invoice.delete_instance()
            self.change_main_context(DashbordViewWidget)


class ShowInvoiceTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [_("Quantité"), _("Désignation"), _("Prix Unitaire"),
                         _("Montant")]
        self.stretch_columns = [1, 3]
        self.align_map = {2: 'r', 3: 'r'}
        # self.max_rows = 100
        # self.display_vheaders = False
        # self.display_fixed = True
        self.refresh_()

    def refresh_(self):
        """ """
        self._reset()
        self.set_data_for()
        self.refresh()

        pw = self.parent.parent.page_width() / 5
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, pw * 2)
        self.setColumnWidth(2, pw)
        self.setColumnWidth(3, pw)

    def set_data_for(self):

        items = self.parent.invoice.items if self.parent.invoice.items else []
        self.data = [(item.quantity, item.description, item.price,
                      item.quantity * item.price) for item in items]

    def extend_rows(self):

        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 3)
        self.setSpan(nb_rows, 0, 3, 2)
        mtt_ttc = QTableWidgetItem(u"Total: ")
        mtt_ttc.setTextAlignment(Qt.AlignRight)
        self.setItem(nb_rows + 1, 2, mtt_ttc)

        montant_ht = 0
        for row_num in xrange(0, self.data.__len__()):
            quantity = is_int(self.item(row_num, 0).text())
            pu = is_int(self.item(row_num, 2).text())
            montant_ht += (quantity * pu)
        # Montant TTC
        montant_ttc = QTableWidgetItem(formatted_number(montant_ht))
        montant_ttc.setTextAlignment(Qt.AlignRight)
        self.setItem(row_num + 2, 3, montant_ttc)

        bicon = QIcon.fromTheme(
            '', QIcon(u"{}del.png".format(Config.img_media)))
        # self.button = QPushButton(bicon, u"Annuler la facture")
        self.button = Deleted_btt(u"Annuler la facture")
        self.button.released.connect(self.parent.annulation)
        # self.setCellWidget(nb_rows + 2, 3, self.button)

        # self.setColumnWidth(1, 250)
