#!usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad


from PyQt4.QtGui import QVBoxLayout, QGridLayout, QIcon, QPushButton

from datetime import datetime
from configuration import Config
from models import (Store, Product, Reports)

from Common.ui.common import (FWidget, FLabel, BttExportPDF, BttExportXLSX)
from Common.ui.util import show_date
from Common.ui.table import FTableWidget


class ReportForStoreWidget(FWidget):

    def __init__(self, store="", parent=0, *args, **kwargs):
        super(ReportForStoreWidget, self).__init__(
            parent=parent, *args, **kwargs)
        self.title = u"<h1> Situation du : <i>{}</i></h1>".format(store)
        self.parentWidget().set_window_title("Magasin {}".format(store))
        self.parent = parent
        self.store = Store.get(name=store)

        self.table_resultat = ReportTableWidget(parent=self)

        self.prod_label = FLabel(self.title)
        self.btt_input = QPushButton(QIcon.fromTheme(
            '', QIcon(u"{}in.png".format(Config.img_media))), u"Entrée")
        self.btt_input.clicked.connect(self.goto_input)
        self.btt_output = QPushButton(QIcon.fromTheme(
            '', QIcon(u"{}out.png".format(Config.img_media))), u"Sortie")
        self.btt_output.clicked.connect(self.goto_output)
        self.btt_transfer = QPushButton(
            QIcon.fromTheme('', QIcon(u"{}transfer.png".format(
                Config.img_media))), u"Transfert")
        self.btt_transfer.clicked.connect(self.goto_transfer)

        self.btt_export_pdf = BttExportPDF("")
        self.btt_export_pdf.clicked.connect(self.export_pdf)
        self.btt_export_xlsx = BttExportXLSX("")
        self.btt_export_xlsx.clicked.connect(self.export_xlsx)
        gridbox = QGridLayout()
        gridbox.addWidget(self.btt_input, 0, 1)
        gridbox.addWidget(self.btt_output, 0, 2)
        gridbox.addWidget(self.btt_transfer, 0, 3)
        gridbox.setColumnStretch(7, 2)
        gridbox.addWidget(self.btt_export_pdf, 0, 8)
        gridbox.addWidget(self.btt_export_xlsx, 0, 9)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.prod_label)
        vbox.addLayout(gridbox)
        vbox.addWidget(self.table_resultat)
        self.setLayout(vbox)

    def goto_input(self):
        from ui.stock_input import StockInputWidget
        self.change_main_context(StockInputWidget, store=self.store)

    def goto_output(self):
        from ui.stock_output import StockOutputWidget
        self.change_main_context(StockOutputWidget, store=self.store)

    def goto_transfer(self):
        from ui.stock_transfer import StockTransferWidget
        self.parent.open_dialog(
            StockTransferWidget, modal=True, store=self.store, table_p=self.table_resultat)

    def export_pdf(self):
        from Common.exports_pdf import export_dynamic_data
        export_dynamic_data(self.table_resultat.dict_data())

    def export_xlsx(self):

        from Common.exports_xlsx import export_dynamic_data
        export_dynamic_data(self.table_resultat.dict_data())


class ReportTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):

        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = [
            "Produit", "Restante(carton)", "Restante (pièce)", "Date"]

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

        for prod in [p for p in Product.select().order_by(Product.name)]:
            try:
                repts = Reports.select().where(
                    Reports.store == self.store, Reports.product == prod
                ).order_by(-Reports.date)[0]
                remaining = repts.remaining
                last_op = repts.date
                print(repts.product, remaining)
            except Exception as e:
                continue
            dict_store = {}
            dict_store["prod"] = prod.name
            dict_store["last_remaining_box"] = remaining
            dict_store["last_remaining_p"] = remaining * prod.number_parts_box
            dict_store["last_op"] = last_op
            if remaining > 0:
                reports.append(dict_store)

        self.data = [(rep.get('prod'), rep.get('last_remaining_box'),
                      rep.get('last_remaining_p'), show_date(
            rep.get('last_op'))) for rep in reports]
        self.refresh()

    def dict_data(self):

        return {
            'title': "Situation du {}".format(self.store),
            'file_name': "report_store",
            'headers': self.hheaders,
            'data': self.data,
            'date': show_date(datetime.now()),
            'sheet': self.store.name,
            'widths': self.stretch_columns
        }
