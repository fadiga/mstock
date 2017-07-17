#!usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad


from PyQt4.QtGui import (QVBoxLayout, QGridLayout, QLineEdit, QFrame,
                         QCompleter, QTableWidgetItem)
from PyQt4.QtCore import QDate, Qt

from configuration import Config
from models import (Store, Product, Reports)

from Common.ui.common import (FWidget, FormatDate, FPageTitle)
from Common.ui.util import formatted_number, is_int, show_date
from Common.ui.table import FTableWidget


class ReportProductStoreWidget(FWidget):

    def __init__(self, product="", parent=0, *args, **kwargs):
        super(ReportProductStoreWidget, self).__init__(
            parent=parent, *args, **kwargs)
        title = u" <h1> Situation </h1>"
        self.parentWidget().setWindowTitle(Config.NAME_ORGA + title)
        self.parent = parent

        vbox = QVBoxLayout(self)
        editbox = QGridLayout()
        self.format_prod_label = "<h2 > Produit:<i style = 'color:blue' > {} < /i > Categorie: <i style = 'color:blue'> {} < /i > <h2 >"

        self.prod_label = FPageTitle(
            self.format_prod_label.format("...", "..."))
        self.date = FormatDate(QDate.currentDate())

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Rechercher un article")
        self.search_field.setMaximumSize(
            400, self.search_field.maximumSize().height())
        self.search_field.textChanged.connect(self.finder)

        completion_values = [catg.name for catg in Product.all()]
        completer = QCompleter(completion_values, parent=self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.search_field.setCompleter(completer)

        self.vline = QFrame()
        self.vline.setFrameShape(QFrame.VLine)
        self.vline.setFrameShadow(QFrame.Sunken)

        self.table_resultat = ReportTableWidget(parent=self)

        editbox.addWidget(self.search_field, 1, 0)
        # editbox.addWidget(self.vline, 1, 2, 2, 1)
        # editbox.setColumnStretch(3, 3)

        vbox.addWidget(self.prod_label)
        vbox.addLayout(editbox)
        vbox.addWidget(self.table_resultat)
        self.setLayout(vbox)

    def finder(self):
        value = str(self.search_field.text())
        self.table_resultat.refresh_(value)


class ReportTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):

        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.hheaders = ["Magasin",
                         "Restante(carton)", "Restante (pièce)", "Date"]

        self.parent = parent

        self.sorter = True
        self.stretch_columns = [0, 1, 2, 3]
        self.align_map = {0: 'l', 1: 'r', 2: 'r'}
        # self.ecart = -5
        self.display_vheaders = False
        self.refresh_()

    def refresh_(self, product=None):
        """ """
        self._reset()
        self.set_data_for(product)
        self.refresh()

        pw = self.width() / 5 - 20
        self.setColumnWidth(0, pw * 2)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)

    def set_data_for(self, product):
        if product:
            reports = []
            try:
                prod = Product.get(name=product)

                self.parent.prod_label.setText(
                    self.parent.format_prod_label.format(
                        prod.name, prod.category))
            except:
                return

            for store in Store.select().order_by(Store.name):
                try:
                    repts = Reports.select().where(
                        Reports.store == store, Reports.product == prod
                    ).order_by(-Reports.date)[0]
                    remaining = repts.remaining
                    last_op = repts.date
                except Exception as e:
                    print(e)
                    continue
                dict_store = {}
                dict_store["store"] = store.name
                dict_store["last_remaining_box"] = formatted_number(remaining)
                dict_store["last_remaining_p"] = formatted_number(
                    remaining * prod.number_parts_box)
                dict_store["last_op"] = last_op
                reports.append(dict_store)

            self.data = [(rep.get('store'), rep.get('last_remaining_box'),
                          rep.get('last_remaining_p'), show_date(
                              rep.get('last_op'))) for rep in reports]
            self.refresh()

    # def click_item(self, row, column, *args):
    #     product_column = 0
    #     if column == product_column:
    #         from ui.by_product import By_productViewWidget
    #         self.parent.change_main_context(
    #             By_productViewWidget, product=self.data[row][product_column])
    #     else:
    #         return

    def extend_rows(self):

        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 1)
        # self.setSpan(nb_rows, 0, 1, 1)
        mtt_ttc = QTableWidgetItem(u"TOTAUX: ")
        mtt_ttc.setTextAlignment(Qt.AlignRight)
        self.setItem(nb_rows, 0, mtt_ttc)

        tall_in = 0
        tall_out = 0

        for row_num in range(0, self.data.__len__()):
            all_in = is_int(str(self.item(row_num, 1).text()))
            tall_in += all_in
            all_out = is_int(str(self.item(row_num, 2).text()))
            tall_out += all_out

        # Montant TTC
        tall_in = QTableWidgetItem(formatted_number(tall_in))
        tall_in.setTextAlignment(Qt.AlignRight)
        self.setItem(row_num + 1, 1, tall_in)
        tall_out = QTableWidgetItem(formatted_number(tall_out))
        tall_out.setTextAlignment(Qt.AlignRight)
        self.setItem(row_num + 1, 2, tall_out)
