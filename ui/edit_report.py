#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga

from PyQt4 import QtGui
from PyQt4 import QtCore

from Common.ui.common import FWidget, FBoxTitle, FPageTitle, Button, FormatDate
from Common.ui.util import date_to_datetime
from models import Reports, Product


class EditReportViewWidget(QtGui.QDialog, FWidget):

    def __init__(self, report, parent, *args, **kwargs):
        QtGui.QDialog.__init__(self, parent, *args, **kwargs)
        self.setWindowTitle(u"Modification")
        self.title = FPageTitle(u"Vous le vous modifié ?")

        self.op = report
        vbox = QtGui.QVBoxLayout()

        self.qty_use = QtGui.QLineEdit(str(self.op.qty_use))
        self.qty_use.setValidator(QtGui.QIntValidator())

        self.date_ = FormatDate(QtCore.QDate(self.op.date))

        self.time = QtGui.QDateTimeEdit(QtCore.QTime.currentTime())
        formbox = QtGui.QVBoxLayout()
        editbox = QtGui.QGridLayout()
        formbox.addWidget(FBoxTitle(u"Modification"))
        # Combobox widget

        i = 0
        self.liste_type = Reports.TYPES
        self.box_type = QtGui.QComboBox()
        for index in xrange(0, len(self.liste_type)):
            ty = self.liste_type[index]
            if ty == self.op.type_:
                i = index
            sentence = u"%(type_)s" % {'type_': ty}
            self.box_type.addItem(sentence, QtCore.QVariant(ty))
            self.box_prod.setCurrentIndex(i)
        # Combobox widget
        # self.liste_store = Store.order_by(desc(Store.id)).all()
        # self.box_mag = QtGui.QComboBox()
        # for index in xrange(0, len(self.liste_store)):
        #     op = self.liste_store[index]
        #     sentence = _(u"%(name)s") % {'name': op.name}
        #     self.box_mag.addItem(sentence, QtCore.QVariant(op.id))
        # Combobox widget

        self.liste_product = Product.all()
        self.box_prod = QtGui.QComboBox()

        for index in xrange(0, len(self.liste_product)):
            op = self.liste_product[index]
            if op == self.op.product.article:
                i = index
            sentence = u"%(article)s" % {'article': op.article}
            self.box_prod.addItem(sentence, QtCore.QVariant(op.id))
            self.box_prod.setCurrentIndex(i)

        editbox.addWidget(QtGui.QLabel(u"Type"), 0, 0)
        editbox.addWidget(self.box_type, 1, 0)
        # editbox.addWidget(QtGui.QLabel((_(u"Store"))), 0, 1)
        # editbox.addWidget(self.box_mag, 1, 1)
        editbox.addWidget(QtGui.QLabel(u"Produit"), 0, 2)
        editbox.addWidget(self.box_prod, 1, 2)
        editbox.addWidget(QtGui.QLabel(u"Quantité"), 0, 3)
        editbox.addWidget(self.qty_use, 1, 3)
        editbox.addWidget(QtGui.QLabel((u"Date")), 0, 4)
        editbox.addWidget(self.date_, 1, 4)
        butt = Button(u"Enregistrer")
        butt.clicked.connect(self.edit_report)
        cancel_but = Button(u"Annuler")
        cancel_but.clicked.connect(self.cancel)
        editbox.addWidget(butt, 2, 3)
        editbox.addWidget(cancel_but, 2, 4)
        formbox.addLayout(editbox)
        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def cancel(self):
        self.close()

    def edit_report(self):

        type_ = self.box_type.currentIndex()
        product = self.liste_product[self.box_prod.currentIndex()]
        qty_use = str(self.nbr_carton.text())
        date_ = self.date_.text()
        datetime_ = date_to_datetime(date_)

        report = self.op
        report.type_ = type_
        report.product = product
        report.qty_use = qty_use
        report.remaining = 0
        report.date = datetime_
        report.save()
        self.cancel()
        self.parent.Notify(u"Votre rapport a été modifié", "success")
