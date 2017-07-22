#!usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fadiga

from datetime import date
from PyQt4.QtCore import Qt, QDate
from PyQt4.QtGui import (QVBoxLayout, QGridLayout, QTableWidgetItem,
                         QIcon, QMenu)

from configuration import Config
from models import Reports, Store
from Common.ui.common import (FWidget, FPageTitle, FormatDate, Button,
                              FormLabel)
from Common.ui.table import FTableWidget
from Common.ui.util import (
    formatted_number, raise_error, date_on_or_end, show_date)


class GReportViewWidget(FWidget):

    def __init__(self, parent=0, *args, **kwargs):
        super(GReportViewWidget, self).__init__(parent=parent,
                                                *args, **kwargs)
        self.parentWidget().setWindowTitle(Config.NAME_ORGA +
                                           u"    GESTION DES RAPPORTS")
        self.parent = parent
        self.title = u"Tous les mouvements"
        tablebox = QVBoxLayout()
        self.on_date = FormatDate(QDate(date.today().year, 1, 1))
        self.end_date = FormatDate(QDate.currentDate())
        self.Button = Button(u"OK")
        self.Button.clicked.connect(self.refresh_)
        self.table_op = GReportTableWidget(parent=self)
        tablebox.addWidget(self.table_op)

        vbox = QVBoxLayout()
        # Grid
        gridbox = QGridLayout()
        gridbox.addWidget(FormLabel("Debut"), 0, 2)
        gridbox.addWidget(self.on_date, 0, 3)
        gridbox.addWidget(FormLabel("Fin"), 0, 4)
        gridbox.addWidget(self.end_date, 0, 5)
        gridbox.addWidget(self.Button, 0, 6)
        gridbox.setColumnStretch(7, 5)
        self.text_format = "Les mouvements du {} au {}"
        self.period_label = FPageTitle(self.text_format.format(
            show_date(self.on_date.text(), time=False),
            show_date(self.end_date.text(), time=False)))
        self.refresh_()

        vbox = QVBoxLayout()
        vbox.addWidget(self.period_label)
        # vbox.addWidget(FormLabel(period))
        vbox.addLayout(gridbox)
        vbox.addLayout(tablebox)
        self.setLayout(vbox)

    def refresh_(self):
        self.table_op.refresh_()
        self.period_label.setText(self.text_format.format(
            show_date(self.on_date.text(), time=False),
            show_date(self.end_date.text(), time=False)))


class GReportTableWidget(FTableWidget):

    """ """

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [u" ", u"Magasin", u"Produit", u"Quantité utilisé",
                         u"Restante", u"Date", u""]
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)
        self.setMouseTracking(True)
        self.current_hover = [0, 0]
        # self.cellEntered.connect(self.cellHover)

        self.stretch_columns = [1, 2, 5]
        self.align_map = {0: 'l', 1: "l", 2: "l", 3: "r", 4: "r"}
        self.ecart = 144
        self.display_vheaders = False
        self.refresh_()

    def refresh_(self):
        """ """

        self._reset()
        self.set_data_for()
        self.refresh()
        # je cache la 7 eme colonne
        self.hideColumn(6)
        self.setColumnWidth(0, 40)

    def set_data_for(self):

        on = date_on_or_end(self.parent.on_date.text()),
        end = date_on_or_end(self.parent.end_date.text(), on=False)

        self.data = [(rap.type_, rap.store.name, rap.product,
                      formatted_number(rap.qty_use),
                      formatted_number(rap.remaining),
                      show_date(rap.date), rap.id)
                     for rap in Reports.filter(
            deleted=False, date__gte=on, date__lte=end).order_by(
            Reports.date.desc(), Reports.store.desc(), Reports.product.desc())]

    def _item_for_data(self, row, column, data, context=None):
        if column == 0 and self.data[row][0] == Reports.E:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(
                img_media=Config.img_media, img="in.png")), u"")
        if column == 0 and self.data[row][0] == Reports.S:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(
                img_media=Config.img_media, img="out.png")), u"")

        return super(GReportTableWidget, self)._item_for_data(row, column,
                                                              data, context)

    def popup(self, pos):
        row = self.selectionModel().selection().indexes()[0].row()
        if (len(self.data) - 1) < row:
            return False

        # self.report = Reports.filter(id=self.data[row][6]).get()
        self.report = Reports.select().where(
            Reports.id == self.data[row][6]).get()
        menu = QMenu()
        delaction = menu.addAction(
            QIcon("{}del.png".format(Config.img_cmedia)), "supprimer")
        editaction = menu.addAction(
            QIcon("{}edit.png".format(Config.img_cmedia)), "Modifier")

        select = Store.select().where(Store.name == self.data[row][1])
        addgroup = menu.addMenu(u"Transfert")
        # # Ajout au groupe
        lt_grp_select = [(i.name) for i in select]
        [addgroup.addAction("{}".format(grp.name),
                            lambda grp=grp: self.transfer(
                                grp, self.data[row][-1]))
         for grp in Store.select() if not grp.name in lt_grp_select]
        action = menu.exec_(self.mapToGlobal(pos))

        if action == editaction:
            from ui.report_edit import EditReportViewWidget
            self.parent.open_dialog(
                EditReportViewWidget, modal=True, report=self.report,
                table_p=self.parent.table_op)
        if action == delaction:
            from ui.deleteview import DeleteViewWidget
            self.parent.open_dialog(
                DeleteViewWidget, modal=True, trash=False,
                table_p=self.parent.table_op, obj=self.report)
        self.refresh()

    def transfer(self, store, report_id):
        rep = Reports.get(id=report_id)
        if not self.check_befor(rep):
            return
        rep_ = Reports.get(id=report_id)
        rep_.store = store
        if not self.check_befor(rep_):
            return
        rep_.save()
        rep.recalculate()
        self.parent.refresh_()

    def click_item(self, row, column, *args):
        pass

    def check_befor(self, report):
        from data_helper import check_befor_update_data
        remaining, isok = check_befor_update_data(report)
        if isok:
            return True
        else:
            raise_error(
                "Erreur", "Impossible de déplacer ({}) {} du  {}/{} car"
                " le restant ({}) sera  < 0".format(
                    report.qty_use, report.type_, report.product.name,
                    report.store.name, remaining))
            return False
