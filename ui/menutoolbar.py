# !/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: fad

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtGui import (QIcon, QToolBar, QFont, QCursor)
from PyQt4.QtCore import Qt, QSize

from configuration import Config
from Common.ui.common import FWidget

from GCommon.ui.products import ProductsViewWidget
from GCommon.ui.stores import StoresViewWidget

from ui.state_stock import StateStockViewWidget
from ui.dashboard import DashbordViewWidget
# from ui.reports_managers import GReportViewWidget
from ui.invoice_view import InvoiceViewWidget
from ui.inventory import InventoryViewWidget
from ui.stock_input import StockInputWidget
from ui.order_view import OrderViewWidget
from ui.stock_output import StockOutputWidget
from ui.reports_managers import GReportViewWidget
from ui.report_product_store import ReportProductStoreWidget


class MenuToolBar(QToolBar, FWidget):

    def __init__(self, parent=None, admin=False, *args, **kwargs):
        QToolBar.__init__(self, parent, *args, **kwargs)

        self.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.setIconSize(QSize(30, 30))

        font = QFont()
        font.setPointSize(8)
        font.setBold(True)
        font.setWeight(75)
        self.setFont(font)
        self.setCursor(QCursor(Qt.PointingHandCursor))
        self.setAcceptDrops(True)
        self.setAutoFillBackground(True)
        # Menu File
        self.setOrientation(Qt.Horizontal)
        self.addAction(
            QIcon(u"{}exit.png".format(Config.img_cmedia)),
            u"Quiter", self.goto_exit)
        # self.addSeparator()
        menu = [{"name": u"Tableau de bord", "icon": 'dashboard',
                 "admin": False, "goto": DashbordViewWidget},
                {"name": u"Magasin", "icon": 'store', "admin": False,
                    "shortcut": "Ctrl+M", "goto": StoresViewWidget},
                {"name": u"Articles", "admin": True,
                    "icon": 'product', "goto": ProductsViewWidget},
                {"name": u"Entrée", "icon": 'in',
                    "admin": False, "goto": StockInputWidget},
                {"name": u"Sortie", "icon": 'out',
                    "admin": True, "goto": StockOutputWidget},
                {"name": u"Facturation", "icon": 'invoice', "admin": False,
                    "shortcut": "Ctrl+", "goto": InvoiceViewWidget},
                {"name": u"Commande", "admin": True,
                    "icon": 'order', "goto": OrderViewWidget},
                {"name": u"State", "icon": 'state',
                    "admin": False, "goto": StateStockViewWidget},
                {"name": u"Inventaire", "icon": 'inventory',
                 "admin": False, "goto": InventoryViewWidget},
                {"name": u"Situation du stock", "icon": '', "admin": False,
                    "shortcut": "ctrl+D", "goto": ReportProductStoreWidget},
                {"name": u"Mouvements", "icon": 'reports', "admin": False,
                    "shortcut": "alt+T", "goto": GReportViewWidget}]

        for m in menu:
            self.addSeparator()
            self.addAction(QIcon(
                "{}{}.png".format(Config.img_media, m.get('icon'))),
                m.get('name'), lambda m=m: self.goto(m.get('goto')))

    def goto(self, goto):
        self.change_main_context(goto)

    def goto_exit(self):
        self.parent().exit()
