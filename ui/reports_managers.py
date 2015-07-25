#!usr/bin/env python
# -*- coding: utf-8 -*-
#maintainer: Fadiga

from datetime import date
from PyQt4.QtCore import Qt, SIGNAL, SLOT, QDate
from PyQt4.QtGui import (QVBoxLayout, QGridLayout,QTableWidgetItem, QIcon, QMenu)

from configuration import Config
from models import Reports
from Common.ui.common import (FWidget, FPageTitle, FormatDate, Button,
                              BttExportXLS, FormLabel)
from Common.ui.table import FTableWidget
from Common.ui.util import (formatted_number, raise_error, date_on_or_end,
                            show_date)

from GCommon.ui.confirm_deletion import ConfirmDeletionDiag


class GReportViewWidget(FWidget):

    def __init__(self, parent=0, *args, **kwargs):
        super(GReportViewWidget, self).__init__(parent=parent,\
                                                        *args, **kwargs)
        self.parentWidget().setWindowTitle(Config.NAME_ORGA +
                                           u"    GESTION DES RAPPORTS")
        self.parent = parent
        self.title = u"Tous les mouvements"
        tablebox = QVBoxLayout()
        self.table_op = GReportTableWidget(parent=self)
        tablebox.addWidget(self.table_op)

        self.on_date = FormatDate(QDate(date.today().year, 1, 1))
        self.end_date = FormatDate(QDate.currentDate())
        self.Button = Button(_(u"OK"))
        self.Button.clicked.connect(self.report_filter)
        vbox = QVBoxLayout()
        # Grid
        gridbox = QGridLayout()
        gridbox.addWidget(FormLabel(_(u"debut")), 0, 2)
        gridbox.addWidget(self.on_date, 0, 3)
        gridbox.addWidget(FormLabel(_(u"Fin")), 0, 4)
        gridbox.addWidget(self.end_date, 0, 5)
        gridbox.addWidget(self.Button, 0, 6)
        gridbox.setColumnStretch(7, 5)

        period = " Du {} au {}".format(
                                    show_date(self.on_date.text(), time=False),
                                    show_date(self.end_date.text(), time=False))
        self.report_filter()

        vbox = QVBoxLayout()
        vbox.addWidget(FPageTitle(self.title))
        vbox.addWidget(FormLabel(period))
        vbox.addLayout(gridbox)
        vbox.addLayout(tablebox)
        self.setLayout(vbox)

    def report_filter(self):
        self.table_op.refresh_(on=date_on_or_end(self.on_date.text()),
                            end=date_on_or_end(self.end_date.text(), on=False))


class GReportTableWidget(FTableWidget):
    """ """

    def __init__(self, parent, *args, **kwargs):
        FTableWidget.__init__(self, parent=parent, *args, **kwargs)

        self.parent = parent

        self.hheaders = [u" ", u"Magasin", u"Produit", u"Quantité utilisé",
                         u"Restante", u"Date", u""]
        self.setContextMenuPolicy(Qt.CustomContextMenu)
        self.customContextMenuRequested.connect(self.popup)


        self.stretch_columns = [1, 2, 5]
        self.align_map = {0: 'l', 1: "l", 2: "l"}
        self.ecart = 144
        self.display_vheaders = False
        self.refresh_()

    def refresh_(self, on=None, end=None):
        """ """
        self._reset()
        self.set_data_for(on, end)
        self.refresh()
        #je cache la 7 eme colonne
        self.hideColumn(6)
        self.setColumnWidth(0, 40)

    def set_data_for(self, on, end):

        self.data = [(rap.type_, rap.store.name, rap.product,
                      formatted_number(rap.qty_use),
                      formatted_number(rap.remaining),
                      show_date(rap.date), rap.id)
                      for rap in Reports.filter(deleted=False, date__gte=on, date__lte=end)
                                        .order_by(Reports.date.desc())]

    def _item_for_data(self, row, column, data, context=None):
        if column == 0 and self.data[row][0] == Reports.E:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(img_media=Config.img_media,
                                                                     img="in.png")), u"")
        if column == 0 and self.data[row][0] == Reports.S:
            return QTableWidgetItem(QIcon(u"{img_media}{img}".format(img_media=Config.img_media,
                                                                     img="out.png")), u"")

        return super(GReportTableWidget, self)._item_for_data(row, column,
                                                              data, context)

    def popup(self, pos):
        row = self.selectionModel().selection().indexes()[0].row()
        if (len(self.data) - 1) < row:
            return False

        # self.report = Reports.filter(id=self.data[row][6]).get()
        self.report = Reports.select().where(Reports.id == self.data[row][6]).get()
        menu = QMenu()
        menu.addAction(QIcon("{}del.png".format(Config.img_cmedia)),
                       u"supprimer", lambda: self.del_report(self.report))

        self.action = menu.exec_(self.mapToGlobal(pos))

    def click_item(self, row, column, *args):
        pass

    def del_report(self, report):
        remaining, nb = report.store.get_remaining_and_nb_parts(report.product)
        remaining -= report.remaining
        if remaining >= 0:
            self.parent.open_dialog(ConfirmDeletionDiag, modal=True,
                                    obj_delete=report,
                                    msg="Magasin : {}\nProduit: {}\nQuantité: {}".format(report.store,
                                                              report.product,
                                                              report.qty_use),
                                    table_p=self.parent.table_op)
            rep = Reports.select().where(Reports.date <
                             report.date).order_by(Reports.date.desc()).get()
            rep.save()
        else:
            raise_error(u"Erreur", u"Impossible de supprimer ce rapport car"
                        u" le restant sera : <b>%s</b> qui est < 0"
                        % remaining)
