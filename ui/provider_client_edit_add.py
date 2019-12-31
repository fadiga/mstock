#!/usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from __future__ import (
    unicode_literals, absolute_import, division, print_function)

from PyQt4.QtGui import (QVBoxLayout, QDialog,
                         QTextEdit, QFormLayout)

from Common.ui.util import check_is_empty, field_error

from Common.ui.common import (
    FWidget, ButtonSave, FormLabel, LineEdit, IntLineEdit)
import peewee
from models import ProviderOrClient


try:
    unicode
except:
    unicode = str


class EditOrAddClientOrProviderDialog(QDialog, FWidget):

    def __init__(self, table_p, parent, prov_clt=None, *args, **kwargs):
        FWidget.__init__(self, parent, *args, **kwargs)

        self.table_p = table_p
        self.prov_clt = prov_clt
        self.parent = parent
        if self.prov_clt:
            self.new = False
            self.title = u"Modification de {} {}".format(self.prov_clt.type_,
                                                         self.prov_clt.name)
            self.succes_msg = u"{} a été bien mise à jour".format(
                self.prov_clt.type_)
        else:
            self.new = True
            self.succes_msg = u"Client a été bien enregistré"
            self.title = u"Création d'un nouvel client"
            self.prov_clt = ProviderOrClient()
        self.setWindowTitle(self.title)

        vbox = QVBoxLayout()
        # vbox.addWidget(FPageTitle(u"Utilisateur: %s " %
        # self.prov_clt.name))

        self.name = LineEdit(self.prov_clt.name)
        self.phone_field = IntLineEdit(str(self.prov_clt.phone))
        # self.phone_field.setInputMask("D9.999.99.99.99.99")
        self.phone_field.setInputMask("+D99999999999999")
        self.legal_infos = LineEdit(self.prov_clt.legal_infos)
        self.address = QTextEdit(self.prov_clt.address)
        self.email = LineEdit(self.prov_clt.email)

        formbox = QFormLayout()
        formbox.addRow(FormLabel(u"Nom complete : *"), self.name)
        # formbox.addRow(FormLabel(u"Tel: *"), self.phone_field)
        formbox.addRow(FormLabel(u"E-mail :"), self.email)
        formbox.addRow(FormLabel(u"addresse complete :"), self.address)
        formbox.addRow(FormLabel(u"Info. legale :"), self.legal_infos)

        butt = ButtonSave(u"Enregistrer")
        butt.clicked.connect(self.save_edit)
        formbox.addRow("", butt)

        vbox.addLayout(formbox)
        self.setLayout(vbox)

    def save_edit(self):
        ''' add operation '''
        name = unicode(self.name.text())
        legal_infos = unicode(self.legal_infos.text())
        email = unicode(self.email.text())
        phone = unicode(self.phone_field.text())
        address = unicode(self.address.toPlainText())
        field_error
        if check_is_empty(self.name):
            return
        if phone == '...':
            field_error(self.phone_field, "Numéro téléphone manquant")
            return

        prov_clt = self.prov_clt
        prov_clt.phone = int(phone.replace(".", ""))
        prov_clt.name = name
        prov_clt.email = email
        prov_clt.legal_infos = legal_infos
        prov_clt.address = address
        try:
            prov_clt.save()
            self.close()
            self.table_p.refresh_()
            self.parent.Notify(u"Le Compte %s a été mise à jour" %
                               prov_clt.name, "success")
        except peewee.IntegrityError:
            field_error(
                self.phone_field, "Ce Numéro existe dans la basse de donnée.")
