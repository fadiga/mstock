#!usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from PyQt4.QtGui import (
    QVBoxLayout, QHBoxLayout, QLabel, QTableWidgetItem, QDialog,
    QIcon, QGridLayout, QSplitter, QLineEdit, QFrame, QMenu, QPixmap)
from PyQt4.QtCore import QDate, Qt

from configuration import Config
from models import (Store, Product, Invoice, InvoiceItem, Owner)
from Common.ui.common import (FWidget, IntLineEdit, ErrorLabel,
                              FormLabel, FormatDate, Button_menu, ButtonSave)
from Common.ui.util import raise_error, formatted_number, is_int, date_to_datetime
from Common.ui.table import FTableWidget

# from ui.invoice_show import ShowInvoiceViewWidget


class InvoiceAddViewWidgetDialog(QDialog, FWidget):

    def __init__(self, table_p, parent, *args, **kwargs):
        # super(InvoiceAddViewWidgetDialog, self).__init__(parent=parent, *args, **kwargs)
        QDialog.__init__(self, parent, *args, **kwargs)
        title = "Facturation"
        self.setWindowTitle("{} {}".format(Config.APP_NAME, title))
        self.setFixedWidth(self.parentWidget().width() - 10)
        self.setFixedHeight(self.parentWidget().height())

        self.table_p = table_p
        self.parent = parent

        vbox = QVBoxLayout(self)
        hbox = QHBoxLayout(self)
        re_editbox = QGridLayout()
        editbox = QGridLayout()

        self.num_invoice = IntLineEdit("%d" % (Invoice.select().count() + 1))
        self.num_invoice.setToolTip(u"Le numéro de la facture")
        self.num_invoice.setMaximumSize(
            80, 40)
        self.num_invoice_error = ErrorLabel("")
        self.invoice_date = FormatDate(QDate.currentDate())
        self.name_client = QLineEdit()
        # self.name_client.setMaximumSize(
        #     200, self.name_client.maximumSize().height())
        self.name_client.setPlaceholderText("Taper le nom du client")
        self.name_client_error = ErrorLabel("")
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Rechercher un article")
        self.search_field.setMaximumSize(
            500, self.search_field.maximumSize().height())
        self.search_field.textChanged.connect(self.finder)

        self.vline = QFrame()
        self.vline.setFrameShape(QFrame.VLine)
        self.vline.setFrameShadow(QFrame.Sunken)

        self.table_invoice = OrderTableWidget(parent=self)
        self.table_resultat = ResultatTableWidget(parent=self)
        self.table_info = InfoTableWidget(parent=self)

        self.table_resultat.refresh_("")
        # re_editbox.addWidget(FormLabel(u"Recherche:"), 0, 0)
        re_editbox.addWidget(self.search_field, 1, 0)
        re_editbox.setRowStretch(4, 1)
        # re_editbox.addWidget(self.vline, 0, 1, 2, 5)
        # form_ly = QFormLayout()
        # form_ly.addRow(QLabel("Facture N°:"), self.num_invoice)
        # form_ly.addRow(QLabel(u"Doit:"), self.name_client)
        # form = QHBoxLayout()
        editbox.addWidget(FormLabel(u"Facture N°:"), 0, 2)
        editbox.addWidget(self.num_invoice, 0, 3)
        editbox.addWidget(self.num_invoice_error, 0, 4)
        editbox.addWidget(FormLabel(u"Doit:"), 1, 2)
        editbox.addWidget(self.name_client, 1, 3)
        editbox.addWidget(self.name_client_error, 1, 4)
        editbox.addWidget(FormLabel(u"Date:"), 0, 5)
        editbox.addWidget(self.invoice_date, 0, 6)
        # form.addLayout(editbox)

        splitter = QSplitter(Qt.Horizontal)
        splitter_inv = QSplitter(Qt.Horizontal)

        splitter_left = QSplitter(Qt.Vertical)
        splitter_down = QSplitter(Qt.Vertical)
        splitter_left.setLayout(re_editbox)
        splitter_left.addWidget(self.table_resultat)
        # splitter_down.resize(15, 20)
        splitter_down.addWidget(self.table_info)
        splitter_rigth = QSplitter(Qt.Vertical)
        splitter_inv.setLayout(editbox)
        splitter_rigth.addWidget(splitter_inv)
        splitter_rigth.addWidget(self.table_invoice)

        splitter_left.addWidget(splitter_down)
        splitter.addWidget(splitter_left)
        splitter.addWidget(splitter_rigth)

        hbox.addWidget(splitter)
        # vbox.addLayout(editbox)
        vbox.addLayout(hbox)
        self.setLayout(vbox)

    def finder(self):
        completion_values = []
        search_term = self.search_field.text()
        # try:
        #     products = Product.select().where(Product.name.icontains(search_term))
        # except ValueError:
        #     pass
        # for product in products:
        #     last_r = product.last_report_by_prod()
        #     try:
        #         completion_values.append(last_r.product.__str__())
        #     except:
        #         pass
        # completer = QCompleter(completion_values, parent=self)
        # completer.setCaseSensitivity(Qt.CaseInsensitive)
        # completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)

        # self.search_field.setCompleter(completer)
        self.table_resultat.refresh_(search_term)

    def save_b(self):
        ''' add operation '''
        # entete de la facture
        if not self.table_invoice.isvalid:
            return False
        try:
            num_invoice = int(self.num_invoice.text())
            self.num_invoice_error.setText(u"")
        except:
            self.pixmap = QPixmap(u"{img_media}{img}".format(img_media=Config.img_media,
                                                             img="warning.png"))
            self.num_invoice.setStyleSheet(
                "background-color:  rgb(255, 235, 235);")
            self.num_invoice_error.setToolTip(
                u"Le numero de facture est obligatoire.")
            self.num_invoice_error.setPixmap(self.pixmap)
        invoice_date = str(self.invoice_date.text())
        name_client = str(self.name_client.text())
        datetime_ = date_to_datetime(invoice_date)

        values_t = self.table_invoice.get_table_items()
        if name_client == "":
            self.name_client.setStyleSheet(
                "background-color: rgb(255, 235, 235);")
            self.pixmap = QPixmap(u"{img_media}{img}".format(img_media=Config.img_media,
                                                             img="decline.png"))
            self.name_client_error.setToolTip(
                u"Nom du client est obligatoire.")
            self.name_client_error.setPixmap(self.pixmap)
            return False
        # if num_invoice > Config.credit:
        #     raise_error(("Avertisement"), u"<h2>Veuillez payer la reste de la licence</h2>")
        #     return False
        invoice = Invoice()
        try:
            invoice.owner = Owner.get(islog=True)
        except:
            if Config.DEBUG:
                invoice.owner = Owner.get(username='root')
            else:
                return False

        invoice.number = num_invoice
        invoice.date_ord = datetime_
        invoice.client = name_client.capitalize()
        invoice.location = "Bamako"
        invoice.type_ = "Facture"
        invoice.subject = ""
        invoice.tax = False
        invoice.otax_rate = 18
        try:
            invoice.save()
        except:
            raise_error(
                "Erreur", u"Impossible d'enregistrer l'entête de la facture")
            return False

        # Save orderitems
        try:
            order = Invoice.get(number=num_invoice)
        except:
            return False
        for i in values_t:
            qty, name, price = i
            description = Product.filter(name=name).get()
            item = InvoiceItem()
            item.invoices = invoice.id
            item.quantity = int(i[0])
            item.description = description
            item.detailed = int(i[2])
            item.price = int(i[3])
            try:
                item.save()
                self.name_client.clear()
                self.num_invoice.clear()
            except Exception as e:
                print(e)
                invoice.delete_instance()
                raise_error("Erreur", u"Ce mouvement n'a pas pu etre "
                                      u"enregistré dans les rapports")
                return False

        self.close()
        self.table_p.refresh_()
        # self.change_main_context(ShowInvoiceViewWidget, table_p=self,
        #                          invoice=invoice)


class ResultatTableWidget(FTableWidget):
    """docstring for ResultatTableWidget"""

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [u"info", u"Resultat", u"Ajouter"]
        self.stretch_columns = [1]
        self.align_map = {1: 'l'}
        # self.display_fixed = True
        self.refresh_()

    def refresh_(self, value=None):
        """ """

        self._reset()
        self.set_data_for(value)
        self.refresh()

        pw = self.width()
        self.setColumnWidth(0, 20)
        self.setColumnWidth(1, pw)
        self.setColumnWidth(2, 60)

    def set_data_for(self, prod_find):

        products = Product.select().order_by(Product.name.asc())
        if prod_find:
            products = products.where(Product.name.contains(prod_find))

        self.data = [("", prod.name, "") for prod in products]

    def _item_for_data(self, row, column, data, context=None):
        if column == 2:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(
                img_media=Config.img_cmedia, img="go-next.png")), "")
        if column == 0:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(
                img_media=Config.img_cmedia, img="info.png")), "")
        return super(ResultatTableWidget, self)._item_for_data(row, column,
                                                               data, context)

    def click_item(self, row, column, *args):
        if column != 2:
            self.choix = Product.filter(name=self.data[row][1]).get()
            self.parent.table_info.refresh_(self.choix.id)
        if column == 2:
            # self.removeRow(row)
            self.choix = Product.filter(name=self.data[row][1]).get()
            self.parent.table_invoice.refresh_(self.choix)


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
        self.name.setText(
            u"<h6>{name}</h6>".format(name=self.prod.name.title()))
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
        from ui.show_image import ShowImageViewWidget
        try:
            self.parent.open_dialog(
                ShowImageViewWidget, modal=True, prod=self.prod)
        except AttributeError:
            pass


class OrderTableWidget(FTableWidget):

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent
        self.pparent = parent.parent
        self.hheaders = [u"Quantité", u"produit vendu", u"Détaille", u"Prix Unitaire",
                         u"Montant"]

        # self.setSelectionMode(QAbstractItemView.NoSelection)
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)

        self.stretch_columns = [1]
        self.align_map = {3: 'r'}
        self.display_vheaders = False
        self.display_fixed = True
        self.refresh_(choix=None)
        self.isvalid = False

    def refresh_(self, choix):

        if choix:
            self.row = [0, u"%s" % choix.name, "", 0, 0]
        else:
            return
        if not [row for row in self.data if self.row[1] in row]:
            self._reset()
            self.set_data_for()
            self.refresh()

    def set_data_for(self):
        print(self.row)
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
        self.setSpan(nb_rows, 0, 1, 3)
        self.setItem(nb_rows, 3, QTableWidgetItem(u"Montant"))
        monttc = QTableWidgetItem(formatted_number(u"%d" % 0))
        monttc.setTextAlignment(Qt.AlignRight)
        self.setItem(nb_rows, 4, monttc)

        nb_rows += 1
        self.setRowCount(nb_rows + 1)
        self.setSpan(nb_rows, 0, 1, 4)
        self.button = ButtonSave(u"Enregistrer")
        self.button.released.connect(self.parent.save_b)
        self.setCellWidget(nb_rows, 4, self.button)

        pw = (self.parentWidget().width()) / 8
        # self.setColumnWidth(0, pw)
        self.setColumnWidth(1, pw * 2)
        self.setColumnWidth(2, pw * 3)
        self.setColumnWidth(3, pw * 1.5)
        # self.setColumnWidth(3, pw)

    # def add_row(self):
    #     pass

    def _item_for_data(self, row, column, data, context=None):
        if column in [0, 2, 3]:
            self.line_edit = IntLineEdit()
            # self.line_edit.clear()
            self.line_edit.textChanged.connect(self.changed_value)
            return self.line_edit
        return super(OrderTableWidget, self)._item_for_data(
            row, column, data, context)

    def _update_data(self, row_num, new_data):
        self.data[row_num] = (new_data[0], new_data[1], self.data[row_num][2])

    def get_table_items(self):
        """ Recupère les elements du tableau """
        list_invoice = []
        for i in range(self.rowCount() - 1):
            liste_item = []
            try:
                liste_item.append(str(self.cellWidget(i, 0).text()))
                liste_item.append(str(self.item(i, 1).text()))
                liste_item.append(str(self.cellWidget(i, 2).text()))
                liste_item.append(str(self.cellWidget(i, 3).text()))
                list_invoice.append(liste_item)
            except:
                liste_item.append("")

        return list_invoice

    def changed_value(self, refresh=False):
        """ Calcule les Resultat """
        mtt_ht = 0
        for row_num in range(0, self.data.__len__()):
            last_report = Product.filter(name=str(self.item(row_num, 1)
                                                  .text())).get().last_report
            try:
                qtremaining = last_report.remaining
            except AttributeError:
                qtremaining = 0

            qtsaisi = is_int(self.cellWidget(row_num, 0).text())
            detaille = is_int(self.cellWidget(row_num, 2).text())
            pu = is_int(self.cellWidget(row_num, 3).text())

            self.isvalid = True
            viderreur_qtsaisi = ""
            viderreur_pu = ""
            stylerreur = "background-color: rgb(255, 235, 235);" + \
                         "border: 3px double SeaGreen"
            if qtsaisi == 0:
                viderreur_qtsaisi = stylerreur
                self.cellWidget(row_num, 0).setToolTip(u"obligatoire")
                self.isvalid = False
            if pu == 0:
                viderreur_pu = stylerreur
                self.cellWidget(row_num, 0).setToolTip(u"obligatoire")
                self.isvalid = False

            self.cellWidget(row_num, 0).setStyleSheet(viderreur_qtsaisi)
            self.cellWidget(row_num, 3).setStyleSheet(viderreur_pu)

            self.cellWidget(row_num, 0).setToolTip("")
            if qtremaining < qtsaisi:
                self.cellWidget(row_num, 0).setStyleSheet("font-size:20px;"
                                                          " color: red")
                self.cellWidget(
                    row_num, 0).setToolTip(
                    u"%s est > %s (stock remaining)" % (qtsaisi, qtremaining))
                # self.isvalid = False
                # return False
            ui_item = (qtsaisi * pu)
            mtt_ht += ui_item
            montt = QTableWidgetItem(formatted_number(ui_item))
            montt.setTextAlignment(Qt.AlignRight)
            self._update_data(row_num, [qtsaisi, detaille, pu, mtt_ht])
            self.setItem(row_num, 4, montt)
        monttc = QTableWidgetItem(formatted_number(mtt_ht))
        monttc.setTextAlignment(Qt.AlignRight)
        self.setItem(row_num + 1, 4, monttc)
