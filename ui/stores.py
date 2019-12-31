#!usr/bin/env python
# -*- encoding: utf-8 -*-
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)


from functools import partial
# from PyQt4.QtCore import Qt
from PyQt4.QtGui import (QVBoxLayout, QGridLayout, QGroupBox,
                         QIcon, QPushButton, QHBoxLayout)

from Common.ui.common import (FWidget, MenuBtt, IntLineEdit, LineEdit, FLabel)
from Common.exports_xlsx import export_dynamic_data

from configuration import Config


from ui.store_edit_or_add import EditOrAddStoresViewWidget

from ui.stock_input import StockInputWidget
from ui.stock_output import StockOutputWidget
from ui.report_for_store import ReportForStoreWidget
from models import Store


class StoresViewWidget(FWidget):

    def __init__(self, store="", parent=0, *args, **kwargs):
        super(StoresViewWidget, self).__init__(parent=parent,
                                               *args, **kwargs)
        self.parentWidget().setWindowTitle(Config.APP_NAME + u"  MAGASINS")

        self.parent = parent

        hbox = QHBoxLayout()
        vbox = QVBoxLayout()
        self.title = u"LES MAGASINS"
        gridbox = QGridLayout()

        self.name = LineEdit()
        self.stock_maxi = IntLineEdit()

        butt = MenuBtt(u"+ &Magasin")
        butt.clicked.connect(self.add_store)
        butt.setFixedHeight(70)
        gridbox.addWidget(butt, 0, 0)
        gridbox.setColumnStretch(0, 1)

        vbox.addLayout(gridbox)

        h1box = QHBoxLayout()
        for index, mg in enumerate(Store.all()):
            self.store_group_box(mg, index)
            if index % 2 == 0:
                h1box.addWidget(self.topLeftGroupBox)
            else:
                hbox.addWidget(self.topLeftGroupBox)

        vbox.addLayout(hbox)
        vbox.addLayout(h1box)
        self.setLayout(vbox)

    def store_group_box(self, store, index):
        self.topLeftGroupBox = QGroupBox(self.tr("{mg}".format(mg=store.name)))
        self.topLeftGroupBox.setStyleSheet("""
            QGroupBox {
                    max-height: 30em;
                    max-width: 50em;
                    background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E0E0E0, stop: 1 #FFFFFF);
                    border: 2px solid gray;
                    border-radius: 5px;
                    margin-top: 1ex; /* leave space at the top for the title */
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center; /* position at the top center */
                    padding: 0 3px;
                    background-color: qlineargradient(
                    x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #E0E0E0, stop: 1 #FFFFFF);
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    border-top-left-radius: 15px;
                    border-bottom-right-radius: 15px;
                    border-bottom-right-radius: 15px;
                    padding: 15px 50px;
                    background-color: #63707d;
                    color: rgb(255, 255, 255);
                }""")
        self.goto_button = QPushButton(u"Ouvrir")
        self.goto_button.setStyleSheet(
            "QPushButton {font-size:40px; background-color: #0052ff; color: #FFFFFF}"
            "QPushButton:pressed { background-color: gray }"
            "QCommandLinkButton:hover { background-color: #6a737c; color: #FFF}")
        self.goto_button.clicked.connect(partial(self.goto, ReportForStoreWidget, store=store))
        self.add_button = MenuBtt(u"Entrée")
        self.add_button.clicked.connect(partial(self.opento, StockInputWidget, store=store))
        self.add_button.setIcon(QIcon.fromTheme('', QIcon(u"{}in.png".format(Config.img_media))))
        self.sub_button = MenuBtt(u"Sortie")
        self.sub_button.setIcon(QIcon.fromTheme('', QIcon(u"{}out.png".format(Config.img_media))))
        self.sub_button.clicked.connect(partial(self.opento, StockOutputWidget, store=store))
        # self.cancel_button.setFlat(True)
        gridbox_ = QGridLayout()
        gridbox_.addWidget(FLabel(""), 0, 0, 0, 1)
        gridbox_.addWidget(self.goto_button, 1, 0, 1, 3)
        gridbox_.addWidget(self.add_button, 2, 0)
        gridbox_.addWidget(self.sub_button, 2, 2)
        self.topLeftGroupBox.setLayout(gridbox_)

    def export_xls(self):
        dict_data = {
            'file_name': "produits.xls",
            'headers': self.store_table.hheaders,
            'data': self.store_table.data,
            'sheet': self.title,
            'widths': self.store_table.stretch_columns
        }
        export_dynamic_data(dict_data)

    def add_store(self, store=None):
        ''' add operation '''
        self.parent.open_dialog(EditOrAddStoresViewWidget, modal=True,
                                store=store, table_p=self, opacity=1)

    def goto(self, goto, store=None):
        self.change_main_context(goto, store=store)

    def opento(self, goto, store=None):
        self.parent.open_dialog(goto, modal=True, store=store, opacity=1)
