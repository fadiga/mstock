#!usr/bin/env python
# -*- coding: utf-8 -*-
#maintainer: Fad

from PyQt4.QtGui import (QVBoxLayout, QHBoxLayout, QLabel, QTableWidgetItem,
                         QIcon, QGridLayout, QSplitter, QLineEdit, QFrame,
                         QMenu, QCompleter, QComboBox, QPushButton)
from PyQt4.QtCore import QDate, Qt, QVariant

from configuration import Config
from models import (Store, Product, Reports)

from Common import notification
from Common.ui.common import (FWidget, IntLineEdit, FormLabel, FormatDate,
                              Button_menu, Button, Button_save)
from Common.ui.util import raise_error, is_int, date_to_datetime
from Common.ui.table import FTableWidget
from ui.reports_managers import GReportViewWidget


class StockInputWidget(FWidget):

    def __init__(self, product="", parent=0, *args, **kwargs):
        super(StockInputWidget, self).__init__(parent=parent, *args, **kwargs)
        title = u"   Rapports d'entrée dans le magasin"
        self.parentWidget().setWindowTitle(Config.NAME_ORGA +
                                           title)
        Config.logging.info(title)
        self.parent = parent

        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout(self)
        editbox = QGridLayout()

        # vbox.addWidget(FPageTitle(u"Entrée"))

        self.date = FormatDate(QDate.currentDate())

        #Combobox widget for add store
        self.liste_store = Store.all()

        self.box_mag = QComboBox()
        for index in range(0, len(self.liste_store)):
            op = self.liste_store[index]
            sentence = u"%(name)s" % {'name': op.name}
            self.box_mag.addItem(sentence, op.id)

        self.search_field = QLineEdit()
        self.search_field.setToolTip("Rechercher un produit")
        self.search_field.setMaximumSize(200,
                                         self.search_field.maximumSize().height())
        self.search_field.textChanged.connect(self.finder)

        self.add_prod = Button(u"Nouveau produit")
        self.add_prod.setIcon(QIcon.fromTheme('document-new',
                                              QIcon(u"{img_media}{img}".format(img_media=Config.img_media,
                                                      img='product_add.png'))))
        self.add_prod.clicked.connect(self.add_product)

        self.vline = QFrame()
        self.vline.setFrameShape(QFrame.VLine)
        self.vline.setFrameShadow(QFrame.Sunken)

        self.table_resultat = ResultatTableWidget(parent=self)
        self.table_info = InfoTableWidget(parent=self)
        self.table_in = InputTableWidget(parent=self)

        self.table_resultat.refresh_()
        editbox.addWidget(FormLabel(u"Recherche:"), 0, 0)
        editbox.addWidget(self.search_field, 0, 1)

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
        from GCommon.ui.product_edit_or_add import EditOrAddProductsDialog

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
        date = str(self.date.text())
        datetime_ = date_to_datetime(date)
        store = self.liste_store[self.box_mag.currentIndex()]
        values_t = self.table_in.get_table_items()

        for ligne in values_t:
            qty, name = ligne
            product = Product.select().where(Product.name==name).get()

            rep = Reports(orders=None, type_=Reports.E, store=store,
                          date=datetime_, product=product,
                          qty_use=int(qty))
            try:
                rep.save()
            except:
                raise
                raise_error("Error", u"Ce mouvement n'a pas pu être "
                                     u"enrgistré dans les raports")
                return False

        self.parent.change_context(GReportViewWidget)
        self.parent.Notify("L'entrée des articles avec succès")


class ResultatTableWidget(FTableWidget):
    """docstring for ResultatTableWidget"""
    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent
        self.hheaders = ["i", u"Produits", u"Ajouter"]
        self.stretch_columns = [1]
        self.align_map = {1: 'l', 2: 'r'}
        self.display_fixed = True
        self.refresh_()

    def refresh_(self, value=None):

        self._reset()
        self.set_data_for(value)
        self.refresh()

        pw = 100
        self.setColumnWidth(0, 20)
        self.setColumnWidth(1, pw * 2)
        self.setColumnWidth(2, pw)

    def set_data_for(self, prod_find):

        products = Product.select().order_by(Product.name.asc())
        if prod_find:
            products = products.where(Product.name.contains(prod_find))

        self.data = [("", prod.name, "") for prod in products]

    def _item_for_data(self, row, column, data, context=None):
        if column == 2:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(img_media=Config.img_cmedia,
                                                      img="go-next.png")), "Ajouter")
        if column == 0:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(img_media=Config.img_cmedia,
                                                      img="info.png")), "")
        return super(ResultatTableWidget, self)._item_for_data(row, column,
                                                               data, context)

    def click_item(self, row, column, *args):
        self.choix = Product.filter(name=self.data[row][1]).get()
        if column != 2:
            self.parent.table_info.refresh_(self.choix.id)
        if column == 2:
            self.parent.table_in.refresh_(self.choix)


class InfoTableWidget(FWidget):

    def __init__(self, parent, *args, **kwargs):
        super(FWidget, self).__init__(parent=parent, *args, **kwargs)

        self.parent = parent

        self.refresh()
        self.store = QLabel(" ")

        self.nameLabel = QLabel("")
        self.name = QLabel(" ")
        self.stock_remaining = QLabel(" ")
        self.imagelabel = QLabel("")
        self.image = Button_menu("")
        self.image.clicked.connect(self.chow_image)

        gridbox = QGridLayout()
        gridbox.addWidget(self.nameLabel, 1, 0)
        gridbox.addWidget(self.name, 1, 1)
        # gridbox.addWidget(self.store, 0, 1)
        gridbox.addWidget(self.store, 4, 0, 1, 2)
        gridbox.addWidget(self.imagelabel, 5, 0, 1, 5)
        hbox = QHBoxLayout()
        hbox.addWidget(self.image)

        vbox = QVBoxLayout()
        vbox.addLayout(gridbox)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def refresh_(self, idd):

        self.prod = Product.get(id=idd)
        self.nameLabel.setText((u"<h4>Article:</h4>"))
        self.name.setText(u"<h6>{name}</h6>".format(name=self.prod.name.title()))
        rest_by_store = ""

        for store in Store.select():
            remaining, nbr_parts = store.get_remaining_and_nb_parts(self.prod)

            if remaining < 10:
                color_style = 'color: DarkGreen'
            if remaining <= 5:
                color_style = 'color: LightCoral'
            if remaining <= 2:
                color_style = 'color: red; text-decoration: blink'
            if remaining >= 10:
                color_style = 'color: LimeGreen;'
            color_style = color_style + "; border:3px solid green; font-size: 15px"

            rest_by_store += u"<div> {store}: <strong style='{color_style}'>" \
                             u" {remaining} </strong> ({nbr_parts} pièces)"\
                             u"</div>".format(store=store.name,
                                              color_style=color_style,
                                              remaining=remaining,
                                              nbr_parts=nbr_parts)

        self.store.setText(u"<h4><u>Quantité restante</u>:</h4> \
                           {remaining}</ul>".format(remaining=rest_by_store))

        self.imagelabel.setText(u"<b>Pas d'image<b>")
        self.image.setStyleSheet("")
        if self.prod.image_link:
            self.imagelabel.setText(u"<b><u>Image</u></b>")
            self.image.setStyleSheet("background: url({image})"
                                     " no-repeat scroll 20px 110px #CCCCCC;"
                                     "width: 55px".format(image=self.prod.image_link))

    def chow_image(self):
        """ doit afficher l'image complete dans une autre fenetre"""
        from GCommon.ui.show_image import ShowImageViewWidget
        try:
            self.parent.open_dialog(ShowImageViewWidget, modal=True, prod=self.prod)
        except AttributeError:
            pass


class InputTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)
        self.parent = parent

        self.hheaders = [u"Quantité (en carton)", u"Désignation"]
        # self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

        self.stretch_columns = [0, 1]
        self.align_map = {1: 'l', 0: 'r'}
        self.display_vheaders = False
        self.display_fixed = True
        self.refresh_()
        self.isvalid = True

    def refresh_(self, choix=None):
        if choix:
            self.row = [1, u"%s" % choix.name]
            if not [row for row in self.data if self.row[1] in row]:
                self.set_data_for()
                self.refresh()

    def set_data_for(self):

        self._reset()
        self.data.extend([self.row])
        self.refresh()

    def popup(self, pos):
        if (len(self.data) - 1) < self.selectionModel().selection().indexes()[0].row():
            return False
        menu = QMenu()
        quitAction = menu.addAction("Supprimer cette ligne")
        action = menu.exec_(self.mapToGlobal(pos))
        if action == quitAction:
            try:
                self.data.pop(self.selectionModel()
                                  .selection().indexes()[0].row())
            except IndexError:
                pass
            self.refresh()

    def extend_rows(self):
        nb_rows = self.rowCount()

        self.setRowCount(nb_rows + 1)
        self.setSpan(nb_rows, 0, 1, 1)

        self.button = Button_save(u"Enrgistrer l'entrée")
        self.button.released.connect(self.parent.save_b)
        self.setCellWidget(nb_rows, 1, self.button)

        pw = (self.parentWidget().width()) / 3
        self.setColumnWidth(0, pw)
        self.setColumnWidth(1, (pw * 2) - 2)

    def _item_for_data(self, row, column, data, context=None):
        if column != 1 and column != 3:
            self.line_edit = IntLineEdit(u"%s" % data)
            self.line_edit.textChanged.connect(self.changed_value)
            return self.line_edit
        return super(InputTableWidget, self)._item_for_data(row,
                                                                column, data,
                                                                context)

    def _update_data(self, row_num, new_data):
        self.data[row_num] = (new_data[0], self.data[row_num][1], new_data[0])

    def get_table_items(self):
        """  """
        list_stock_input = []
        for i in range(self.rowCount() - 1):
            liste_item = []
            row_data = self.data[i]
            try:
                liste_item.append(int(row_data[0]))
                liste_item.append(str(row_data[1]))
                list_stock_input.append(liste_item)
            except Exception as e:
                print(e)
                liste_item.append("")

        return list_stock_input

    def changed_value(self, refresh=False):
        """ Calcule les Resultat """
        for row_num in xrange(0, self.data.__len__()):

            qtsaisi = is_int(self.cellWidget(row_num, 0).text())
            self.isvalid = True
            viderreur_qtsaisi = ""
            stylerreur = "background-color: rgb(255, 235, 235);border: 3px double SeaGreen"
            if qtsaisi == 0:
                viderreur_qtsaisi = stylerreur
                self.cellWidget(row_num, 0).setToolTip(u"La quantité est obligatoire")
                self.isvalid = False

            self.cellWidget(row_num, 0).setStyleSheet(viderreur_qtsaisi)

            self.cellWidget(row_num, 0).setToolTip("")
            self._update_data(row_num, [qtsaisi])
