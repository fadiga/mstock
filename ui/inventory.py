#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from datetime import date

from PyQt4 import QtGui, QtCore

from configuration import Config
from Common.ui.common import (FWidget, FPageTitle, FormLabel, BttExportXLS,
                              BttSmall, FormatDate)
from database import Reports, Product
from Common.ui.table import FTableWidget
from Common.ui.util import formatted_number, is_int, date_on_or_end
from Common.exports_xlsx import export_dynamic_data


class InventoryViewWidget(FWidget):

    def __init__(self, parent=0, *args, **kwargs):
        super(InventoryViewWidget, self).__init__(
            parent=parent, *args, **kwargs)

        self.parent = parent

        self.title = u"Inventaire des articles"
        self.parentWidget().setWindowTitle(Config.NAME_ORGA + " " + self.title)

        self.invent_table = InventoryTableWidget(parent=self)

        self.on_date = FormatDate(QtCore.QDate(date.today().year, 1, 1))
        self.end_date = FormatDate(QtCore.QDate.currentDate())
        self.btt_ok = BttSmall(u"Ok")
        self.btt_ok.clicked.connect(self.rapport_filter)
        self.btt_export = BttExportXLS(u"Exporter")
        self.btt_export.clicked.connect(self.export_xls)
        self.btt_export.setEnabled(False)
        vbox = QtGui.QVBoxLayout()
        # Grid
        gridbox = QtGui.QGridLayout()
        gridbox.addWidget(FormLabel(u"Date debut"), 0, 1)
        gridbox.addWidget(self.on_date, 0, 2)
        gridbox.addWidget(FormLabel(u"Date fin"), 1, 1)
        gridbox.addWidget(self.end_date, 1, 2)
        gridbox.addWidget(self.btt_ok, 1, 3)
        gridbox.setColumnStretch(4, 5)
        gridbox.addWidget(self.btt_export, 1, 6)
        vbox.addWidget(FPageTitle(self.title))
        vbox.addLayout(gridbox)
        vbox.addWidget(self.invent_table)
        self.setLayout(vbox)

    def refresh(self):
        self.invent_table.refresh()

    def rapport_filter(self):
        self.btt_export.setEnabled(True)
        self.invent_table.refresh_(on=date_on_or_end(self.on_date.text()),
                                   end=date_on_or_end(self.end_date.text(),
                                                      on=False))

    def export_xls(self):
        dict_data = {
            'file_name': "inventaire.xls",
            'headers': self.invent_table.hheaders,
            'data': self.invent_table.data,
            'sheet': self.title,
            'widths': self.invent_table.stretch_columns,
            "date": "Du " + self.on_date.text() + " au " + self.end_date.text()
        }
        export_dynamic_data(dict_data)


class InventoryTableWidget(FTableWidget):

    """ """

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent
        self.pparent = parent.parent

        self.hheaders = [u"Magasin", u"Code art.", u"Article",
                         u"Qtté Restante (Carton)", "Qtté (piéce)"]
        self.stretch_columns = [0, 1, 2, 3]
        self.align_map = {0: 'l', 1: 'l', 2: 'l', 3: 'r'}
        self.display_vheaders = True
        self.live_refresh = False
        self.sorter = True
        self.refresh_()

    def refresh_(self, on=None, end=None):
        self._reset()
        self.set_data_for(on, end)
        self.refresh()

    def set_data_for(self, on, end):

        if on:
            reports = []
            for prod in Product.all():
                try:
                    reports.append(Reports.select().where(
                        Reports.product == prod, Reports.date >= on,
                        Reports.date <= end).order_by(Reports.date.desc())
                        .get())
                except:
                    pass
            self.data = [(rep.store.name, rep.product.code, rep.product.name,
                          rep.remaining, rep.remaining * rep.product.number_parts_box)
                         for rep in reports]

    def _item_for_data(self, row, column, data, context=None):

        # if column == 2:
        #     line_edit = IntLineEdit("")
        #     line_edit.textChanged.connect(self.changed_value)
        #     return line_edit
        return super(InventoryTableWidget, self)._item_for_data(row, column,
                                                                data, context)

    def click_item(self, row, column, *args):
        from ui.by_product import By_productViewWidget
        if column == 1:
            try:
                # print("UUUUUUU", self.data[row][1])
                self.parent.change_main_context(
                    By_productViewWidget, table_p=self,
                    product=Product.get(code=self.data[row][1]))
            except IndexError:
                pass

    def changed_value(self, refresh=False):

        some = 0
        for row_num in xrange(0, self.data.__len__()):
            ui_item = (is_int(self.item(row_num, 1).text()) *
                       is_int(self.cellWidget(row_num, 2).text()))
            some += ui_item
            ui_item_ = QtGui.QTableWidgetItem(formatted_number(ui_item))
            ui_item_.setTextAlignment(QtCore.Qt.AlignRight)
            self.setItem(row_num, 3, ui_item_)
        row_num += 1
        som_val = QtGui.QTableWidgetItem(formatted_number(some))
        som_val.setTextAlignment(QtCore.Qt.AlignRight)
        self.setItem(row_num + 1, 2, QtGui.QTableWidgetItem(u"%s" % u"TOTAUX"))
        self.setItem(row_num + 1, 3, som_val)

    def get_table_items(self):
        """  """
        list_order = []
        for i in range(self.rowCount() - 1):
            liste_item = []
            try:
                liste_item.append(str(self.item(i, 0).text()))
                liste_item.append(is_int(self.item(i, 1).text()))
                liste_item.append(is_int(self.cellWidget(i, 2).text()))
                liste_item.append(is_int(self.item(i, 3).text()))
                list_order.append(liste_item)
            except:
                liste_item.append("")

        return list_order

    def refresh_period(self, l_date):
        self._reset()
        self.set_data_for(l_date)
        self.refresh()

    def extend_rows(self):

        pw = (self.parentWidget().width()) / 4
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, pw)
        self.setColumnWidth(3, pw)

        nb_rows = self.rowCount()
        self.setRowCount(nb_rows + 2)
        self.setSpan(nb_rows, 0, 2, 2)
        mtt_ttc = QtGui.QTableWidgetItem(u"TOTAUX: ")
        mtt_ttc.setTextAlignment(QtCore.Qt.AlignRight)
        self.setItem(nb_rows + 1, 2, mtt_ttc)

        self.montant_ht = 0
        for row_num in xrange(0, self.data.__len__()):
            mtt = is_int(self.item(row_num, 3).text())
            self.montant_ht += mtt
        # Montant TTC
        montant_ttc = QtGui.QTableWidgetItem(formatted_number(self.montant_ht))
        montant_ttc.setTextAlignment(QtCore.Qt.AlignRight)
        self.setItem(row_num + 2, 3, montant_ttc)
