#!usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from PyQt4.QtGui import (
    QVBoxLayout, QCompleter, QComboBox, QDialog, QFormLayout)
from PyQt4.QtCore import QDate, Qt

from Common.ui.common import (
    FWidget, Button, FormLabel, LineEdit, IntLineEdit, FormatDate)
from Common.ui.util import (
    date_to_datetime, check_is_empty, is_valide_codition_field)

from models import (Store, Product, Reports)


class StockTransferWidget(QDialog, FWidget):

    def __init__(self, table_p, parent, store=None, *args, **kwargs):
        FWidget.__init__(self, parent, *args, **kwargs)
        self.setWindowTitle(
            "Transfert depuis le magasin {}".format(store))
        self.table_p = table_p
        self.parent = parent
        self.store = store
        vbox = QVBoxLayout(self)

        self.date_field = FormatDate(QDate.currentDate())
        self.qtty_field = IntLineEdit()
        self.product_field = LineEdit()
        # self.product_field.textChanged.connect(self.product)
        self.product_field.setPlaceholderText(u"Rechercher un product")
        self.product_field.setMaximumHeight(40)
        completion_values = [catg.name for catg in Product.all()]
        completer = QCompleter(completion_values, parent=self)
        completer.setCaseSensitivity(Qt.CaseInsensitive)
        self.product_field.setCompleter(completer)
        # Combobox widget for add store
        self.liste_store = Store.select().where(Store.name != self.store.name)
        print(self.liste_store)
        self.store_box = QComboBox()
        for index in range(0, len(self.liste_store)):
            op = self.liste_store[index]
            self.store_box.addItem(op.name, op.id)

        formbox = QFormLayout()
        formbox.addRow(
            FormLabel(u"Transfert de {} vers ".format(
                self.store.name)), self.store_box)
        formbox.addRow(FormLabel(u"Produit : *"), self.product_field)
        formbox.addRow(FormLabel(u"Quatité : *"), self.qtty_field)
        formbox.addRow(FormLabel(u"Date : *"), self.date_field)

        butt = Button(u"Enregistrer")
        butt.clicked.connect(self.save)
        formbox.addRow("", butt)

        vbox.addLayout(formbox)

    def save(self):

        print("Save")
        # field_error
        if check_is_empty(self.product_field):
            return
        if check_is_empty(self.qtty_field):
            return
        if check_is_empty(self.date_field):
            return

        product_name = str(self.product_field.text())
        product = Product.select().where(Product.name == product_name)

        if is_valide_codition_field(
                self.product_field, "Le produit {} n'existe pas".format(
                    product_name), product.count() == 0):
            return

        qtty = int(self.qtty_field.text())
        date_op = date_to_datetime(str(self.date_field.text()))
        store_dest = self.liste_store[self.store_box.currentIndex()]

        rep = Reports(
            orders=None, date=date_op, product=product.get(), qty_use=qtty,
            store=self.store, type_=Reports.S)

        remaining = rep.last_report().remaining
        if is_valide_codition_field(
            self.qtty_field, "Il ne reste que {} {} dans le magasin {}".format(
                remaining, rep.product.name, self.store.name), remaining < qtty):
            return

        try:
            rep.save()
        except Exception as e:
            print(e)

        rep_dest = Reports(
            orders=None, date=date_op, product=product.get(), qty_use=qtty,
            type_=Reports.E, store=store_dest)
        try:
            rep_dest.save()
        except Exception as e:
            print(e)

        try:
            self.close()
            self.table_p.refresh_()
            self.parent.Notify(u"Transfert de {} du {} <==> {}".format(
                rep.qty_use, rep.store.name, rep.store.rep_dest), "success")
        except Exception as e:
            print(e)
