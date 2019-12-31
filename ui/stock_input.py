#!usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from datetime import date
from PyQt4.QtGui import (QVBoxLayout, QHBoxLayout, QTableWidgetItem,
                         QMessageBox, QIcon, QGridLayout, QSplitter, QLineEdit, QFrame,
                         QMenu, QComboBox, QPushButton, QDialog)
from PyQt4.QtCore import QDate, Qt

from configuration import Config
from models import (Store, Product, Reports)

from Common.ui.common import(FWidget, IntLineEdit, FormLabel, FormatDate, Button)
from Common.ui.util import is_int, date_to_datetime, formatted_number
from Common.ui.table import FTableWidget

from ui.product_detail import InfoTableWidget


class StockInputWidget(QDialog, FWidget):

    def __init__(self, store="", table="", parent=0, *args, **kwargs):
        # super(StockInputWidget, self).__init__(parent=parent, *args, **kwargs)
        QDialog.__init__(self, parent, *args, **kwargs)

        title = u"   ENTREE STOCK"
        self.setWindowTitle("{} {}".format(Config.APP_NAME, title))
        # Config.logging.info(title)
        self.setFixedWidth(self.parentWidget().width() - 50)
        self.setFixedHeight(self.parentWidget().height())
        self.parent = parent
        self.store = store
        self.table_p = table
        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout(self)
        editbox = QGridLayout()

        self.date = FormatDate(QDate.currentDate())

        self.liste_store = Store.all()

        self.box_mag = QComboBox()
        for index in range(0, len(self.liste_store)):
            op = self.liste_store[index]
            self.box_mag.addItem(op.name, op.id)

            if self.store and self.store.name == op.name:
                self.box_mag.setCurrentIndex(index)

        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Rechercher un article")
        self.search_field.setMaximumSize(
            200, self.search_field.maximumSize().height())
        self.search_field.textChanged.connect(self.finder)

        self.add_prod = Button(u"+ &Article")
        self.add_prod.clicked.connect(self.add_product)

        self.vline = QFrame()
        self.vline.setFrameShape(QFrame.VLine)
        self.vline.setFrameShadow(QFrame.Sunken)

        self.table_resultat = ResultatTableWidget(parent=self)
        self.table_info = InfoTableWidget(parent=self)
        self.table_in = InputTableWidget(parent=self)

        self.table_resultat.refresh_()
        editbox.addWidget(self.search_field, 0, 0)

        editbox.addWidget(self.vline, 0, 2, 1, 1)

        editbox.addWidget(FormLabel(u"Magasin:"), 0, 4)
        editbox.addWidget(self.box_mag, 0, 5)
        editbox.addWidget(FormLabel(u"Date d'entrée:"), 0, 6)
        editbox.addWidget(self.date, 0, 7)

        editbox.setColumnStretch(3, 3)
        splitter = QSplitter(Qt.Horizontal)
        # splitter.setFrameShape(QFrame.StyledPanel)

        splitter_left = QSplitter(Qt.Vertical)
        # splitter_left.addWidget(FBoxTitle(u"Les products"))
        splitter_left.addWidget(self.table_resultat)

        splitter_down = QSplitter(Qt.Vertical)
        splitter_down.resize(15, 20)
        splitter_down.addWidget(self.table_info)
        splitter_down.addWidget(self.add_prod)

        splitter_rigth = QSplitter(Qt.Vertical)
        # splitter_rigth.addWidget(FBoxTitle(u"Les products achatés"))
        splitter_rigth.addWidget(self.table_in)
        splitter_rigth.resize(500, 900)

        splitter_left.addWidget(splitter_down)
        splitter.addWidget(splitter_left)
        splitter.addWidget(splitter_rigth)

        hbox.addWidget(splitter)
        vbox.addLayout(editbox)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def add_product(self):
        """ """
        from ui.product_edit_or_add import EditOrAddProductsDialog

        self.open_dialog(EditOrAddProductsDialog, modal=True,
                         product=None, table_p=self.table_resultat)

    def finder(self):
        value = str(self.search_field.text())
        self.table_resultat.refresh_(value)

    def save_b(self):
        ''' add operation '''
        # entete de la facture
        if not self.table_in.isvalid:
            return False

        datetime_ = date_to_datetime(str(self.date.text()))
        store = self.liste_store[self.box_mag.currentIndex()]
        values_t = self.table_in.get_table_items()

        for qty, name in values_t:
            product = Product.select().where(Product.name == name).get()

            rep = Reports(orders=None, type_=Reports.E, store=store,
                          date=datetime_, product=product, qty_use=int(qty))
            try:
                rep_p = Reports.select().where(
                    Reports.product == product, Reports.type_ == Reports.E,
                    Reports.store == store,
                    Reports.qty_use == int(qty)).get()
            except:
                rep_p = False
            if rep_p and date.today() == datetime_.date():
                print("if duplicate_record")
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setWindowTitle("Alerte doublon")
                msg.setText(
                    "{qty} {prod} a été rentré aujourd'hui ({date}) à {time_} dans le magasin {mag}".format(
                        date=datetime_.strftime("%d/%m/%Y"), prod=rep_p.product.name, time_=rep_p.date.strftime("%H: %M"), mag=rep_p.store, qty=rep_p.qty_use))
                msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
                if msg.exec_() == QMessageBox.Cancel:
                    print("Pas accepter")
                    return False
                # if msg.exec_() == QMessageBox.YesAll:
                #     yes_all = True

            try:
                rep.save()
            except:
                self.parent.Notify(
                    "Ce mouvement n'a pas pu être enrgistré dans les raports", "error")
                return False

        # self.table_p.refresh_()
        self.close()
        self.parent.Notify(u"L'entrée des articles avec succès", "success")


class ResultatTableWidget(FTableWidget):

    """docstring for ResultatTableWidget"""

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent
        self.hheaders = ["i", u"Produits", u"Ajouter"]
        self.stretch_columns = [1]
        self.align_map = {1: 'l', 2: 'r'}
        # self.display_fixed = True
        self.refresh_()

    def refresh_(self, value=None):

        self._reset()
        self.set_data_for(value)
        self.refresh()

        pw = self.width()
        self.setColumnWidth(0, 20)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, 40)

    def set_data_for(self, prod_find):

        products = Product.select().order_by(Product.name.asc())
        if prod_find:
            products = products.where(Product.name.contains(prod_find))

        self.data = [("", prod.name, "") for prod in products]

    def _item_for_data(self, row, column, data, context=None):
        if column == 2:
            return QTableWidgetItem(QIcon(
                u"{img_media}{img}".format(img_media=Config.img_cmedia,
                                           img="go-next.png")), "")
        if column == 0:
            return QTableWidgetItem(QIcon(
                u"{img_media}{img}".format(img_media=Config.img_cmedia,
                                           img="info.png")), "")
        return super(ResultatTableWidget, self)._item_for_data(row, column,
                                                               data, context)

    def click_item(self, row, column, *args):
        self.choix = Product.filter(name=self.data[row][-2]).get()
        if column != 2:
            self.parent.table_info.refresh_(self.choix.id)
        if column == 2:
            self.parent.table_in.refresh_(self.choix)


class InputTableWidget(FTableWidget):

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
        self.isvalid = True
        self.col_dest = 2
        self.col_qtty = 0

    def refresh_(self, choix=None):
        if choix:
            self.row = [1, choix.number_parts_box, u"%s" % choix.name]
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
                self.refresh_()
            except IndexError:
                pass
            if self.data == []:
                self._reset()
            self.refresh()

    def extend_rows(self):
        nb_rows = self.rowCount()

        self.setRowCount(nb_rows + 1)
        # self.setSpan(nb_rows, 0, 1, 1)
        bicon = QIcon.fromTheme(
            '', QIcon(u"{img_media}{img}".format(img_media=Config.img_cmedia,
                                                 img='save.png')))
        self.button = QPushButton(bicon, u"Enrgistrer l'entrée")
        self.button.released.connect(self.parent.save_b)
        self.setCellWidget(nb_rows, self.col_dest, self.button)

    def _item_for_data(self, row, column, data, context=None):
        if column == 0:
            self.line_edit = IntLineEdit(u"%s" % data)
            self.line_edit.textChanged.connect(self.changed_value)
            return self.line_edit
        return super(InputTableWidget, self)._item_for_data(
            row, column, data, context)

    def _update_data(self, row_num, new_data):
        self.data[row_num] = (new_data[0], new_data[1], self.data[row_num][2])

    def get_table_items(self):
        list_stock_input = []
        for i in range(self.rowCount() - 1):
            liste_item = []
            row_data = self.data[i]
            try:
                liste_item.append(int(row_data[self.col_qtty]))
                liste_item.append(str(row_data[self.col_dest]))
                list_stock_input.append(liste_item)
            except Exception as e:
                liste_item.append("")

        return list_stock_input

    def changed_value(self, refresh=False):
        """ Calcule les Resultat """
        self.isvalid = True
        for row_num in range(0, self.data.__len__()):

            qtsaisi = is_int(self.cellWidget(row_num, self.col_qtty).text())
            # col_dest = is_int(self.cellWidget(row_num, self.col_dest).text())
            # designation = self.item(row_num, self.col_dest).text()

            nb_parts_box = Product.filter(name=self.item(
                row_num, self.col_dest).text()).get(
            ).number_parts_box * qtsaisi

            viderreur_qtsaisi = ""
            if qtsaisi == 0:
                viderreur_qtsaisi = "background-color: rgb(255, 235, 235);border: 3px double SeaGreen"
                self.cellWidget(row_num, 0).setToolTip(
                    u"La quantité est obligatoire")
            #     self.isvalid = False
            # duplicate_record = ""
            # prod = str(designation)
            # # qty_use = ""

            # repts = Reports.select().where(
            #     Reports.qty_use == qtsaisi, Reports.store == self.parent.store, Reports.product == prod).get()
            # print(repts)
            # if not repts:
            #     duplicate_record = "background-color: rgb(255, 235, 235);border: 3px double SeaGreen"
            #     self.cellWidget(row_num, 0).setToolTip(u"Alert doublons")
            #     self.isvalid = False

            # self.cellWidget(row_num, 0).setStyleSheet(duplicate_record)
            self.cellWidget(row_num, 0).setStyleSheet(viderreur_qtsaisi)
            self.cellWidget(row_num, 0).setToolTip("")
            self._update_data(row_num, [qtsaisi, nb_parts_box])

            nb_parts_box = QTableWidgetItem(
                formatted_number(u"%d" % nb_parts_box))
            nb_parts_box.setTextAlignment(Qt.AlignRight)
            self.setItem(row_num, 1, nb_parts_box)
