#!usr/bin/env python
# -*- coding: utf-8 -*-
# maintainer: Fad

from PyQt4.QtGui import (QVBoxLayout, QHBoxLayout, QLabel,
                         QGridLayout)
from PyQt4.QtCore import QDate, Qt, QVariant, SIGNAL

from models import (Store, Product, Reports)
from Common.ui.common import (FWidget, IntLineEdit, Button_menu,
                              FormLabel, FormatDate)


class InfoTableWidget(FWidget):

    def __init__(self, parent, *args, **kwargs):
        super(FWidget, self).__init__(parent=parent, *args, **kwargs)

        self.parent = parent

        self.refresh()
        self.info_box = QLabel(" ")
        self.image = Button_menu("")
        self.image.clicked.connect(self.chow_image)

        hbox = QVBoxLayout()
        hbox.addWidget(self.info_box)
        hbox.addWidget(self.image)
        self.setLayout(hbox)

    def refresh_(self, idd):

        self.prod = Product.get(id=idd)
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
            color_style = color_style + \
                "; border:3px solid green; font-size: 15px"

            rest_by_store += """<li> {store}: <strong style='{color_style}'>
                {remaining} </strong> <i>carton</i> ({nbr_parts} <i>pièces</i>)
                </li>""".format(store=store.name, color_style=color_style,
                                remaining=remaining,
                                nbr_parts=nbr_parts * remaining)

        self.info_box.setText(u"""<h2>{name}</h2>
            <h4>Quantité restante:</h4>
            <ul>{remaining}
            <li><button type="submit"><img src="{image}"/></button></li></ul>
            """.format(name=self.prod.name,
                       remaining=rest_by_store, image=self.prod.image_link))
        self.image.setStyleSheet("")
        if self.prod.image_link:
            self.image.setStyleSheet("""background: url({image})
                no-repeat scroll 20px 10px #CCCCCC;
                width: 55px""".format(image=self.prod.image_link))

    def chow_image(self):
        """ doit afficher l'image complete dans une autre fenetre"""
        from GCommon.ui.show_image import ShowImageViewWidget
        try:
            self.parent.open_dialog(
                ShowImageViewWidget, modal=False, prod=self.prod)
        except AttributeError:
            pass
