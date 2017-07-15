#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: fad

from PyQt4.QtGui import (QIcon, QAction)
from PyQt4.QtCore import SIGNAL

from configuration import Config
from Common.ui.common import FWidget
# from Common.ui.login import LoginWidget
# from Common.exports import export_database_as_file

from GCommon.ui.stores import StoresViewWidget
from GCommon.ui.products import ProductsViewWidget

from ui.invoice_view import InvoiceViewWidget
from ui.inventory import InventoryViewWidget
from ui.state_stock import StateStockViewWidget
from ui.order_view import OrderViewWidget
from ui.dashboard import DashbordViewWidget
from ui.stock_input import StockInputWidget
from ui.stock_output import StockOutputWidget
from ui.reports_managers import GReportViewWidget
from ui.report_product_store import ReportProductStoreWidget
# from ui.helps import HTMLView

from Common.ui.cmenubar import FMenuBar


class MenuBar(FMenuBar, FWidget):

    def __init__(self, parent=None, *args, **kwargs):
        FMenuBar.__init__(self, parent=parent, *args, **kwargs)

        # self.setWindowIcon(QIcon(QPixmap("{}".format(Config.APP_LOGO))))
        self.parent = parent

        menu = [{"name": u"Tableau de bord", "icon": 'dashboard', "admin": False, "shortcut": "Ctrl+T", "goto": DashbordViewWidget},
                {"name": u"Articles", "admin": True, "icon": 'product',
                    "shortcut": "Ctrl+P", "goto": ProductsViewWidget},
                {"name": u"Commande", "admin": True, "icon": 'order',
                    "shortcut": "Ctrl+O", "goto": OrderViewWidget},
                {"name": u"Inventaire", "admin": True, "icon": 'inventory',
                    "shortcut": "Ctrl+I", "goto": InventoryViewWidget},
                {"name": u"Entrée", "icon": 'in', "admin": False,
                    "shortcut": "Ctrl+E", "goto": StockInputWidget},
                {"name": u"Sortie", "icon": 'out', "admin": True,
                    "shortcut": "Ctrl+S", "goto": StockOutputWidget},
                {"name": u"State", "icon": 'state', "admin": False,
                    "shortcut": "Ctrl+R", "goto": StateStockViewWidget},
                {"name": u"Magasin", "icon": 'store', "admin": False,
                    "shortcut": "Ctrl+M", "goto": StoresViewWidget},
                {"name": u"Facturation", "icon": 'invoice', "admin": False,
                    "shortcut": "Ctrl+F", "goto": InvoiceViewWidget},
                {"name": u"Situation du stock", "icon": '', "admin": False,
                    "shortcut": "ctrl+D", "goto": ReportProductStoreWidget},
                {"name": u"Mouvements", "icon": 'reports', "admin": False,
                    "shortcut": "alt+T", "goto": GReportViewWidget},
                ]

        # Menu aller à
        goto_ = self.addMenu(u"&Aller a")

        for m in menu:
            el_menu = QAction(
                QIcon("{}{}.png".format(Config.img_media, m.get('icon'))), m.get('name'), self)
            el_menu.setShortcut(m.get("shortcut"))
            self.connect(
                el_menu, SIGNAL("triggered()"), lambda m=m: self.goto(m.get('goto')))
            goto_.addSeparator()
            goto_.addAction(el_menu)

        about = self.addMenu(u"Aide")
        about_ = QAction(QIcon.fromTheme('', QIcon('')),
                         u"À propos", self)
        about_.setShortcut("Ctrl+I")
        self.connect(about_, SIGNAL("triggered()"), self.goto_about)
        about.addAction(about_)

        sommaire_ = QAction(QIcon.fromTheme('', QIcon('')),
                            u"Sommaire", self)
        sommaire_.setShortcut("Alt+S")
        self.connect(sommaire_, SIGNAL("triggered()"), self.goto_help)
        about.addAction(sommaire_)
