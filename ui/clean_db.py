#!usr/bin/env python
# -*- coding: utf8 -*-
# maintainer: Fad
from __future__ import (
    unicode_literals, absolute_import, division, print_function)

# from PyQt4.QtCore import Qt

from PyQt4.QtGui import (QVBoxLayout, QGroupBox, QIcon,
                         QPushButton, QDialog, QComboBox,
                         QFormLayout)

from Common.ui.common import (FWidget, FormLabel, EnterTabbedLineEdit,
                              ErrorLabel, LineEdit, FPageTitle)
from Common.ui.util import check_is_empty, field_error
from Common.models import Owner
from configuration import Config


class DBCleanerWidget(QDialog, FWidget):

    def __init__(self, parent=0, *args, **kwargs):
        QDialog.__init__(self, parent=parent, *args, **kwargs)
        self.parent = parent

        self.setWindowTitle(u"Confirmation de le suppression")
        vbox = QVBoxLayout()

        self.loginUserGroupBox()
        vbox.addWidget(self.topLeftGroupBox)
        self.setLayout(vbox)

    def loginUserGroupBox(self):
        self.topLeftGroupBox = QGroupBox(
            self.tr("Suppression des enregistrements"))

        self.liste_username = Owner.select().where(Owner.isactive == True)
        # Combobox widget
        self.box_username = QComboBox()
        for index in self.liste_username:
            self.box_username.addItem(u'%(username)s' % {'username': index})

        # username field
        self.username_field = self.box_username
        # password field
        self.password_field = EnterTabbedLineEdit()
        self.password_field.setEchoMode(LineEdit.Password)
        self.password_field.setFocus()
        # login button
        self.login_button = QPushButton(u"&S'Supprimer")
        self.login_button.setIcon(QIcon.fromTheme(
            'delete', QIcon(u"{}login.png".format(Config.img_cmedia))))
        self.login_button.clicked.connect(self.login)

        self.cancel_button = QPushButton(u"&Quiter")
        self.cancel_button.clicked.connect(self.cancel)
        self.cancel_button.setFlat(True)

        # login error
        self.login_error = ErrorLabel("")

        formbox = QFormLayout()

        # grid layout
        formbox.addRow(FormLabel(u"Identifiant"), self.username_field)
        formbox.addRow(FormLabel(u"Mot de passe"), self.password_field)
        formbox.addRow(self.cancel_button, self.login_button)

        self.topLeftGroupBox.setLayout(formbox)

    def is_valide(self):
        if check_is_empty(self.password_field):
            return False
        return True

    def cancel(self):
        self.close()

    def login(self):
        """ """
        if not self.is_valide():
            print("is not valide")
            return

        username = str(self.liste_username[self.box_username.currentIndex()])
        password = Owner().crypt_password(
            str(self.password_field.text()).strip())
        # check completeness

        try:
            owner = Owner.get(
                Owner.username == username, Owner.password == password)
            owner.islog = True
            owner.save()
        except Exception as e:
            print(e)
            field_error(self.password_field, "Mot de passe incorrect")
            return False
        self.cleaner_db()

    def cleaner_db(self):
        for m in Reports:
            m.deletes_data()

        self.parent.Notify("Les rapport ont été bien supprimé", "error")
