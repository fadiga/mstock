#!usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from PyQt4.QtGui import (QVBoxLayout, QHBoxLayout, QTableWidgetItem,
                         QIcon, QGridLayout, QSplitter, QLineEdit, QFrame,
                         QPushButton, QMenu, QComboBox, QDialog)
from PyQt4.QtCore import QDate, Qt, SIGNAL

from configuration import Config
from Common.ui.common import (FWidget, IntLineEdit,
                              FormLabel, FormatDate)
from Common.ui.util import is_int, date_to_datetime
from Common.ui.table import FTableWidget
from peewee import fn

# from ui.reports_managers import GReportViewWidget
from GCommon.ui._product_detail import InfoTableWidget
from models import (Store, Product, Reports)


class StockOutputWidget(QDialog, FWidget):

    def __init__(self, store="", table="", parent=0, *args, **kwargs):
        # super(StockInputWidget, self).__init__(parent=parent, *args, **kwargs)
        QDialog.__init__(self, parent, *args, **kwargs)

        title = u"SORTIE"
        self.setWindowTitle("{} {}".format(Config.APP_NAME, title))
        self.setFixedWidth(self.parentWidget().width() - 50)
        self.setFixedHeight(self.parentWidget().height())
        self.parent = parent
        self.store = store
        self.table_p = table
        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout(self)
        editbox = QGridLayout()

        self.date_out = FormatDate(QDate.currentDate())

        # Combobox widget for add store
        self.liste_store = Store.all()

        self.box_store = QComboBox()
        for index in range(0, len(self.liste_store)):
            op = self.liste_store[index]
            self.box_store.addItem(op.name, op.id)
            if self.store and self.store.name == op.name:
                self.box_store.setCurrentIndex(index)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Rechercher un article")
        self.search_field.setMaximumSize(
            200, self.search_field.maximumSize().height())
        self.search_field.textChanged.connect(self.finder)

        self.vline = QFrame()
        self.vline.setFrameShape(QFrame.VLine)
        self.vline.setFrameShadow(QFrame.Sunken)

        self.table_resultat = ResultatTableWidget(parent=self)
        self.table_info = InfoTableWidget(parent=self)
        self.table_out = InproductTableWidget(parent=self)
        self.box_store.connect(self.box_store,
                               SIGNAL("currentIndexChanged(int)"),
                               self.table_out.changed_value)

        self.table_resultat.refresh_("")
        # editbox.addWidget(FormLabel(u"Recherche:"), 0, 0)
        editbox.addWidget(self.search_field, 0, 0)

        editbox.addWidget(self.vline, 0, 2, 1, 1)

        editbox.addWidget(FormLabel(u"Magasin:"), 0, 4)
        editbox.addWidget(self.box_store, 0, 5)
        editbox.addWidget(FormLabel(u"Date de sortie:"), 0, 6)
        editbox.addWidget(self.date_out, 0, 7)

        editbox.setColumnStretch(3, 3)
        splitter = QSplitter(Qt.Horizontal)

        splitter_left = QSplitter(Qt.Vertical)
        # splitter_left.addWidget(FBoxTitle(u"Les products"))
        splitter_left.addWidget(self.table_resultat)

        splitter_down = QSplitter(Qt.Vertical)
        splitter_down.resize(15, 20)
        splitter_down.addWidget(self.table_info)

        splitter_rigth = QSplitter(Qt.Vertical)
        # splitter_rigth.addWidget(FBoxTitle(u"Les products achatés"))
        splitter_rigth.addWidget(self.table_out)
        splitter_rigth.resize(500, 900)

        splitter_left.addWidget(splitter_down)
        splitter.addWidget(splitter_left)
        splitter.addWidget(splitter_rigth)

        hbox.addWidget(splitter)
        vbox.addLayout(editbox)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def finder(self):
        value = str(self.search_field.text())
        self.table_resultat.refresh_(value)

    def save_report(self):
        ''' add operation '''
        # entete de la facture
        self.table_out.changed_value()
        if not self.table_out.isvalid:
            return False
        date_out = str(self.date_out.text())
        datetime_ = date_to_datetime(date_out)
        self.current_store = self.liste_store[self.box_store.currentIndex()]

        values_t = self.table_out.get_table_items()

        for qty, name in values_t:
            rep = Reports(type_=Reports.S, store=self.current_store,
                          date=datetime_, product=Product.get(name=name),
                          qty_use=int(qty))
            try:
                rep.save()
            except:
                self.parent.Notify(
                    u"Ce mouvement n'a pas pu être enrgistré dans les raports",
                    "error")
                return False
        self.table_p.refresh_()
        self.close()
        # self.parent.change_context(GReportViewWidget)
        self.parent.Notify(u"La sortie des articles avec succès", "success")


class ResultatTableWidget(FTableWidget):

    """docstring for ResultatTableWidget"""

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [u"i", u"Resultat", u"Ajouter"]
        self.stretch_columns = [1]
        self.align_map = {1: 'l'}
        # self.display_fixed = True
        # self.display_vheaders = False
        self.refresh_()

    def refresh_(self, value=None):
        """ """
        pw = self.width()
        self.setColumnWidth(0, 20)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, 40)
        self._reset()
        self.set_data_for(value)
        self.refresh()

    def set_data_for(self, value):

        products = [(Product.get(id=rpt.product_id).name) for rpt in
                    Reports.select(fn.Distinct(Reports.product))]
        if value:
            products = [(prod.name) for prod in Product.select(
            ).where(Product.name.contains(value)).where(
                Product.name << products).order_by(Product.name.desc())]
        self.data = [("", rpt, "") for rpt in products]

    def _item_for_data(self, row, column, data, context=None):
        if column == 2:
            return QTableWidgetItem(
                QIcon(u"{img_media}{img}".format(img_media=Config.img_cmedia,
                                                 img="go-next.png")), "")
        if column == 0:
            return QTableWidgetItem(
                QIcon(u"{img_media}{img}".format(img_media=Config.img_cmedia,
                                                 img="info.png")), "")
        return super(ResultatTableWidget, self)._item_for_data(row, column,
                                                               data, context)

    def click_item(self, row, column, *args):
        self.choix = Product.filter(name=self.data[row][1]).get()
        if column != 2:
            self.parent.table_info.refresh_(self.choix.id)
        if column == 2:
            self.parent.table_out.refresh_(self.choix)


class InproductTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = ["Quantité (carton)", "Nombre pièce", "Désignation"]

        # self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

        self.stretch_columns = [0, 1, 2]
        self.align_map = {0: 'r', 1: 'r', 2: 'l'}
        self.display_vheaders = False
        # self.display_fixed = True
        self.refresh_()
        # self.isvalid = True
        self.col_dest = 2
        self.col_qtty = 0

    def refresh_(self, choix=None):
        if choix:
            self.row = [1, choix.number_parts_box, choix.name]
            if not [row for row in self.data if self.row[
                    self.col_dest] in row]:
                self.set_data_for()
                self.refresh()
            self.refresh()

    def set_data_for(self):

        self._reset()
        self.data.extend([self.row])
        self.refresh_()
        pw = self.width() / 4 - 20
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, (pw * 2))

    def popup(self, pos):
        if (len(self.data) - 1) < self.selectionModel().selection().indexes(
        )[0].row():
            return False
        menu = QMenu()
        quit_action = menu.addAction("Supprimer cette ligne")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == quit_action:
            try:
                self.data.pop(self.selectionModel()
                                  .selection().indexes()[0].row())
            except IndexError:
                pass
            if self.data == []:
                self._reset()
            self.refresh()

    def extend_rows(self):
        nb_rows = self.rowCount()

        self.setRowCount(nb_rows + 1)
        bicon = QIcon.fromTheme(
            '', QIcon(u"{img_media}{img}".format(img_media=Config.img_cmedia,
                                                 img='save.png')))
        self.button = QPushButton(bicon, u"Enrgistrer la sortie")
        self.button.released.connect(self.parent.save_report)
        self.setCellWidget(nb_rows, self.col_dest, self.button)

    def _item_for_data(self, row, column, data, context=None):
        if column == 0:
            self.line_edit = IntLineEdit(u"%s" % data)
            self.line_edit.textChanged.connect(self.changed_value)
            return self.line_edit
        return super(InproductTableWidget, self)._item_for_data(
            row, column, data, context)

    def _update_data(self, row_num, new_data):
        self.data[row_num] = (new_data[0], new_data[1], self.data[row_num][2])

    def get_table_items(self):
        """  """
        list_order = []
        for i in range(self.rowCount() - 1):
            liste_item = []
            row_data = self.data[i]
            try:
                liste_item.append(int(row_data[self.col_qtty]))
                liste_item.append(str(row_data[self.col_dest]))
                list_order.append(liste_item)
            except:
                liste_item.append("")

        return list_order

    def changed_value(self, refresh=False):
        """ Calcule les Resultat """
        current_store = self.parent.liste_store[
            self.parent.box_store.currentIndex()]

        self.button.setEnabled(True)
        self.isvalid = True
        for row_num in range(0, self.data.__len__()):
            qtsaisi = is_int(self.cellWidget(row_num, self.col_qtty).text())

            nb_parts_box = Product.filter(
                name=self.item(row_num, self.col_dest).text()).get(
            ).number_parts_box * qtsaisi

            self.setItem(row_num, 1, QTableWidgetItem(
                "{}".format(nb_parts_box)))

            self._update_data(row_num, [qtsaisi, nb_parts_box])

            try:
                last_report = Reports.filter(
                    store=current_store, product__name=str(
                        self.item(row_num, self.col_dest).text())).order_by(
                    Reports.date.desc()).get()
                qtremaining = last_report.remaining
                # date_out = str(self.parent.date_out.text())
                # if last_report.date > date_on_or_end(date_out, on=False):
                #     self.parent.date_out.setStyleSheet("font-size:15px;"
                #                                        "color:red")
                #     self.parent.date_out.setToolTip(
                #         "Cette date est Inférieure à la date de la dernière rapport ({}).".format(last_report.date))
                #     self.isvalid = False
                #     self.button.setEnabled(False)
                # return False

            except Exception as e:
                qtremaining = 0

            viderreur_qtsaisi = ""
            stylerreur = "background-color: rgb(255, 235, 235);" + \
                "border: 3px double SeaGreen"
            if qtsaisi == 0:
                viderreur_qtsaisi = stylerreur
                self.cellWidget(row_num, self.col_qtty).setToolTip(
                    u"obligatoire")
                self.isvalid = False
                self.button.setEnabled(False)

            self.cellWidget(row_num, self.col_qtty).setStyleSheet(
                viderreur_qtsaisi)

            self.cellWidget(row_num, self.col_qtty).setToolTip("")
            if qtremaining < qtsaisi:
                self.cellWidget(row_num, self.col_qtty).setStyleSheet(
                    "font-size:20px; color: red")
                self.cellWidget(
                    row_num, self.col_qtty).setToolTip(
                    u"{} est > {} la quantité restante.".format(
                        qtsaisi, qtremaining))
                self.isvalid = False
                # self.button.setEnabled(False)
