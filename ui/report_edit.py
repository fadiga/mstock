#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga

from PyQt4 import QtGui
from PyQt4 import QtCore

from Common.ui.common import FWidget, FBoxTitle, FPageTitle, Button, FormatDate
from Common.ui.util import date_to_datetime
from models import Reports, Product, Store


class EditReportViewWidget(QtGui.QDialog, FWidget):

    def __init__(self, table_p, report, parent, *args, **kwargs):
        QtGui.QDialog.__init__(self, parent, *args, **kwargs)
        self.setWindowTitle(u"Modification")
        self.title = FPageTitle(u"Vous le vous modifié ?")

        self.rep = report
        self.parent = parent
        self.table_p = table_p
        vbox = QtGui.QVBoxLayout()

        self.qty_use = QtGui.QLineEdit(str(self.rep.qty_use))
        self.qty_use.setValidator(QtGui.QIntValidator())

        self.date_ = FormatDate(QtCore.QDate(self.rep.date))

        self.time = QtGui.QDateTimeEdit(QtCore.QTime.currentTime())
        formbox = QtGui.QVBoxLayout()
        editbox = QtGui.QGridLayout()
        formbox.addWidget(FBoxTitle(u"Modification"))
        # Combobox widget

        i = 0
        self.liste_type = Reports.TYPES
        self.box_type = QtGui.QComboBox()
        for index in range(0, len(self.liste_type)):
            typ = self.liste_type[index]
            if typ[0] == self.rep.type_:
                i = index
            sentence = u"%(type_)s" % {'type_': typ[1]}
            self.box_type.addItem(sentence, typ[0])
            self.box_type.setCurrentIndex(i)

        self.liste_store = Store.select().order_by(Store.name.asc())
        self.box_store = QtGui.QComboBox()
        for index in range(0, len(self.liste_store)):
            store = self.liste_store[index]
            if store == self.rep.store:
                i = index
            sentence = u"%(name)s" % {'name': store.name}
            self.box_store.addItem(sentence, store.id)
            self.box_store.setCurrentIndex(i)

        self.liste_product = Product.select().order_by(Product.name.asc())
        self.box_prod = QtGui.QComboBox()

        for index in range(0, len(self.liste_product)):
            prod = self.liste_product[index]
            if prod == self.rep.product:
                i = index
            sentence = u"%(name)s" % {'name': prod.name}
            self.box_prod.addItem(sentence, prod.id)
            self.box_prod.setCurrentIndex(i)

        self.box_type.setEnabled(False)
        self.date_.setEnabled(False)
        self.box_store.setEditable(True)
        self.box_prod.setEditable(True)
        editbox.addWidget(QtGui.QLabel(u"Type"), 0, 0)
        editbox.addWidget(self.box_type, 0, 1)
        editbox.addWidget(QtGui.QLabel(u"Store"), 1, 0)
        editbox.addWidget(self.box_store, 1, 1)
        editbox.addWidget(QtGui.QLabel(u"Produit"), 2, 0)
        editbox.addWidget(self.box_prod, 2, 1)
        editbox.addWidget(QtGui.QLabel(u"Quantité"), 3, 0)
        editbox.addWidget(self.qty_use, 3, 1)
        editbox.addWidget(QtGui.QLabel((u"Date")), 4, 0)
        editbox.addWidget(self.date_, 4, 1)
        butt = Button(u"Enregistrer")
        butt.clicked.connect(self.report_edit)
        cancel_but = Button(u"Annuler")
        cancel_but.clicked.connect(self.cancel)
        editbox.addWidget(butt, 5, 1)
        editbox.addWidget(cancel_but, 5, 0)
        formbox.addLayout(editbox)
        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def cancel(self):
        self.close()

    def report_edit(self):

        report = self.rep
        # report.type_ = self.box_type.currentIndex()
        report.store = self.liste_store[self.box_store.currentIndex()]
        report.product = self.liste_product[self.box_prod.currentIndex()]
        report.qty_use = str(self.qty_use.text())
        # report.remaining = 0
        # report.date = date_to_datetime(self.date_.text())
        report.save()
        self.cancel()
        self.table_p.refresh_()
        self.parent.Notify("Votre rapport a été modifié", "success")
